-- DRAFT PostgreSQL schema; not applied or validated against a live database.
-- No production writer, actor authentication, policy evaluator, canonical hash
-- encoding, retention enforcement, or Kafka connector is supplied by this scaffold.
BEGIN;
CREATE SCHEMA spine_reference;
REVOKE ALL ON SCHEMA spine_reference FROM PUBLIC;
SET LOCAL search_path = spine_reference, pg_catalog;

CREATE TYPE authorization_result AS ENUM ('ALLOW', 'DENY', 'HOLD');
CREATE TYPE transition_result AS ENUM ('PROMOTE', 'REJECT', 'HOLD');
CREATE TYPE prescription_state AS ENUM (
  'PRESCRIBED', 'PRESCRIPTION_RECEIVED', 'COVERAGE_CHECK', 'PA_NOT_REQUIRED',
  'PA_REQUIRED', 'PA_SUBMITTED', 'PAYER_REVIEW', 'NEEDS_INFORMATION',
  'PROVIDER_ACTION', 'DENIED', 'APPROVED', 'PHARMACY_PROCESSING', 'READY',
  'DISPENSED', 'PATIENT_RECEIPT_KNOWN', 'FOLLOW_UP', 'CLOSED'
);

CREATE TABLE policies (
  policy_version text PRIMARY KEY,
  policy_document jsonb NOT NULL,
  authority_basis_ref text NOT NULL,
  recorded_at timestamptz NOT NULL
);
CREATE TABLE retention_policies (
  retention_policy_version text PRIMARY KEY,
  record_category text NOT NULL,
  applicable_basis_ref text NOT NULL,
  permitted_storage_scope jsonb NOT NULL,
  disposition_rules jsonb NOT NULL,
  recorded_at timestamptz NOT NULL
  -- No universal six/seven-year or indefinite-retention default.
);

CREATE TABLE source_events (
  event_id uuid PRIMARY KEY,
  coordination_id text NOT NULL,
  source_system text NOT NULL CHECK (source_system <> ''),
  source_event_id text NOT NULL CHECK (source_event_id <> ''),
  source_authority text NOT NULL CHECK (source_authority IN
    ('PATIENT', 'PRESCRIBER', 'PHARMACY', 'PAYER', 'SPINE')),
  event_type text NOT NULL,
  actor_id text NOT NULL,
  actor_organization text NOT NULL,
  identity_evidence_ref text NOT NULL,
  raw_payload bytea NOT NULL,
  payload_hash bytea NOT NULL CHECK (octet_length(payload_hash) = 32),
  serialization_version text NOT NULL,
  source_timestamp timestamptz,
  source_sequence text,
  source_effective_scope jsonb NOT NULL,
  received_at timestamptz NOT NULL,
  chain_scope text,
  chain_sequence bigint CHECK (chain_sequence > 0),
  previous_event_hash bytea CHECK (octet_length(previous_event_hash) = 32),
  record_hash bytea CHECK (octet_length(record_hash) = 32),
  corrects_event_ref uuid REFERENCES source_events(event_id),
  revokes_event_ref uuid REFERENCES source_events(event_id),
  policy_version text NOT NULL REFERENCES policies,
  retention_policy_version text NOT NULL REFERENCES retention_policies,
  UNIQUE (source_system, source_event_id),
  UNIQUE (chain_scope, chain_sequence)
  -- Hash fields are storage shapes, not a verified chain or canonicalizer.
  -- A duplicate identity with different payload/context must HOLD in the writer.
);

CREATE TABLE authorization_decisions (
  authorization_id uuid PRIMARY KEY,
  event_ref uuid REFERENCES source_events,
  actor_id text,
  actor_role text,
  organization text,
  patient_ref text,
  purpose text,
  resource_type text NOT NULL,
  resource_id text NOT NULL,
  requested_action text NOT NULL,
  result authorization_result NOT NULL,
  reason_code text NOT NULL,
  authority_basis jsonb NOT NULL,
  consent_basis jsonb NOT NULL,
  policy_version text REFERENCES policies,
  evaluated_at timestamptz NOT NULL,
  CHECK (result = 'HOLD' OR policy_version IS NOT NULL)
  -- Null event_ref permits audit of denied/held reads or unresolved intake.
);

CREATE TABLE transition_decisions (
  transition_id uuid PRIMARY KEY,
  event_ref uuid NOT NULL REFERENCES source_events,
  authorization_ref uuid NOT NULL REFERENCES authorization_decisions,
  coordination_id text NOT NULL,
  from_state prescription_state,
  requested_to_state prescription_state NOT NULL,
  from_version bigint NOT NULL CHECK (from_version >= 0),
  result transition_result NOT NULL,
  reason_code text NOT NULL,
  guards jsonb NOT NULL,
  ordering_evidence jsonb NOT NULL,
  policy_version text REFERENCES policies,
  evaluated_at timestamptz NOT NULL,
  CHECK (result <> 'PROMOTE' OR policy_version IS NOT NULL)
);

CREATE TABLE conflicts (
  conflict_id uuid PRIMARY KEY,
  coordination_id text NOT NULL,
  current_event_ref uuid NOT NULL REFERENCES source_events,
  incoming_event_ref uuid NOT NULL REFERENCES source_events,
  fact_scope jsonb NOT NULL,
  authority_basis_refs jsonb NOT NULL,
  promotion_blocked boolean NOT NULL CHECK (promotion_blocked),
  detected_at timestamptz NOT NULL,
  hold_reason text NOT NULL
);
CREATE TABLE conflict_resolutions (
  resolution_id uuid PRIMARY KEY,
  conflict_ref uuid NOT NULL REFERENCES conflicts,
  governing_event_ref uuid NOT NULL REFERENCES source_events,
  qualification_state text NOT NULL CHECK (qualification_state = 'VERIFIED_STATE'),
  authority_basis jsonb NOT NULL,
  evidence_basis jsonb NOT NULL,
  policy_version text NOT NULL REFERENCES policies,
  resolved_by text NOT NULL,
  resolved_at timestamptz NOT NULL,
  UNIQUE (conflict_ref)
  -- Qualification only. It never writes current_states by itself.
);

CREATE TABLE state_promotions (
  promotion_id uuid PRIMARY KEY,
  coordination_id text NOT NULL,
  event_ref uuid NOT NULL REFERENCES source_events,
  authorization_ref uuid NOT NULL REFERENCES authorization_decisions,
  transition_ref uuid NOT NULL REFERENCES transition_decisions UNIQUE,
  prior_version bigint NOT NULL CHECK (prior_version >= 0),
  new_version bigint NOT NULL CHECK (new_version = prior_version + 1),
  prior_state prescription_state,
  promoted_state prescription_state NOT NULL,
  prior_responsible_actor text,
  new_responsible_actor text,
  resulting_snapshot jsonb NOT NULL,
  policy_version text NOT NULL REFERENCES policies,
  promoted_at timestamptz NOT NULL,
  UNIQUE (coordination_id, new_version)
);
CREATE TABLE current_states (
  coordination_id text PRIMARY KEY,
  version bigint NOT NULL CHECK (version > 0),
  promotion_ref uuid NOT NULL REFERENCES state_promotions,
  status prescription_state NOT NULL,
  source text NOT NULL,
  responsible_actor text,
  next_required_action text,
  patient_action text NOT NULL,
  last_updated timestamptz NOT NULL,
  confidence text NOT NULL,
  closure_reason text,
  closed_at timestamptz,
  closure_basis jsonb,
  closure_provenance_refs jsonb,
  FOREIGN KEY (coordination_id, version)
    REFERENCES state_promotions(coordination_id, new_version),
  CHECK (status <> 'CLOSED' OR (
    responsible_actor IS NULL AND next_required_action IS NULL
    AND patient_action = 'None' AND closure_reason IS NOT NULL AND closed_at IS NOT NULL
    AND closure_basis IS NOT NULL AND jsonb_typeof(closure_basis) = 'array'
    AND jsonb_array_length(closure_basis) > 0
    AND closure_provenance_refs IS NOT NULL
    AND jsonb_typeof(closure_provenance_refs) = 'array'
    AND jsonb_array_length(closure_provenance_refs) > 0
  ))
  -- Active conflicts are an overlay, never current prescription status = HOLD.
  -- Clinical/milestone evidence checks still require a policy-bound evaluator.
);

CREATE TABLE provenance_links (
  link_id uuid PRIMARY KEY,
  coordination_id text NOT NULL,
  event_ref uuid NOT NULL REFERENCES source_events,
  authorization_ref uuid REFERENCES authorization_decisions,
  transition_ref uuid REFERENCES transition_decisions,
  prior_promotion_ref uuid REFERENCES state_promotions,
  resulting_promotion_ref uuid REFERENCES state_promotions,
  link_type text NOT NULL,
  recorded_at timestamptz NOT NULL
);
CREATE TABLE audit_events (
  audit_id uuid PRIMARY KEY,
  recorded_at timestamptz NOT NULL,
  action_type text NOT NULL CHECK (action_type IN (
    'EVENT_RECEIVED', 'AUTHORIZATION_EVALUATED', 'TRANSITION_EVALUATED',
    'STATE_PROMOTED', 'STATE_REJECTED', 'STATE_HELD', 'DUPLICATE_EVENT',
    'CONFLICT_DETECTED', 'RECONCILIATION_PERFORMED', 'CLOSED'
  )),
  actor_id text,
  organization text,
  patient_ref text,
  purpose text,
  resource_type text NOT NULL,
  resource_id text NOT NULL,
  event_ref uuid REFERENCES source_events,
  authorization_ref uuid REFERENCES authorization_decisions,
  transition_ref uuid REFERENCES transition_decisions,
  promotion_ref uuid REFERENCES state_promotions,
  conflict_ref uuid REFERENCES conflicts,
  authorization_outcome authorization_result,
  transition_outcome transition_result,
  reason_code text NOT NULL,
  authority_basis jsonb NOT NULL,
  consent_basis jsonb NOT NULL,
  prior_state_ref uuid REFERENCES state_promotions,
  resulting_state_ref uuid REFERENCES state_promotions,
  policy_version text REFERENCES policies,
  retention_policy_version text NOT NULL REFERENCES retention_policies,
  provenance_refs jsonb NOT NULL
);

-- Inbox/checkpoint bookkeeping is mutable. It is not immutable source evidence.
CREATE TABLE consumer_checkpoints (
  consumer_group text NOT NULL,
  topic text NOT NULL,
  partition_id integer NOT NULL CHECK (partition_id >= 0),
  next_offset bigint NOT NULL CHECK (next_offset >= 0),
  PRIMARY KEY (consumer_group, topic, partition_id)
);
CREATE TABLE delivery_attempts (
  attempt_id uuid PRIMARY KEY,
  event_ref uuid REFERENCES source_events,
  source_system text,
  source_event_id text,
  observed_at timestamptz NOT NULL,
  outcome transition_result NOT NULL,
  reason_code text NOT NULL,
  audit_ref uuid NOT NULL REFERENCES audit_events
);

CREATE FUNCTION block_evidence_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'reference evidence is append-only; update/delete is prohibited';
END;
$$;
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['policies', 'retention_policies', 'source_events',
    'authorization_decisions', 'transition_decisions', 'conflicts',
    'conflict_resolutions', 'state_promotions', 'provenance_links',
    'audit_events', 'delivery_attempts']
  LOOP
    EXECUTE format('CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON %I '
      'FOR EACH ROW EXECUTE FUNCTION block_evidence_mutation()', t);
  END LOOP;
END;
$$;

-- Materialization is provisional: validates links and versions, not source truth.
CREATE FUNCTION require_promotion_record() RETURNS trigger
LANGUAGE plpgsql SET search_path = spine_reference, pg_catalog AS $$
DECLARE p state_promotions%ROWTYPE;
BEGIN
  SELECT * INTO p FROM state_promotions WHERE promotion_id = NEW.promotion_ref;
  IF NOT FOUND OR p.coordination_id <> NEW.coordination_id
      OR p.new_version <> NEW.version OR p.promoted_state <> NEW.status
      OR p.new_responsible_actor IS DISTINCT FROM NEW.responsible_actor THEN
    RAISE EXCEPTION 'materialized state must match a promotion record';
  END IF;
  IF TG_OP = 'INSERT' AND p.prior_version <> 0 THEN
    RAISE EXCEPTION 'initial materialization requires version zero predecessor';
  END IF;
  IF TG_OP = 'UPDATE' AND (OLD.coordination_id <> NEW.coordination_id
      OR p.prior_version <> OLD.version OR p.prior_state IS DISTINCT FROM OLD.status
      OR OLD.status = 'CLOSED') THEN
    RAISE EXCEPTION 'invalid materialization predecessor or terminal state';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM authorization_decisions a JOIN transition_decisions d
      ON d.authorization_ref = a.authorization_id
      JOIN source_events e ON e.event_id = d.event_ref
    WHERE a.authorization_id = p.authorization_ref AND a.result = 'ALLOW'
      AND d.transition_id = p.transition_ref AND d.result = 'PROMOTE'
      AND a.event_ref = p.event_ref AND d.event_ref = p.event_ref
      AND d.coordination_id = p.coordination_id AND d.from_version = p.prior_version
      AND d.requested_to_state = p.promoted_state
      AND d.from_state IS NOT DISTINCT FROM p.prior_state
      AND e.coordination_id = p.coordination_id
      AND d.guards @> '{"G1":"PASS","G2":"PASS","G3":"PASS","G4":"PASS",
        "G5":"PASS","G6":"PASS","G7":"PASS","G8":"PASS","G9":"PASS","G10":"PASS"}'::jsonb
      AND a.policy_version = p.policy_version AND d.policy_version = p.policy_version
  ) THEN
    RAISE EXCEPTION 'matching authorization and transition records are required';
  END IF;
  IF EXISTS (SELECT 1 FROM conflicts c WHERE c.coordination_id = NEW.coordination_id
      AND NOT EXISTS (SELECT 1 FROM conflict_resolutions r
                      WHERE r.conflict_ref = c.conflict_id)) THEN
    RAISE EXCEPTION 'unresolved conflict blocks materialization';
  END IF;
  RETURN NEW;
END;
$$;
CREATE TRIGGER promotion_required BEFORE INSERT OR UPDATE ON current_states
FOR EACH ROW EXECUTE FUNCTION require_promotion_record();
CREATE TRIGGER no_current_state_delete BEFORE DELETE ON current_states
FOR EACH ROW EXECUTE FUNCTION block_evidence_mutation();

REVOKE ALL ON ALL TABLES IN SCHEMA spine_reference FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA spine_reference FROM PUBLIC;
COMMIT;
-- Deployment must create least-privilege roles and one transaction-bound writer.
-- That writer must save decisions/conflicts/promotion/audit/checkpoint atomically,
-- serialize each coordination_id, and re-evaluate closure/conflicts before commit.
-- Owners/superusers can bypass these controls; this schema is not a security boundary.
