"""Historical reconstruction remains unimplemented and fails closed."""

from .models import PolicyConfig, TransitionDecision, TransitionResult


class ReconstructionService:
    def reconstruct_state(
        self, coordination_id: str, as_of_timestamp: str, policy: PolicyConfig
    ) -> TransitionDecision:
        reason = ("POLICY_UNRESOLVED" if not policy.policy_version
                  else "REPLAY_TIME_AND_POLICY_UNRESOLVED")
        return TransitionDecision(TransitionResult.HOLD, reason, policy.policy_version)

    # Define as-known/promoted versus source-effective time, persist evaluation policy
    # versions and decisions, and apply read authorization before supplying results.
