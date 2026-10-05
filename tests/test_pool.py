import ast
import hashlib
import json
from pathlib import Path
import pytest

BODY = b"Retain copyright and permission notices. Do not use contributor names for endorsement."
HASH = hashlib.sha256(BODY).hexdigest()


def address(account):
    return "0x" + account.hex()


def setup(vm, factory, account, vector=None, status=200, body=BODY):
    c = factory("contracts/LicenseObligationPool.py")
    vm.sender = account
    mocks(vm, vector, status, body)
    return c


def mocks(vm, vector=None, status=200, body=BODY):
    vm.clear_mocks()
    vm.mock_web(r".*raw\.githubusercontent\.com/spdx/license-list-data/.*", {"status": status, "body": body})
    vm.mock_llm(r"(?s).*Derive a four-field obligation checklist.*", json.dumps({"obligations": vector or ["YES", "YES", "NO", "YES"]}))


def test_consensus_output_drives_counters(direct_vm, direct_deploy, direct_alice):
    c = setup(direct_vm, direct_deploy, direct_alice)
    c.add("bundle", "one", "MIT", HASH)
    pool = c.get_pool(address(direct_alice), "bundle")
    assert pool["counts"] == [1, 1, 0, 1] and pool["coverage"] == "COMPLETE"
    mocks(direct_vm, ["NO", "NO", "YES", "NO"])
    c.add("bundle", "two", "Apache-2.0", HASH)
    assert c.get_pool(address(direct_alice), "bundle")["counts"] == [1, 1, 1, 1]


def test_removal_preserves_shared_obligations(direct_vm, direct_deploy, direct_alice):
    c = setup(direct_vm, direct_deploy, direct_alice)
    c.add("bundle", "one", "MIT", HASH)
    c.add("bundle", "two", "BSD-3-Clause", HASH)
    before = c.get_entry(address(direct_alice), "bundle", "one")["report"]
    c.remove("bundle", "one")
    pool = c.get_pool(address(direct_alice), "bundle")
    assert pool["counts"] == [1, 1, 0, 1] and pool["active"] == 1
    assert not c.get_entry(address(direct_alice), "bundle", "one")["active"]
    assert c.get_entry(address(direct_alice), "bundle", "one")["report"] == before
    c.remove("bundle", "two")
    assert c.get_pool(address(direct_alice), "bundle")["coverage"] == "EMPTY"


def test_unknown_is_not_zero_obligations(direct_vm, direct_deploy, direct_alice):
    c = setup(direct_vm, direct_deploy, direct_alice)
    c.add("bundle", "ok", "MIT", HASH)
    mocks(direct_vm, ["YES", "UNKNOWN", "NO", "NO"])
    c.add("bundle", "uncertain", "MIT", HASH)
    pool = c.get_pool(address(direct_alice), "bundle")
    assert pool["coverage"] == "PARTIAL" and pool["unresolved"] == 1
    assert pool["counts"] == [1, 1, 0, 1]
    c.remove("bundle", "uncertain")
    assert c.get_pool(address(direct_alice), "bundle")["coverage"] == "COMPLETE"


@pytest.mark.parametrize("vector", [[True, "YES", "NO", "NO"], ["YES"], ["MAYBE"] * 4])
def test_malformed_model_does_not_commit(vector, direct_vm, direct_deploy, direct_alice):
    c = setup(direct_vm, direct_deploy, direct_alice, vector)
    with direct_vm.expect_revert("malformed obligation vector"):
        c.add("bundle", "bad", "MIT", HASH)
    assert c.get_pool(address(direct_alice), "bundle")["active"] == 0


@pytest.mark.parametrize("status,hash_value", [(404, HASH), (200, "f" * 64)])
def test_unavailable_or_false_commitment(status, hash_value, direct_vm, direct_deploy, direct_alice):
    c = setup(direct_vm, direct_deploy, direct_alice, status=status)
    c.add("bundle", "bad", "MIT", hash_value)
    pool = c.get_pool(address(direct_alice), "bundle")
    assert pool["coverage"] == "PARTIAL" and pool["counts"] == [0, 0, 0, 0]
    assert c.get_entry(address(direct_alice), "bundle", "bad")["report"]["reason"] == "SOURCE"


def test_namespaces_prevent_unauthorized_removal(direct_vm, direct_deploy, direct_alice, direct_bob):
    c = setup(direct_vm, direct_deploy, direct_alice)
    c.add("same", "one", "MIT", HASH)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("unknown slot in caller pool"):
        c.remove("same", "one")
    c.add("same", "one", "MIT", HASH)
    c.remove("same", "one")
    assert c.get_pool(address(direct_alice), "same")["active"] == 1
    assert c.get_pool(address(direct_bob), "same")["active"] == 0


def test_replay_and_cross_pool_resolution(direct_vm, direct_deploy, direct_alice):
    c = setup(direct_vm, direct_deploy, direct_alice)
    c.add("a", "one", "MIT", HASH)
    with direct_vm.expect_revert("unknown slot in caller pool"):
        c.remove("b", "one")
    with direct_vm.expect_revert("reused slot"):
        c.add("a", "one", "MIT", HASH)
    c.remove("a", "one")
    with direct_vm.expect_revert("already removed"):
        c.remove("a", "one")
    with direct_vm.expect_revert("reused slot"):
        c.add("a", "one", "MIT", HASH)


def test_immutable_root_bound_history(direct_vm, direct_deploy, direct_alice):
    c = setup(direct_vm, direct_deploy, direct_alice)
    c.add("a", "one", "MIT", HASH)
    c.remove("a", "one")
    events = c.history(address(direct_alice), "a", 0, 20)
    assert [e["action"] for e in events] == ["ADD", "REMOVE"]
    assert events[1]["previous"] == events[0]["root"]
    for event in events:
        unrooted = {k: v for k, v in event.items() if k != "root"}
        assert hashlib.sha256(json.dumps(unrooted, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest() == event["root"]
    with direct_vm.expect_revert("pagination"):
        c.history(address(direct_alice), "a", 0, 21)


def test_bounds_and_publisher_allowlist(direct_vm, direct_deploy, direct_alice):
    c = setup(direct_vm, direct_deploy, direct_alice)
    with direct_vm.expect_revert("unsupported license"):
        c.add("a", "bad", "../../attacker", HASH)
    with direct_vm.expect_revert("invalid pool identity"):
        c.add("a/b", "bad", "MIT", HASH)
    for i in range(32):
        c.add("full", str(i), "MIT", HASH)
    with direct_vm.expect_revert("active entry limit"):
        c.add("full", "overflow", "MIT", HASH)


def test_exact_reports_reject_opposite_decisions_and_boolean_alias():
    tree = ast.parse(Path("contracts/LicenseObligationPool.py").read_text())
    helpers = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("canonical", "reports_match")]
    scope = {"json": json}
    exec(compile(ast.Module(body=helpers, type_ignores=[]), "helpers", "exec"), scope)
    assert not scope["reports_match"]({"vector": ["YES"]}, {"vector": ["NO"]})
    assert not scope["reports_match"]({"http": True}, {"http": 1})
