"""Contract table and fail-closed evaluation stub; never produces PROMOTE."""

from collections.abc import Mapping

from .models import (
    AuthorizationDecision, AuthorizationResult, GUARD_NAMES, GuardOutcome,
    PolicyConfig, TransitionDecision, TransitionResult,
)


ALLOWED_EDGES = frozenset({
    (None, "PRESCRIBED"),
    ("PRESCRIBED", "PRESCRIPTION_RECEIVED"),
    ("PRESCRIPTION_RECEIVED", "COVERAGE_CHECK"),
    ("COVERAGE_CHECK", "PA_NOT_REQUIRED"),
    ("COVERAGE_CHECK", "PA_REQUIRED"),
    ("PA_REQUIRED", "PA_SUBMITTED"),
    ("PA_SUBMITTED", "PAYER_REVIEW"),
    ("PAYER_REVIEW", "NEEDS_INFORMATION"),
    ("NEEDS_INFORMATION", "PROVIDER_ACTION"),
    ("PROVIDER_ACTION", "PAYER_REVIEW"),
    ("PAYER_REVIEW", "APPROVED"),
    ("PAYER_REVIEW", "DENIED"),
    ("PA_NOT_REQUIRED", "PHARMACY_PROCESSING"),
    ("APPROVED", "PHARMACY_PROCESSING"),
    ("PHARMACY_PROCESSING", "READY"),
    ("READY", "DISPENSED"),
    ("DISPENSED", "PATIENT_RECEIPT_KNOWN"),
    ("PATIENT_RECEIPT_KNOWN", "FOLLOW_UP"),
    ("FOLLOW_UP", "CLOSED"),
})


class StateTransitionService:
    def evaluate(
        self, prior_state: str | None, requested_state: str,
        authorization: AuthorizationDecision,
        guards: Mapping[str, GuardOutcome], policy: PolicyConfig,
    ) -> TransitionDecision:
        def result(value: TransitionResult, reason: str) -> TransitionDecision:
            return TransitionDecision(value, reason, policy.policy_version)

        if not policy.policy_version:
            return result(TransitionResult.HOLD, "POLICY_UNRESOLVED")
        if authorization.policy_version != policy.policy_version:
            return result(TransitionResult.HOLD, "POLICY_VERSION_MISMATCH")
        if guards.get("G1") == GuardOutcome.FAIL:
            return result(TransitionResult.REJECT, "INVALID_SOURCE_IDENTITY")
        if guards.get("G1") != GuardOutcome.PASS:
            return result(TransitionResult.HOLD, "IDENTITY_UNRESOLVED")
        if authorization.result == AuthorizationResult.DENY:
            return result(TransitionResult.REJECT, "AUTHORIZATION_DENIED")
        if authorization.result != AuthorizationResult.ALLOW:
            return result(TransitionResult.HOLD, "AUTHORIZATION_UNRESOLVED")
        if guards.get("G10") == GuardOutcome.FAIL:
            return result(TransitionResult.REJECT, "DUPLICATE_EVENT")
        if (prior_state, requested_state) not in ALLOWED_EDGES:
            return result(TransitionResult.REJECT, "INVALID_TRANSITION")
        if guards.get("G8") == GuardOutcome.FAIL:
            return result(TransitionResult.HOLD, "BLOCKING_CONFLICT")
        if any(guards.get(name) != GuardOutcome.PASS for name in GUARD_NAMES):
            return result(TransitionResult.HOLD, "GUARD_EVIDENCE_UNRESOLVED")
        # Even supplied PASS labels do not implement authority, evidence, ordering,
        # closure predicates, or atomic persistence. This reference cannot promote.
        return result(TransitionResult.HOLD, "TRANSITION_EVALUATOR_UNIMPLEMENTED")
