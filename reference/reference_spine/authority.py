"""Fail-closed authority/consent stub. A policy version is never permission."""

from .models import (
    AuthorizationContext, AuthorizationDecision, AuthorizationResult,
    KNOWN_ROLES, PolicyConfig,
)


class AuthorityConsentService:
    def evaluate(
        self, context: AuthorizationContext, policy: PolicyConfig
    ) -> AuthorizationDecision:
        if not policy.policy_version:
            reason = "POLICY_UNRESOLVED"
        elif context.actor_role not in KNOWN_ROLES:
            reason = "AUTHORITY_UNRESOLVED"
        elif not all((context.actor_id, context.organization, context.patient_ref,
                      context.purpose, context.resource_id, context.requested_action)):
            reason = "AUTHORIZATION_CONTEXT_UNRESOLVED"
        else:
            reason = "AUTHORITY_CONSENT_EVALUATOR_UNIMPLEMENTED"
        return AuthorizationDecision(AuthorizationResult.HOLD, reason, policy.policy_version)
