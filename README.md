# Healthcare Coordination Spine

Prescription coordination across patient, prescriber, pharmacy, and payer systems: **Where is the prescription, what is blocking it, and who is responsible for the next action?**

**Responsibility moves. Authority does not.** Access does not create authority. The Spine references source facts, preserves provenance, and blocks promotion of conflicting claims into verified coordination state until reconciliation.

## Current status

Documentation baseline recorded on 2026-10-03 under **Nicholas B. Carty (N.B.C.) authority**. The v0.1 data model incorporates the subsequently authorized successful-closure criteria. The authority and transition contracts are design specifications. The Audit & Provenance Contract is now included as an imported draft, with discrepancies tracked before ratification. A [local Python reference scaffold](reference/README.md) now supplies fail-closed stubs, a draft SQL schema, synthetic fixtures, and boundary tests. Full enforcement, deployed services, clinical validation, vendor connections, and compliance certification remain unestablished.

## Read in order

| Order | Artifact | Status |
|---|---|---|
| 1 | [v0 System Definition](docs/specifications/v0-system-definition.md) | Bounded concept baseline |
| 2 | [v0.1 Data Model](docs/specifications/v0.1-data-model.md) | Frozen documentation baseline with closure completion |
| 3 | [v0.1 Authority & Consent Contract](docs/specifications/v0.1-authority-consent-contract.md) | Design contract |
| 4 | [v0.1 State-Transition Contract](docs/specifications/v0.1-state-transition-contract.md) | Design contract |
| 5 | [v0.1 Audit & Provenance Contract](docs/specifications/v0.1-audit-provenance-contract.md) | Imported draft; reconciliation pending |
| 6 | [Worked prescription scenario](docs/examples/prescription-coordination.md) | Synthetic conflict and happy-path walkthrough |
| 7 | [Provenance, clarifications, and remaining work](docs/specification-status.md) | Source inventory and implementation boundary |
| 8 | [Python reference scaffold](reference/README.md) | Local fail-closed stubs; draft SQL; synthetic fixtures |

The [original v0 HTML](archive/source-artifacts/v0-system-definition.html), [original v0.1 data-model HTML](archive/source-artifacts/v0.1-data-model.html), and [original Audit & Provenance draft HTML](archive/source-artifacts/v0.1-audit-provenance-contract.html) are preserved unchanged. The Markdown specifications distinguish later conversation-authorized completion from the uploaded source. Examples and future timestamps are illustrative, not patient records or execution evidence.

## Governing boundaries

- The prescriber originates clinical orders, the payer originates coverage decisions, the pharmacy originates fulfillment facts, and the patient originates bounded patient reports.
- Transport services carry claims; their brand or technical access does not establish source authority.
- Authorization, transition validity, and verified-state promotion are separate decisions.
- Conflict creates a hold on Spine promotion. It does not control upstream publication or independently stop external dispensing.
- `DISPENSED` does not establish patient receipt, ingestion, adherence, or clinical effectiveness.
- `CLOSED` means successful coordination completion only, with attributable evidence and no outstanding required action.

## Next bounded artifact

Reconcile the imported **Audit & Provenance draft** with the preceding contracts before ratification. The local reference scaffold keeps unresolved policy/evaluation paths on HOLD; replacing those stubs requires reviewed adapter, policy, and persistence contracts. Event identity, ordering, retention/access rules, and implementation prerequisites are tracked in [specification status](docs/specification-status.md#audit--provenance-draft-import-2026-10-03).

Conceptual framework and authority: Nicholas B. Carty (N.B.C.). Assistant-assisted documentation is identified in the provenance record. Rights: [© HeliosFi LLC. All Rights Reserved.](COPYRIGHT.md)
