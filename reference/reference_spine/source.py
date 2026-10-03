"""Adapter/identity boundary: no signature or vendor adapter is implemented."""

from .models import PolicyConfig, SourceEvent, TransitionDecision, TransitionResult


class SourceIdentityService:
    def validate(self, event: SourceEvent, policy: PolicyConfig) -> TransitionDecision:
        if not policy.policy_version:
            reason = "POLICY_UNRESOLVED"
        elif not event.source_system or not event.source_event_id:
            reason = "IDENTITY_UNRESOLVED"
        else:
            reason = "SOURCE_IDENTITY_VALIDATOR_UNIMPLEMENTED"
        return TransitionDecision(TransitionResult.HOLD, reason, policy.policy_version)

    # Future authenticated validator: confirmed invalid identity -> REJECT /
    # INVALID_SOURCE_IDENTITY. Never trust a wire-provided identity_verified flag.
