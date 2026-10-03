# Specification provenance and current status

## Authority and scope

On 2026-10-03, Nicholas B. Carty (N.B.C.) directed that the supplied Healthcare Coordination Spine material be placed in `heliosfi/Healthcare-Coordination-Spine`. Earlier explicit “N.B.C authority continue” authorized successful-only closure completion, carrying forward the v0.1 data-model baseline, and proceeding through the Authority & Consent and State-Transition contracts.

This repository import is documentation-only. Specification language such as MUST, “frozen,” “implements,” and “executable” describes intended design obligations, not executed code or validation. No paper/live authority, clinical authority, vendor account, outreach, or broader project disposition is created by this import.

## Source inventory

| Source | Repository location | Treatment |
|---|---|---|
| Uploaded Healthcare Coordination Spine — v0 System Definition.html | [Original HTML](../archive/source-artifacts/v0-system-definition.html) | Byte-preserved; readable transcription in specifications |
| Uploaded Healthcare Coordination Spine — v0.1 Data Model.html | [Original HTML](../archive/source-artifacts/v0.1-data-model.html) | Byte-preserved; readable specification adds subsequently authorized closure completion |
| Uploaded Healthcare Coordination Spine — v0.1 Audit & Provenance Contract.html | [Original HTML](../archive/source-artifacts/v0.1-audit-provenance-contract.html) and [readable draft](specifications/v0.1-audit-provenance-contract.md) | Byte-preserved source; imported draft, not ratified or implemented |
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
| Audit / provenance | Uploaded draft preserved and transcribed; cross-contract reconciliation and ratification pending |
| Integration adapters | Illustrative mapping only; contracts and implementations pending |
| Runtime / UI | Local Python fail-closed reference stubs and synthetic fixtures only; no deployed runtime or UI |
| Clinical, institutional, regulatory or vendor validation | Not established by these materials |

Before implementation, specify event identity and collision handling; ordering/effective-time rules; state-version/concurrency control; policy versions and decision precedence; atomic audit/promotion/recovery; permitted storage/access/retention; exact action vocabulary and scoped actor bindings; and adapter authentication/delegation evidence.

Optional receipt and follow-up bypass edges, approval shortcuts, denial/reversal routes, reopening, and post-closure correction policies remain unresolved. The successful-path table must not silently supply them. An unresolved policy or missing required evidence fails closed.

The **smallest next step is reconciliation of the imported Audit & Provenance draft** with the existing contracts. No runtime implementation or new vendor scope is included in this repository import.

## Audit & Provenance draft import 2026-10-03

The user instructed “Drop this in the repo too.” The uploaded HTML is preserved unchanged, linked from the README, and transcribed into readable Markdown. Its status is **Draft for Implementation**, with “Immutable once ratified” in the source footer. Import authorization does not ratify the draft or override the existing authority/consent, conflict, duplicate, or closure rules.

The source displays “Last updated: 2026-01-04.” That is the artifact's displayed date, distinct from the verified repository import date; its accuracy and provenance are not established by this import.

The following are repository-editor observations, not silent changes to the source:

| Draft issue | Required reconciliation before implementation |
|---|---|
| DUPLICATE_EVENT is required by duplicate handling but missing from AuditEvent.action_type | Complete the action vocabulary while preserving the transition contract's duplicate REJECT/no-state-change outcome |
| AuditEvent.decision contains ALLOW/DENY/HOLD only | Represent authorization and transition results separately; do not recast PROMOTE/REJECT as authorization decisions |
| Pipe-delimited idempotency inputs lack escaping or length framing | Define an injective canonical encoding and reject incompatible content under the same source identity |
| “Canonical JSON” and hash chaining lack exact bytes, full-record hash definition, algorithm encoding, chain scope, and verification anchor | Specify canonical serialization and chain verification; SHA-256 alone does not establish authenticated origin or a functioning tamper-evident log |
| Ordering prioritizes source timestamps, references a sequence field absent from SpineEvent, and treats previous_event_hash as causality | Define source sequence/effective-time semantics, policy versions, and causal references separately from append-log order; unresolved ordering remains HOLD |
| REVOKED uses previous_event_hash to reference an arbitrary original | Separate chain predecessor from corrects/revokes references; define authorized revocation events and valid transitions rather than silently adding runtime behavior |
| Full-payload retention, seven-year minimum, and no-hard-delete assertions lack an established applicable policy basis | Resolve permitted retention, access, redaction, and deletion requirements; source wording is a draft proposal, not a verified legal rule or authorization to retain denied payloads |
| Source says the contract operates after transitions but requires audit records for authorization DENY/HOLD | Audit authorization outcomes even when transition evaluation never occurs, under permitted storage/access rules |
| ACTIVE, CLAIM_PAID, and REVOKED examples are outside or undefined by existing prescription/status contracts; Authority omits SPINE coordination events | Define event and state vocabularies and separate external source authority from Spine-authored coordination attestations |
| Linear provenance edge sketch places prior state after transition decision; “losing” claims are marked superseded despite immutability | Specify reference direction/topology and record reconciliation classification as new metadata rather than rewriting source claims |
| Historical reconstruction promises replay without defining time basis, policy versions, concurrent ordering, or recovery | Define source-effective versus as-known/promoted history, versioned evaluation, atomic persistence, and determinism before claiming replay capability |

The existing data-model successful-closure criteria, branch-specific milestones, source-domain boundaries, and last-verified-state preservation remain unchanged. This addition supplies the next draft artifact; it does not establish cryptographic, runtime, clinical, or regulatory verification.

## Python reference scaffold 2026-10-03

The user supplied corrected architecture and requested the actual Python stub files and schema outline. [reference/README.md](../reference/README.md) records the supplied design direction and repository-editor completion of the event flow, API targets, folder map, and implementation boundaries. Existing uploaded source artifacts remain unchanged.

The Python services fail closed: authority/read handlers do not ALLOW or disclose, transitions do not PROMOTE, and reconciliation/reconstruction remain HOLD. The transition table and synthetic inbox/conflict helpers demonstrate selected boundaries without authenticating vendors or processing real patient data. A policy-version label alone does not establish policy validity or grant authority.

The synthetic fixtures record **expected contract behavior**, including hypothetical ALLOW/PROMOTE decisions. They are not executed service outputs. The supplied architecture's claim of complete enforcement is not adopted as runtime evidence.

Corrections carried into the scaffold:

- Conflict evidence survives a rejected edge; a blocking conflict vetoes provisional promotion before any future commit.
- Source identity must be verified separately from client labels; unresolved identity is HOLD.
- Exact redelivery is distinct from a new evaluation of an already retained event after qualification; incompatible identity reuse is HOLD.
- Consumer checkpoints committed with effects form an inbox/checkpoint pattern; an outbox covers outgoing delivery. Neither integration is implemented.
- Append-chain order is distinct from source causality. Canonical integrity encoding and trusted verification anchors remain pending.
- The proposed universal six-year audit minimum is not ratified. Retention is scoped by record category and applicable policy; no indefinite CLOSED default is set.
- Event/decision/promotion/audit/checkpoint persistence needs one transaction and concurrency control; the SQL draft does not supply an authenticated writer or full policy enforcement.

Verification: 19 Python boundary tests passed; the default CLI returned HOLD / POLICY_UNRESOLVED with no disclosed data. Fixture links, source checksums, and Markdown references were checked during preparation. **The SQL schema has not been applied or validated against a PostgreSQL instance.** No exactly-once, hash-chain, clinical, or compliance result is established.
