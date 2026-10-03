"""Show the default withheld read; does not start a server or save data."""

import json

from .models import AuthorizationContext, PolicyConfig
from .read_api import ReadAPI

context = AuthorizationContext(
    actor_id="fixture_patient", actor_role="PATIENT", organization="fixture_org",
    patient_ref="fixture_patient", purpose="patient_access",
    resource_type="CoordinationState", resource_id="fixture_episode",
    requested_action="READ",
)
response = ReadAPI(PolicyConfig()).get(context)
print(json.dumps({"status": "reference_scaffold", "decision": response.authorization.result,
                  "reason_code": response.authorization.reason_code, "data": response.data}))
