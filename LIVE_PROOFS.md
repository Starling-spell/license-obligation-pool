# StudioNet proof matrix

Verified October 5, 2026. These are actual transactions with execution checks, not planned proofs. Deployment is experimental, unaudited and gasless; no assets were transferred.

Contract: [0xAE60dc124B1C219577b92c0A91c02F74bfeFBae2](https://explorer-studio.genlayer.com/address/0xAE60dc124B1C219577b92c0A91c02F74bfeFBae2).

The deployed source matches `contracts/LicenseObligationPool.py` after LF normalization and trailing-newline normalization. Source SHA-256: `a560a7b1a60f3607419051a9cb43dbd2359964fa738071507f56963832cd68cd`.

Principal: `0x7a413BB4AB62E31d62d4cD9efC8C8a8Dae37FB42`; pool: `demo`. Counter order: COPYRIGHT_NOTICE, LICENSE_TEXT, CHANGE_NOTICE, NONENDORSEMENT.

| Scenario | Transaction | Verified execution and result |
|---|---|---|
| Deployment | [bbcb84…3f038](https://explorer-studio.genlayer.com/tx/0xbbcb84888a778b0b2d3226cbad6687c4577948ac3adf08f10cc058180773f038) | FINALIZED / SUCCESS |
| Real MIT observation | [6f3b72…22102](https://explorer-studio.genlayer.com/tx/0x6f3b7216aa315f229baf60c626cdb90c0ac3c1f4f6f810379da8e19291122102) | RESOLVED vector YES, YES, NO, NO |
| Real BSD-3-Clause observation | [42a246…4f51c](https://explorer-studio.genlayer.com/tx/0x42a2462e261215d03f2623940bfbe97bb8fb54ee1a766e871701ff9a1004f51c) | RESOLVED vector YES, YES, NO, YES; counts [2,2,0,1] |
| Cross-pool removal attempt | [84a55e…143f2](https://explorer-studio.genlayer.com/tx/0x84a55e8d27a747d60c5354d95a19186efeb7c59c4024b06c5632de84aa7143f2) | FINALIZED / expected ERROR: unknown slot in caller pool; no mutation |
| Remove BSD contribution | [647f41…15050](https://explorer-studio.genlayer.com/tx/0x647f4111ade8c41a71405876f4fa72cf8a6dad9acb4a55b5ecf1f57691615050) | SUCCESS; counts [1,1,0,0], MIT obligations retained, BSD report unchanged |
| False hash commitment | [f0d5a2…32583](https://explorer-studio.genlayer.com/tx/0xf0d5a2b01777aa46be507aef49d7a3a4fd042b3133c69782c390f2531ec32583) | SUCCESS; entry UNRESOLVED/SOURCE, hash_match false, coverage PARTIAL, known counts unchanged |
| Remove unresolved entry | [f53e35…afe82](https://explorer-studio.genlayer.com/tx/0xf53e355517a1954fc020475a9eaa0a82bec11ee5322bde00e12c169ef17afe82) | SUCCESS; unresolved count zero, coverage COMPLETE, evidence retained |
| Reuse removed BSD slot | [506f63…08636](https://explorer-studio.genlayer.com/tx/0x506f6374ca89aba897149f3b51b68c7271580546555138d16309f07d98208636) | FINALIZED / expected ERROR: invalid or reused slot; no history reset |

Receipts report MAJORITY_AGREE, not unanimity. Some validators stopped after quorum; their idle/error receipts are not independent execution successes. The two adversarial rows are rejected transactions, not successful additions/removals. The CLI's generic success banner is NOT used as proof of contract execution.

## Source acquisition

Every observer constructs the source URL and fetches complete publisher bytes independently. The demonstration uses actual SPDX templates, not synthetic repository fixtures or caller-supplied summaries.

| Source | Complete bytes | Full-response SHA-256 |
|---|---:|---|
| [MIT](https://raw.githubusercontent.com/spdx/license-list-data/31ba1a50e5397e00a304dbadc76531740e89ee48/text/MIT.txt) | 1,078 | `b05785f9f18e6716bab63424b11454513b9943a222595b70411009202fc592b5` |
| [BSD-3-Clause](https://raw.githubusercontent.com/spdx/license-list-data/31ba1a50e5397e00a304dbadc76531740e89ee48/text/BSD-3-Clause.txt) | 1,460 | `5a93d5831e1297ab10fe643e1a631e83be392896da14ee2951285a79012df69d` |

The false commitment was 64 `f` characters. Its independent fetch still returned the actual MIT hash; no semantic contribution was accepted from that mismatched source.

## Immutable evidence roots

- MIT: `aceb68af4ec7cfdb93c4fce4242da11ecc77b44c845d645cbc2d693f62e76ec0`
- BSD: `669e8a77b1abed123605fcbfa9de5660dc9ed8f74d52da6d40e18998aad34c13`
- False-hash entry: `f6055e8006715a06ec2e23d3781204578e0189edd49887788c9c648ea3bac905`

## State assertions

The SDK reader asserted actual deployed state, not mocked outputs:

| Readback point | Active | Counts | Unresolved | Coverage | Accepted history events |
|---|---:|---|---:|---|---:|
| Both valid sources | 2 | [2,2,0,1] | 0 | COMPLETE | 2 |
| BSD removed | 1 | [1,1,0,0] | 0 | COMPLETE | 3 |
| False commitment added | 2 | [1,1,0,0] | 1 | PARTIAL | 4 |
| Recovery completed | 1 | [1,1,0,0] | 0 | COMPLETE | 5 |

Final journal root: `30efbf8cf43bf86a4be69c26cf843f22047ddc8001528ebdd74782434a8ffb3c`. Removed entries retain their original vectors, source hashes and report roots. The final reader returned `assertions: PASSED`.

## Reproduce checks

Run from the repository root; install the locked SDK with `npm ci --ignore-scripts`.

```powershell
node scripts/studio_check.mjs --source 0xAE60dc124B1C219577b92c0A91c02F74bfeFBae2
node scripts/studio_check.mjs --success 0x6f3b7216aa315f229baf60c626cdb90c0ac3c1f4f6f810379da8e19291122102
node scripts/studio_check.mjs --error 0x84a55e8d27a747d60c5354d95a19186efeb7c59c4024b06c5632de84aa7143f2 'unknown slot in caller pool'
node scripts/studio_check.mjs --error 0x506f6374ca89aba897149f3b51b68c7271580546555138d16309f07d98208636 'invalid or reused slot'
$env:LICENSE_POOL_EXPECTED='{"active":1,"counts":[1,1,0,0],"unresolved":0,"coverage":"COMPLETE","events":5}'
node scripts/read_pool.mjs 0xAE60dc124B1C219577b92c0A91c02F74bfeFBae2 0x7a413BB4AB62E31d62d4cD9efC8C8a8Dae37FB42 demo mit bsd wrong
```

## Validation scope

GenVM lint and SDK validation passed. All **13 direct tests** passed. Direct mode runs the leader only and uses mocked web/model results; its exact-report comparison helper test is not a network disagreement simulation. The live calls above exercise real GenVM, external acquisition and semantic validator consensus. UNKNOWN labels, malformed model output, unavailable sources, cross-account isolation, entry-limit boundaries and pagination are direct-test scenarios, not additional onchain proofs. npm installation reported zero known dependency vulnerabilities at verification time.

COMPLETE only describes the four-feature checklist for selected templates. No proof establishes package license attribution, exhaustive compliance, legal compatibility or an authorization to distribute. Historical source commitments do not establish current-world freshness.
