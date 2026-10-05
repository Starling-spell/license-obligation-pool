# Security model

- Identity: sender-owned namespaces; no cross-account or cross-pool removal.
- Replay: every slot ID is permanently spent on addition, even if later removed.
- Evidence: fixed corpus revision, constructed HTTPS paths, full-response commitments, bounded complete text.
- Consensus: each validator independently observes and derives all four labels; exact canonical report comparison rejects opposite decisions and bool/int aliasing.
- Accounting: resolved contributions add/subtract reference counts; unresolved entries block complete coverage; removal cannot underflow or run twice.
- History: reports are immutable; append-only events bind caller pool, contract, contribution root, resulting counts and previous journal root.
- No funds: no token custody, settlement, external write dispatch or wallet transfers.
- Liveness: principal can remove unresolved entries without a new nondeterministic call. Publishing outages/disagreement may prevent additions.

Known limitations: selected templates are not verified package licenses; optional exceptions and obligations outside the four features are not analyzed. Removing a document only removes it from this review pool and does not discharge real-world obligations. Complete coverage is not legal approval. Publisher compromise, coordinated/model-common semantic errors, and caller omission of relevant licenses remain risks. This is a pinned historical corpus, not a live license-change monitor. No upgrade/admin repair exists; a changed policy needs a new deployment.

Report issues through the repository's issue tracker. Do not publish credentials or private keys.
