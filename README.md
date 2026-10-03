# Healthcare Coordination Spine

Prescription coordination across patient, prescriber, pharmacy, and payer systems: **Where is the prescription, what is blocking it, and who is responsible for the next action?**

**Responsibility moves. Authority does not.** Access does not create authority. The Spine references source facts, preserves provenance, and blocks promotion of conflicting claims into verified coordination state until reconciliation.

## Current status

Documentation baseline recorded on 2026-10-03 under **Nicholas B. Carty (N.B.C.) authority**. The v0.1 data model incorporates the subsequently authorized successful-closure criteria. The authority and transition contracts are design specifications. There is no reference implementation, deployed service, clinical validation, vendor connection, or compliance certification in this repository.

## Read in order

| Order | Artifact | Status |
|---|---|---|
| 1 | [v0 System Definition](docs/specifications/v0-system-definition.md) | Bounded concept baseline |
| 2 | [v0.1 Data Model](docs/specifications/v0.1-data-model.md) | Frozen documentation baseline with closure completion |
| 3 | [v0.1 Authority & Consent Contract](docs/specifications/v0.1-authority-consent-contract.md) | Design contract |
| 4 | [v0.1 State-Transition Contract](docs/specifications/v0.1-state-transition-contract.md) | Design contract |
| 5 | [Worked prescription scenario](docs/examples/prescription-coordination.md) | Synthetic conflict and happy-path walkthrough |
| 6 | [Provenance, clarifications, and remaining work](docs/specification-status.md) | Source inventory and implementation boundary |

The [original v0 HTML](archive/source-artifacts/v0-system-definition.html) and [original v0.1 HTML](archive/source-artifacts/v0.1-data-model.html) are preserved unchanged. The Markdown specifications distinguish later conversation-authorized completion from the uploaded source. Examples and future timestamps are illustrative, not patient records or execution evidence.

## Governing boundaries

- The prescriber originates clinical orders, the payer originates coverage decisions, the pharmacy originates fulfillment facts, and the patient originates bounded patient reports.
- Transport services carry claims; their brand or technical access does not establish source authority.
- Authorization, transition validity, and verified-state promotion are separate decisions.
- Conflict creates a hold on Spine promotion. It does not control upstream publication or independently stop external dispensing.
- `DISPENSED` does not establish patient receipt, ingestion, adherence, or clinical effectiveness.
- `CLOSED` means successful coordination completion only, with attributable evidence and no outstanding required action.

## Next bounded artifact

The **Audit & Provenance Contract** remains to be specified, followed by adapter contracts and a reference implementation. Event identity, ordering, retention/access rules, and implementation prerequisites are tracked in [specification status](docs/specification-status.md).

Conceptual framework and authority: Nicholas B. Carty (N.B.C.). Assistant-assisted documentation is identified in the provenance record. Rights: [© HeliosFi LLC. All Rights Reserved.](COPYRIGHT.md)
