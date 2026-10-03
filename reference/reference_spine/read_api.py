"""In-process read handlers only. No HTTP server, database, or vendor connection."""

from dataclasses import dataclass

from .authority import AuthorityConsentService
from .models import AuthorizationContext, AuthorizationDecision, PolicyConfig


@dataclass(frozen=True)
class ReadResponse:
    authorization: AuthorizationDecision
    data: None = None


class ReadAPI:
    def __init__(self, policy: PolicyConfig) -> None:
        self.policy = policy
        self.authority = AuthorityConsentService()

    def get(self, context: AuthorizationContext) -> ReadResponse:
        return ReadResponse(self.authority.evaluate(context, self.policy))

    # Intended routes: coordination, provenance, audit, historical state, conflicts,
    # responsibility timeline. No handler bypasses authority/purpose/consent checks.
