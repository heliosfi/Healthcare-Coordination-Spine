"""Separate authorization, transition, identity, and governance vocabularies."""

from dataclasses import dataclass
from enum import Enum


class AuthorizationResult(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    HOLD = "HOLD"


class TransitionResult(str, Enum):
    PROMOTE = "PROMOTE"
    REJECT = "REJECT"
    HOLD = "HOLD"


class GuardOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class PolicyConfig:
    policy_version: str | None = None
    retention_policy_version: str | None = None


@dataclass(frozen=True)
class AuthorizationContext:
    actor_id: str
    actor_role: str
    organization: str
    patient_ref: str
    purpose: str
    resource_type: str
    resource_id: str
    requested_action: str
    source_authority: str | None = None
    consent_ref: str | None = None
    workflow_id: str | None = None


@dataclass(frozen=True)
class AuthorizationDecision:
    result: AuthorizationResult
    reason_code: str
    policy_version: str | None


@dataclass(frozen=True)
class TransitionDecision:
    result: TransitionResult
    reason_code: str
    policy_version: str | None
    state_changed: bool = False


@dataclass(frozen=True)
class SourceEvent:
    event_id: str
    coordination_id: str
    source_system: str
    source_event_id: str
    event_type: str
    payload: bytes
    synthetic: bool = False


@dataclass(frozen=True)
class ConflictEvidence:
    """Already-attributed, comparable evidence; not a source-identity validator."""

    conflict_id: str
    current_event_ref: str
    incoming_event_ref: str
    authority_basis_refs: tuple[str, ...]


@dataclass(frozen=True)
class AttemptRecord:
    decision: TransitionDecision
    conflicts: tuple[ConflictEvidence, ...]
    promotion_blocked: bool


GUARD_NAMES = tuple(f"G{i}" for i in range(1, 11))
KNOWN_ROLES = frozenset({"PATIENT", "PRESCRIBER", "PHARMACY", "PAYER", "SPINE"})
