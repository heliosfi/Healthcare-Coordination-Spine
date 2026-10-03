# Specification provenance and current status

## Authority and scope

On 2026-10-03, Nicholas B. Carty (N.B.C.) directed that the supplied Healthcare Coordination Spine material be placed in `heliosfi/Healthcare-Coordination-Spine`. Earlier explicit “N.B.C authority continue” authorized successful-only closure completion, carrying forward the v0.1 data-model baseline, and proceeding through the Authority & Consent and State-Transition contracts.

This repository import is documentation-only. Specification language such as MUST, “frozen,” “implements,” and “executable” describes intended design obligations, not executed code or validation. No paper/live authority, clinical authority, vendor account, outreach, or broader project disposition is created by this import.

## Source inventory

| Source | Repository location | Treatment |
|---|---|---|
| Uploaded Healthcare Coordination Spine — v0 System Definition.html | [Original HTML](../archive/source-artifacts/v0-system-definition.html) | Byte-preserved; readable transcription in specifications |
| Uploaded Healthcare Coordination Spine — v0.1 Data Model.html | [Original HTML](../archive/source-artifacts/v0.1-data-model.html) | Byte-preserved; readable specification adds subsequently authorized closure completion |
| Supplied conversation: closure criteria and authorization to continue | [Data-model closure section](specifications/v0.1-data-model.md#7-authorized-closure-completion) | Explicit completion; not misrepresented as already present in uploaded HTML |
| Supplied conversation: Authority & Consent Contract, sections 1–15 | [Authority contract](specifications/v0.1-authority-consent-contract.md) | Repository transcription with listed clarifications |
| Supplied conversation: State-Transition Contract, sections 1–22 | [Transition contract](specifications/v0.1-state-transition-contract.md) | Repository transcription with listed consistency corrections |
| Supplied conflict and successful-path scenarios | [Worked example](examples/prescription-coordination.md) | Synthetic; not runtime or clinical evidence |
| Screenshot IMG_8833.png | Used to identify owner and target repository | Repository screenshot is contextual, not an architecture source; not included as a specification |

The original v0 data-model file was not attached in this turn. It is not reconstructed or represented as preserved. The supplied v0 system definition and v0.1 data model are the actual archived files.

Conceptual framework and authority attribution belong to Nicholas B. Carty (N.B.C.). The supplied conversation and repository preparation include assistant-assisted drafting and technical wording. Repository-editor clarifications below are recorded separately from the user's original artifacts. The import date is not a claim that the concept first originated on that date.

Source SHA-256 checksums are in [SHA256SUMS](../archive/source-artifacts/SHA256SUMS). They verify preservation of the uploaded files; they are not an implemented event integrity chain.

## Documented completions and corrections

| Issue in supplied material | Repository treatment |
|---|---|
| Uploaded CLOSED requires completion criteria but omits them; happy-path example has timestamp rather than closed_at | Add the conversation-authorized closure criteria, closed_at, closure_basis, and provenance references in Markdown; preserve HTML unchanged |
| Closure draft lists APPROVED as universally required despite PA_NOT_REQUIRED branch | Use branch-specific coverage milestones; never fabricate approval for no-PA workflow |
| Initial scenario treats PA-required benefit signal as a payer request for labs | Separate PA submission responsibility from the later explicit supporting-information request |
| Earlier narrative puts reconciliation after later approval in a way that can obscure the earlier conflict's result | Keep conflict resolution to NEEDS_INFORMATION distinct from subsequent new payer approval |
| Draft describes workflow status moving to HOLD while also preserving current_state | Keep last verified prescription state; express hold/reconciliation in conflict metadata and qualified views |
| Draft promises no downstream dispensing on conflict | Limit enforcement to Spine promotion/views; do not claim independent upstream or pharmacy control |
| Draft permits generic routing/submission sources as alternate authorities | Require attributable destination acknowledgement or authenticated originating actor; transport alone is insufficient |
| Consent ACTIVE lacks explicit scope matching; NOT_REQUIRED_BY_WORKFLOW could imply a waiver | Match scope/time/purpose/resource and require an attributable policy basis; unresolved required basis yields HOLD |
| HOLD originally defined only as no state promotion despite read operations being in scope | Withhold held/denied reads as well as state mutations; sensitive audit payload retention needs separate authorization |
| Duplicate example returns NO_STATE_CHANGE outside PROMOTE/REJECT/HOLD enum | REJECT only the duplicate promotion attempt, reason DUPLICATE_EVENT, state_changed false |
| G3 purpose guard absent from TransitionDecision object | Add purpose_valid; guard outcomes distinguish PASS, FAIL, UNRESOLVED |
| Missing evidence ambiguously means both REJECT and HOLD | HOLD for potentially valid operation awaiting evidence; REJECT for confirmed prohibited inference/invalid operation |
| No-skip paragraph suggests configurable shortcuts beyond table | Require an explicit versioned alternate edge before using one; default missing-sequence handling is HOLD |
| Closure expects null actor before transition while FOLLOW_UP still has an actor | Evaluate proposed CLOSED object and atomically clear completed responsibilities with evidence |
| Sample vendor statements sound like verified capabilities or market exclusivity | Mark vendor roles as illustrative planned mappings; make no verified comparison or uniqueness claim |

These are documentation consistency corrections, not new runtime behavior. They preserve the source-data, authority, promotion, and successful-closure boundaries.

## Specification readiness

| Layer | Current evidence |
|---|---|
| System definition | Preserved HTML and readable transcription |
| Data model | Preserved HTML plus authorized closure completion in readable baseline |
| Authority / consent | Design contract; no policy engine or verified live actor bindings |
| Transition logic | Table, guards, conceptual decision objects and examples; no implementation |
| Audit / provenance | Requirements referenced; full contract pending |
| Integration adapters | Illustrative mapping only; contracts and implementations pending |
| Runtime / UI | Not implemented in this import |
| Clinical, institutional, regulatory or vendor validation | Not established by these materials |

Before implementation, specify event identity and collision handling; ordering/effective-time rules; state-version/concurrency control; policy versions and decision precedence; atomic audit/promotion/recovery; permitted storage/access/retention; exact action vocabulary and scoped actor bindings; and adapter authentication/delegation evidence.

Optional receipt and follow-up bypass edges, approval shortcuts, denial/reversal routes, reopening, and post-closure correction policies remain unresolved. The successful-path table must not silently supply them. An unresolved policy or missing required evidence fails closed.

The **smallest next artifact is the Audit & Provenance Contract**. No further implementation or new vendor scope is included in this repository import.
