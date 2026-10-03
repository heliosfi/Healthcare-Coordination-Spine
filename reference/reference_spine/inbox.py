"""Synthetic-only in-memory duplicate demonstration, not an ingestion store."""

from dataclasses import dataclass

from .models import PolicyConfig, SourceEvent, TransitionDecision, TransitionResult


@dataclass(frozen=True)
class InboxObservation:
    existing_event_id: str | None
    decision: TransitionDecision


class SyntheticInbox:
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], SourceEvent] = {}

    def observe(self, event: SourceEvent, policy: PolicyConfig) -> InboxObservation:
        if not event.synthetic:
            raise ValueError("SyntheticInbox accepts synthetic fixtures only")
        if not policy.policy_version or not policy.retention_policy_version:
            reason = "POLICY_UNRESOLVED"
        elif not event.source_system or not event.source_event_id:
            reason = "IDENTITY_UNRESOLVED"
        else:
            key = (event.source_system, event.source_event_id)
            previous = self._events.get(key)
            if previous:
                same_assertion = (
                    previous.coordination_id == event.coordination_id
                    and previous.event_type == event.event_type
                    and previous.payload == event.payload
                )
                value = TransitionResult.REJECT if same_assertion else TransitionResult.HOLD
                reason = "DUPLICATE_EVENT" if same_assertion else "SOURCE_IDENTITY_COLLISION"
                return InboxObservation(previous.event_id,
                    TransitionDecision(value, reason, policy.policy_version))
            self._events[key] = event
            reason = "FIXTURE_RECORDED_NO_AUTHORIZATION"
        return InboxObservation(None,
            TransitionDecision(TransitionResult.HOLD, reason, policy.policy_version))

    # This tuple assumes source_system is a verified, namespaced identifier.
    # Different content/context under the same identity is HOLD, never overwritten.
    # Exact bytes are compared; no canonical JSON or integrity-chain claim is made.
