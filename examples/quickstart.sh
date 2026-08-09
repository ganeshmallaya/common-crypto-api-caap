#!/bin/sh
set -eu

api_url="${CAAP_API_URL:-http://127.0.0.1:8080}"
auth_header=""
if [ -n "${CAAP_AUTH_TOKEN:-}" ]; then
  auth_header="Authorization: Bearer ${CAAP_AUTH_TOKEN}"
fi

post_json() {
  path="$1"
  body="$2"
  if [ -n "$auth_header" ]; then
    curl --fail-with-body --silent --show-error -H 'Content-Type: application/json' -H "$auth_header" -d "$body" "$api_url$path"
  else
    curl --fail-with-body --silent --show-error -H 'Content-Type: application/json' -d "$body" "$api_url$path"
  fi
}

create_body="$(sed 's/example-create-0001/example-create-'"$$"'/' "$(dirname "$0")/create-key.example.json")"
create_response="$(post_json /v1/keys "$create_body")"
key_ref="$(printf '%s' "$create_response" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["keyRef"])')"
message="cmVsZWFzZSBhcnRpZmFjdA"
sign_body="{\"apiVersion\":\"0.2.0-draft\",\"requestId\":\"example-sign-$$\",\"operation\":\"Sign\",\"intent\":\"artifact-signing\",\"expectedPolicy\":{\"profileId\":\"baseline-artifact-signing\",\"profileVersion\":\"1\"},\"minimumConstraints\":{\"profile\":\"artifact-signing-v0\",\"providerClasses\":[\"software\"]},\"input\":{\"keyRef\":\"$key_ref\",\"message\":\"$message\"}}"
sign_response="$(post_json /v1/sign "$sign_body")"
signature="$(printf '%s' "$sign_response" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["signature"])')"
verify_body="{\"apiVersion\":\"0.2.0-draft\",\"requestId\":\"example-verify-$$\",\"operation\":\"Verify\",\"intent\":\"artifact-signing\",\"expectedPolicy\":{\"profileId\":\"baseline-artifact-signing\",\"profileVersion\":\"1\"},\"minimumConstraints\":{\"profile\":\"artifact-signing-v0\",\"providerClasses\":[\"software\"]},\"input\":{\"keyRef\":\"$key_ref\",\"message\":\"$message\",\"signature\":\"$signature\"}}"
post_json /v1/verify "$verify_body"
printf '\n'
