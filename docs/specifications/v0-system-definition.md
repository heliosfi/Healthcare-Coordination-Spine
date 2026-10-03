# Healthcare Coordination Spine — v0 System Definition

Readable transcription of the [uploaded v0 source](../../archive/source-artifacts/v0-system-definition.html). The source is preserved unchanged. Later data-model and contract details are specified separately.

## 1. Purpose

Freeze the concept before code. Make the product do one thing clearly before APIs, vendors, HIPAA implementation, or UI spread the scope.

## 2. Boundaries locked for v0

| Dimension | Definition |
|---|---|
| Primary problem | Patients, doctors, pharmacies, and insurers can each hold valid information while still being out of sync about the current care state. |
| First use case | Prescription coordination. |
| Core question | Where is the prescription, what is blocking it, and who is responsible for the next action? |
| System role | Coordinate authoritative information; do not replace the EHR, pharmacy system, insurer, or clinician. |

**Governance:** access does not create authority.

**Safety:** the system may explain or route information, but does not independently diagnose, prescribe, discontinue medication, or reinterpret a clinician's order.

**Evidence:** every consequential state identifies its source, timestamp, responsible organization, and whether it is verified, disputed, pending, or unknown.

## 3. First state model

| Segment | Progression |
|---|---|
| Intake | `PRESCRIBED` → `PRESCRIPTION_RECEIVED` → `COVERAGE_CHECK` |
| No PA | `PA_NOT_REQUIRED` → `PHARMACY_PROCESSING` |
| PA required | `PA_REQUIRED` → `PA_SUBMITTED` → `PAYER_REVIEW` |
| Information loop | `PAYER_REVIEW` → `NEEDS_INFORMATION` → `PROVIDER_ACTION` → `PAYER_REVIEW` |
| Decision | `APPROVED` continues; `DENIED` has a review path to be defined. |
| Fulfillment | `PHARMACY_PROCESSING` → `READY` → `DISPENSED` |
| Receipt and follow-up | `PATIENT_RECEIPT_KNOWN?` → `FOLLOW-UP` in the original visual |

The v0.1 model normalizes `FOLLOW_UP` and adds successful `CLOSED`; those are later extensions, not changes to this source record.

## 4. Minimum viable coordination object

The object carries separate state, source, responsibility, action, time, and confidence fields rather than only a status string.

| Field | Illustrative value |
|---|---|
| STATUS | `NEEDS_INFORMATION` |
| SOURCE | Health Plan X |
| RESPONSIBLE_ACTOR | Prescribing provider |
| NEXT_REQUIRED_ACTION | Submit requested supporting documentation |
| PATIENT_ACTION | None |
| LAST_UPDATED | 2026-10-03 08:42 EDT |
| CONFIDENCE | Source-confirmed |

## 5. Authority matrix

| Actor | Can originate | Can update | Can view as needed |
|---|---|---|---|
| Patient | Consent, preferences, patient-reported information | Own inputs | Permitted care/coverage state |
| Doctor | Orders, diagnosis, clinical documentation | Clinical objects they control | Relevant patient/coverage/pharmacy status |
| Pharmacy | Dispense/fulfillment state | Pharmacy-controlled events | Prescription and required coverage information |
| Insurer | Coverage, PA, claim state | Payer-controlled decisions | Information needed for covered workflow |
| Coordination Spine | Workflow state, provenance, alerts | Coordination metadata | Referenced source data only as authorized |

The Spine must not overwrite the authoritative source because systems disagree.

## 6. Conflict is a state

Disagreement is a coordination state to manage: `CONFLICT_DETECTED` → `HOLD` → `SOURCE_RECONCILIATION` → `VERIFIED_STATE`.

The v0.1 contract clarifies that this blocks promotion inside the Spine rather than publication in an upstream system.

## 7. Architectural order after freeze

1. Data model.
2. Authority/consent contract.
3. Event/state machine.
4. Audit/provenance contract.
5. UI.
6. Integration adapters.

## 8. Core v0 exclusions

FHIR, TEFCA, payer APIs, and NCPDP belong outside the core as adapters, keeping coordination logic independent of a single transport standard.

One bounded workflow, four authority domains, one coordination state, and no invented medical authority.
