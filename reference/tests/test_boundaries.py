"""Adversarial checks for scaffold withholding; no clinical/integration validation."""

import unittest
from dataclasses import replace

from reference_spine.authority import AuthorityConsentService
from reference_spine.conflict import ReconciliationService, finalize_attempt
from reference_spine.inbox import SyntheticInbox
from reference_spine.models import (
    AuthorizationContext, AuthorizationDecision, AuthorizationResult,
    ConflictEvidence, GUARD_NAMES, GuardOutcome, PolicyConfig, SourceEvent,
    TransitionDecision, TransitionResult,
)
from reference_spine.read_api import ReadAPI
from reference_spine.reconstruction import ReconstructionService
from reference_spine.source import SourceIdentityService
from reference_spine.transition import StateTransitionService


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.policy = PolicyConfig("fixture_policy_v1", "fixture_retention_v1")
        self.context = AuthorizationContext(
            "fixture_actor", "PATIENT", "fixture_org", "fixture_patient",
            "patient_access", "CoordinationState", "fixture_episode", "READ",
        )
        self.allow = AuthorizationDecision(
            AuthorizationResult.ALLOW, "SYNTHETIC_ALLOW_ONLY", self.policy.policy_version
        )
        self.guards = {name: GuardOutcome.PASS for name in GUARD_NAMES}
        self.event = SourceEvent("fixture_event_1", "fixture_episode", "fixture_source",
                                 "fixture_source_1", "READY", b'{"status":"READY"}', True)
        self.conflict = ConflictEvidence("fixture_conflict", "fixture_old", "fixture_new",
                                         ("fixture_authority_basis",))

    def test_missing_policy_never_authorizes(self):
        d = AuthorityConsentService().evaluate(self.context, PolicyConfig())
        self.assertEqual((d.result, d.reason_code),
                         (AuthorizationResult.HOLD, "POLICY_UNRESOLVED"))

    def test_policy_version_alone_never_authorizes(self):
        d = AuthorityConsentService().evaluate(self.context, self.policy)
        self.assertEqual(d.result, AuthorizationResult.HOLD)

    def test_unknown_role_is_held(self):
        d = AuthorityConsentService().evaluate(replace(self.context, actor_role="ADMIN"),
                                              self.policy)
        self.assertEqual(d.reason_code, "AUTHORITY_UNRESOLVED")

    def test_read_response_never_discloses_data(self):
        response = ReadAPI(self.policy).get(self.context)
        self.assertIsNone(response.data)
        self.assertEqual(response.authorization.result, AuthorizationResult.HOLD)

    def test_present_source_labels_are_not_identity_verification(self):
        d = SourceIdentityService().validate(self.event, self.policy)
        self.assertEqual(d.result, TransitionResult.HOLD)

    def test_unresolved_identity_precedes_invalid_transition(self):
        guards = dict(self.guards, G1=GuardOutcome.UNRESOLVED)
        d = StateTransitionService().evaluate("READY", "APPROVED", self.allow,
                                              guards, self.policy)
        self.assertEqual((d.result, d.reason_code),
                         (TransitionResult.HOLD, "IDENTITY_UNRESOLVED"))

    def test_confirmed_invalid_identity_is_rejected(self):
        guards = dict(self.guards, G1=GuardOutcome.FAIL)
        d = StateTransitionService().evaluate("READY", "DISPENSED", self.allow,
                                              guards, self.policy)
        self.assertEqual((d.result, d.reason_code),
                         (TransitionResult.REJECT, "INVALID_SOURCE_IDENTITY"))

    def test_unlisted_transition_is_rejected(self):
        d = StateTransitionService().evaluate("DENIED", "CLOSED", self.allow,
                                              self.guards, self.policy)
        self.assertEqual(d.result, TransitionResult.REJECT)

    def test_all_pass_labels_cannot_activate_stub(self):
        d = StateTransitionService().evaluate("READY", "DISPENSED", self.allow,
                                              self.guards, self.policy)
        self.assertEqual((d.result, d.state_changed), (TransitionResult.HOLD, False))

    def test_mixed_policy_versions_are_held(self):
        old = replace(self.allow, policy_version="fixture_old_policy")
        d = StateTransitionService().evaluate("READY", "DISPENSED", old,
                                              self.guards, self.policy)
        self.assertEqual(d.reason_code, "POLICY_VERSION_MISMATCH")

    def test_duplicate_returns_original_id_without_promotion(self):
        inbox = SyntheticInbox()
        inbox.observe(self.event, self.policy)
        result = inbox.observe(replace(self.event, event_id="fixture_redelivery"), self.policy)
        self.assertEqual(result.existing_event_id, self.event.event_id)
        self.assertEqual((result.decision.result, result.decision.reason_code,
                          result.decision.state_changed),
                         (TransitionResult.REJECT, "DUPLICATE_EVENT", False))

    def test_identity_collision_preserves_original(self):
        inbox = SyntheticInbox()
        inbox.observe(self.event, self.policy)
        for changed in (replace(self.event, payload=b'{"status":"APPROVED"}'),
                        replace(self.event, coordination_id="fixture_other_episode")):
            result = inbox.observe(changed, self.policy)
            self.assertEqual(result.decision.reason_code, "SOURCE_IDENTITY_COLLISION")
            self.assertEqual(result.decision.result, TransitionResult.HOLD)
        original = inbox.observe(self.event, self.policy)
        self.assertEqual(original.decision.reason_code, "DUPLICATE_EVENT")

    def test_synthetic_inbox_requires_retention_policy(self):
        result = SyntheticInbox().observe(self.event, PolicyConfig("fixture_policy"))
        self.assertEqual(result.decision.reason_code, "POLICY_UNRESOLVED")

    def test_non_fixture_input_is_not_stored_by_demo_inbox(self):
        with self.assertRaises(ValueError):
            SyntheticInbox().observe(replace(self.event, synthetic=False), self.policy)

    def test_conflict_survives_transition_rejection(self):
        rejected = TransitionDecision(TransitionResult.REJECT, "INVALID_TRANSITION",
                                      self.policy.policy_version)
        result = finalize_attempt(rejected, (self.conflict,))
        self.assertEqual(result.decision.result, TransitionResult.REJECT)
        self.assertEqual(result.conflicts, (self.conflict,))
        self.assertTrue(result.promotion_blocked)

    def test_conflict_vetoes_provisional_promotion(self):
        provisional = TransitionDecision(TransitionResult.PROMOTE, "SYNTHETIC_ONLY",
                                         self.policy.policy_version, True)
        result = finalize_attempt(provisional, (self.conflict,))
        self.assertEqual((result.decision.result, result.decision.reason_code,
                          result.decision.state_changed),
                         (TransitionResult.HOLD, "BLOCKING_CONFLICT", False))

    def test_clear_conflict_list_does_not_supply_persistence_backend(self):
        provisional = TransitionDecision(TransitionResult.PROMOTE, "SYNTHETIC_ONLY",
                                         self.policy.policy_version, True)
        result = finalize_attempt(provisional, ())
        self.assertEqual(result.decision.result, TransitionResult.HOLD)

    def test_reconciliation_does_not_promote(self):
        d = ReconciliationService().qualify(self.policy)
        self.assertEqual((d.result, d.state_changed), (TransitionResult.HOLD, False))

    def test_reconstruction_does_not_invent_historical_state(self):
        d = ReconstructionService().reconstruct_state("fixture_episode", "2026-10-03",
                                                       self.policy)
        self.assertEqual(d.result, TransitionResult.HOLD)


if __name__ == "__main__":
    unittest.main()
