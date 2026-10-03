# v0.1 Python reference scaffold

**Status: local reference scaffold, synthetic fixtures, fail-closed stubs.** This is not a deployable clinical service or full enforcement implementation. Audit & Provenance remains a draft. The services have no network, database, Kafka, or vendor clients, and cannot authorize reads or promote state.

## Run locally

Python 3.11 or newer; Python standard library only. From the repository root:

```bash
PYTHONPATH=reference python -m reference_spine
PYTHONPATH=reference python -m unittest discover -s reference/tests -v
```

The first command returns HOLD / POLICY_UNRESOLVED with `data: null`. Supplying a policy version is not enough to activate a stub. The tests verify withholding and selected boundary helpers; they do not prove a production engine or validate SQL against PostgreSQL.

## Files and responsibility

| Location | Purpose |
|---|---|
| [models.py](reference_spine/models.py) | Separate authorization/transition enums, contexts, policy references, immutable local records |
| [source.py](reference_spine/source.py) | Identity adapter stub; unknown identity is HOLD |
| [authority.py](reference_spine/authority.py) | Authority/purpose/consent stub; never returns ALLOW |
| [transition.py](reference_spine/transition.py) | Existing explicit transition table and G1–G10 inputs; never returns PROMOTE |
| [conflict.py](reference_spine/conflict.py) | Preserve conflict evidence even after REJECT; veto promotion; reconciliation stub |
| [inbox.py](reference_spine/inbox.py) | Synthetic-only duplicate/collision demonstration; no durable ingestion |
| [read_api.py](reference_spine/read_api.py) | In-process withheld read response; no HTTP server |
| [reconstruction.py](reference_spine/reconstruction.py) | Held historical reconstruction stub |
| [schema.sql](sql/schema.sql) | Draft PostgreSQL shapes, references, append-only triggers, provisional materialization guards |
| [happy_path.json](fixtures/happy_path.json) | Synthetic expected source/decision/promotion/audit chain |
| [conflict.json](fixtures/conflict.json) | Rejection plus preserved conflict, qualification without automatic promotion |
| [duplicate.json](fixtures/duplicate.json) | Duplicate delivery and incompatible reuse of source identity |
| [test_boundaries.py](tests/test_boundaries.py) | Adversarial default-withholding and promotion-veto checks |

## Proposed topology

Adapters and identity verification remain interfaces outside the core. Authority/consent and transition modules remain separate from conflict assessment, the transaction-bound writer, and read authorization. A future PostgreSQL materialized state derives from persisted promotions and decisions; event payloads alone are insufficient for replay. Kafka and separate graph storage are optional deployment choices, not scaffold dependencies.

## Corrected event flow

1. Receive a bounded intake envelope. Before retaining a full payload, establish permitted storage and retention context; unresolved intake does not become an accepted authoritative event.
2. Validate source identity and a verified source namespace. Unresolved identity/authority yields HOLD; confirmed invalid identity yields REJECT / INVALID_SOURCE_IDENTITY. Actual cryptographic validation is unimplemented.
3. Recognize exact redelivery separately from incompatible content under the same source identity. Preserve the original event ID. Duplicate delivery is REJECT / DUPLICATE_EVENT with no state change; collision is HOLD.
4. Evaluate actor, organization, patient, purpose, resource, consent, and policy-version context. DENY/HOLD cannot reach promotion; both still need a permitted audit path.
5. Evaluate all required transition guards and independently record any attributable consequential contradiction, including when an edge is REJECTED. Scope/order uncertainty is not a reason to silently classify claims as compatible.
6. Before any commit, a blocking conflict or unresolved guard vetoes provisional promotion. Hold metadata does not replace the last verified prescription state.
7. A future writer atomically persists authorized evidence, decisions, conflict changes, optional promotion, state version, audit links, and consumer checkpoint under per-episode concurrency control. Missing backend currently yields HOLD.

Audit occurs on every outcome, including steps stopped before transition evaluation. It is not a best-effort action appended after an independently committed state change. Intake/audit retention authorization is separate from authority to promote a source assertion.

## Proposed API surface

These are interface targets, not running endpoints. Every read requires fresh scoped authority/purpose/consent evaluation; audit and historical queries have their own resource scope.

| Method | Route | Bounded responsibility |
|---|---|---|
| POST | `/events` | Authenticated adapter intake; no clinical action or implicit promotion |
| GET | `/coordination/{id}` | Verified prescription state plus hold/conflict qualification |
| GET | `/provenance/{id}` | Permitted source/decision/promotion references |
| GET | `/audit/{id}` | Separately authorized decision/audit view |
| GET | `/coordination/{id}/history?as_of=...&time_basis=...` | Explicit as-known/promoted versus source-effective query; unresolved time basis is HOLD |
| GET | `/coordination/{id}/conflicts` | Permitted conflict and reconciliation evidence |
| GET | `/coordination/{id}/responsibility` | Attributable responsibility handoffs |
| POST | `/coordination/{id}/reconciliations` | Competent actor's qualification evidence; no automatic promotion |

Event/decision/guard labels from clients are never trusted as authentication or authorization results. Reconciliation re-evaluation is a distinct attempt on a stored event, not another source delivery: reusing retained evidence must not be permanently blocked as a duplicate.

## Persistence and integrity boundaries

Storing Kafka input and a checkpoint with effects in PostgreSQL is an **inbox/checkpoint transaction**. An **outbox** is for outgoing messages written in the same database transaction as committed effects. Neither is implemented here. Namespace-scoped uniqueness, collision detection, concurrency/rebalance fencing, monotonic offsets, and retry recovery require a real writer before claiming exactly-once effects.

The SQL draft supplies separate authorization and transition outcomes, raw payloads, policy versions, ordering evidence, conflicts, closure references, and promotion references. Its checks do not authenticate source facts, evaluate all guards, or verify clinical/closure evidence. No SQL adapter or least-privilege writer exists; database owners can bypass triggers. The schema has not been applied to a PostgreSQL instance.

Define canonical bytes, full-record hash coverage, chain scope/sequence, trusted checkpoints, and external verification anchors before claiming tamper evidence. A chain predecessor is not proof of clinical causality; source-effective times, sequence, and causal references need independent attribution. No cryptographic chain implementation is included.

## Retention

No universal six-year audit-event minimum is established by this scaffold. HHS's six-year Security Rule requirement concerns required documentation, measured from creation or last effect as applicable. Medical-record and other event categories need applicable requirements and an attributable organizational policy. CLOSED summaries have no automatic indefinite default.

Sources: [HHS Security Rule summary](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html), [HHS medical-record retention FAQ](https://www.hhs.gov/hipaa/for-professionals/faq/does-hipaa-require-covered-entities-to-keep-medical-records-for-any-period/index.html), and [Apache Kafka delivery semantics](https://kafka.apache.org/41/design/design/).

## Remaining work

Resolve the [Audit & Provenance draft discrepancies](../docs/specification-status.md#audit--provenance-draft-import-2026-10-03), policy/action vocabulary, authenticated adapters, canonical integrity format, retention/access basis, guard evaluation precedence, closure evidence, and atomic persistence/recovery before replacing any HOLD stub. Qualification alone does not promote VERIFIED_STATE as a prescription status. No active conflict can coexist with a committed successful closure.

Fixtures contain expected contract behavior, not actual service outputs. The reference stubs intentionally HOLD the hypothetical happy path until those implementation requirements are supplied and verified.
