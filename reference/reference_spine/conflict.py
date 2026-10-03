"""Keep conflict evidence independently from rejection; no state mutation."""

from .models import (
    AttemptRecord, ConflictEvidence, PolicyConfig, TransitionDecision, TransitionResult,
)


def finalize_attempt(
    decision: TransitionDecision, conflicts: tuple[ConflictEvidence, ...]
) -> AttemptRecord:
    """Final promotion veto. Conflict assessment itself is an unimplemented adapter."""
    if decision.result == TransitionResult.PROMOTE:
        reason = "BLOCKING_CONFLICT" if conflicts else "PROMOTION_BACKEND_UNIMPLEMENTED"
        decision = TransitionDecision(TransitionResult.HOLD, reason, decision.policy_version)
    else:
        # Never accept a caller's state_changed assertion for a non-promotion.
        decision = TransitionDecision(decision.result, decision.reason_code,
                                      decision.policy_version, state_changed=False)
    return AttemptRecord(decision, conflicts, promotion_blocked=True)


class ReconciliationService:
    def qualify(self, policy: PolicyConfig) -> TransitionDecision:
        reason = ("POLICY_UNRESOLVED" if not policy.policy_version
                  else "RECONCILIATION_AUTHORITY_UNIMPLEMENTED")
        return TransitionDecision(TransitionResult.HOLD, reason, policy.policy_version)

    # Future qualification record references original events and authority evidence.
    # Qualification does not mutate current_state or mark the source event consumed
    # as a duplicate. A distinct reconsideration attempt must re-run G1-G10.
