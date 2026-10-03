# Worked example — prescription coordination

Synthetic design walkthrough derived from the supplied conversation. Atorvastatin 20mg, Health Plan X, the illustrative pharmacy, timestamps, and source labels are scenario fixtures. This is not a real clinical record, executed integration, medical recommendation, or comparison establishing other vendors' capabilities.

## Conflict path

| Step | Source event / assertion | Authority interpretation | Coordination effect |
|---|---|---|---|
| 1 | Prescription created in Epic; Surescripts RTPB reports PA required | Prescriber owns prescription; coverage signal needs attributable payer authority | PA_REQUIRED if applicable guards pass; prescriber owns PA submission |
| 2 | CoverMyMeds reports provider PA submission | Submission system preserves authenticated prescriber origin and confirmation | PA_SUBMITTED; payer owns review; prior coverage evidence remains |
| 3 | Health Plan X acknowledges review and requests more information | Payer controls PA outcome and requested supporting information | NEEDS_INFORMATION; prescriber owns supporting documentation; patient action None |
| 4 | Network automation reports APPROVED while payer evidence still says NEEDS_INFORMATION | Transport/automation label alone does not establish an authoritative payer decision | Preserve both claims; create HOLD; block approval promotion |
| 5 | Reconciliation confirms payer NEEDS_INFORMATION applies to the same current PA instance; competing claim lacks an established superseding authority basis | Payer evidence governs this disputed fact; no universal vendor ranking is inferred | Last verified state remains NEEDS_INFORMATION; non-governing claim stays in provenance |

A PA-required coverage result alone does not establish that the payer requested labs. In this fixture, the explicit information request at step 3 creates that obligation. If it asks for a lipid panel, the prescriber's bounded next task is to submit the requested supporting material; the Spine does not diagnose, order testing, or infer the request from PA_REQUIRED.

At step 4, upstream systems may continue publishing their own status. The Spine qualifies its own views and cannot independently control dispensing. No disputed approval becomes its verified READY state, and no verified pickup instruction follows from that claim.

Step 5 does **not** produce APPROVED. Approval requires a new attributable payer decision. If the two claims actually concern different versions, effective periods, or PA instances, reconciliation must establish that distinction rather than force a conflict or choose a winner by arrival time.

## Resume and successful path

After the prescriber submits required information and the payer acknowledges resumed review, a new payer approval can be evaluated. Each row assumes applicable authority/consent, evidence, sequencing, and conflict guards pass.

| Source-backed event | Verified state | Responsible actor | Patient action / boundary |
|---|---|---|---|
| Provider supporting information submitted | PROVIDER_ACTION | PAYER | None; submission is not approval |
| Payer resumes review | PAYER_REVIEW | PAYER | None |
| Payer decision approves | APPROVED | PHARMACY | None; approval is not dispensing |
| Pharmacy begins processing | PHARMACY_PROCESSING | PHARMACY | None |
| Pharmacy confirms readiness | READY | PATIENT | Pick up at selected pharmacy; only if supported by the readiness event |
| Pharmacy confirms dispensing | DISPENSED | PATIENT, if receipt confirmation required | Confirm receipt; dispensing does not prove patient possession |
| Patient confirms receipt | PATIENT_RECEIPT_KNOWN | PRESCRIBER, when follow-up required | None; confidence remains patient-reported |
| Workflow-defined follow-up begins | FOLLOW_UP | PRESCRIBER | Follow the attributable coordination plan; no inferred adherence/effectiveness |
| Required follow-up completed and closure predicates satisfied | CLOSED | null | None; no outstanding required action |

The provenance sequence preserves each source event and the reconciliation decision separately. A reconciliation recorded before a later approval remains a reconciliation of the earlier conflict; it must not be retrospectively described as proof of that later approval.

An illustrative append-only sequence is:

1. Prescriber prescription event.
2. Coverage inquiry and payer-attributed PA requirement.
3. Prescriber PA submission.
4. Payer review acknowledgement and NEEDS_INFORMATION decision.
5. Conflicting automation claim, conflict record, and held promotion decision.
6. Reconciliation evidence confirming the governing NEEDS_INFORMATION claim.
7. Provider supporting information event.
8. Payer resumed review and new APPROVED decision.
9. Pharmacy processing, READY, and DISPENSED events.
10. Patient-reported receipt event.
11. Follow-up start and completion evidence.
12. Spine closure attestation referencing required evidence.

## No-PA branch

Payer-authoritative PA_NOT_REQUIRED evidence permits evaluating pharmacy processing without fabricating PA_SUBMITTED, PAYER_REVIEW, or APPROVED. Closure uses that branch's required coverage evidence. The remaining fulfillment, optional receipt obligations, follow-up, and closure guards still apply.

## Expected design outcomes

| Case | Required behavior |
|---|---|
| Unknown required consent | Authorization HOLD; no disclosure or state promotion |
| Pharmacy asserts payer approval | Reject promotion for invalid source authority |
| Patient requests dose rewrite | Deny source-domain mutation; no prescription rewrite |
| Compatible payer approval with unresolved conflict | HOLD; do not promote APPROVED |
| Proven duplicate event | REJECT second promotion, DUPLICATE_EVENT, no state change |
| Late proven historical NEEDS_INFORMATION | Preserve provenance; reject current promotion as stale |
| Late contradictory claim with unresolved ordering | HOLD pending evidence/reconciliation |
| DISPENSED without receipt evidence | Do not infer PATIENT_RECEIPT_KNOWN |
| Follow-up merely scheduled | Do not infer follow-up completion or CLOSED |
| Closure with outstanding action or active hold | HOLD; do not promote CLOSED |
| Payer DENIED | Preserve denial; do not relabel successful CLOSED |

These are expected contract outcomes, not executed tests. Runtime verification remains pending.
