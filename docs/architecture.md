# LicenseObligationPool boundary

The user selects a license identifier and exact publisher-byte commitment, not license text, labels, scores, package provenance, or compliance claims. The contract constructs a URL in the SPDX license-list-data corpus at a pinned revision. Leader and validators independently fetch the complete document and derive the same four obligation classifications. The entire evidence report must match exactly.

The consensus output changes a reversible multiset: active entries contribute reference counts to each obligation. Removing one entry subtracts only its stored contribution; an obligation remains present while any other entry contributes it. Unresolved entries contribute an unresolved counter, never an all-clear. An empty pool also has no complete checklist. Immutable addition/removal events retain the evidence and old contributions.

This is neither an owner-editable graph nor an approval certificate. Storage consists of per-account pools, active slot contributions, four reference counts, unresolved counts and append-only events. It has no dependency edges, proposal competition, certificate issuance, execution gate, settlement, or one-time consumption. AI-derived obligations, not deterministic graph validity, drive aggregation.

Frontend owns selection of documents and artifact-to-license attribution. The contract does NOT verify that a package really uses a selected license. Source publisher owns the license template. Contract owns source acquisition, complete-byte binding, semantic interpretation, accounting and query provenance. The result is a bounded review checklist, not legal advice, exhaustive obligations, permission to distribute, or a finding of license compatibility.
