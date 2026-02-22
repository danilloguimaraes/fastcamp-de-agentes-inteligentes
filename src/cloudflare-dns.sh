#!/usr/bin/env bash
set -euo pipefail

ROOT_DOMAIN="${ROOT_DOMAIN:-fc.danilloguimaraes.com.br}"
N8N_DOMAIN="${N8N_DOMAIN:-n8n.fc.danilloguimaraes.com.br}"
SERVER_IP="${SERVER_IP:-}"
CF_API_TOKEN="${CF_API_TOKEN:-}"
CF_ZONE_ID="${CF_ZONE_ID:-}"
CF_PROXIED="${CF_PROXIED:-false}"
ROOT_CF_PROXIED="${ROOT_CF_PROXIED:-${CF_PROXIED}}"
N8N_CF_PROXIED="${N8N_CF_PROXIED:-${CF_PROXIED}}"

sanitize() {
  local v="$1"
  v="${v//$'\r'/}"
  v="${v//$'\n'/}"
  v="$(printf "%s" "${v}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

  if [[ ${#v} -ge 2 ]]; then
    local first="${v:0:1}"
    local last="${v: -1}"
    if [[ ("${first}" == '"' && "${last}" == '"') || ("${first}" == "'" && "${last}" == "'") ]]; then
      v="${v:1:${#v}-2}"
    fi
  fi

  printf "%s" "${v}"
}

ROOT_DOMAIN="$(sanitize "${ROOT_DOMAIN}")"
N8N_DOMAIN="$(sanitize "${N8N_DOMAIN}")"
SERVER_IP="$(sanitize "${SERVER_IP}")"
CF_API_TOKEN="$(sanitize "${CF_API_TOKEN}")"
CF_ZONE_ID="$(sanitize "${CF_ZONE_ID}")"
CF_PROXIED="$(sanitize "${CF_PROXIED}")"
ROOT_CF_PROXIED="$(sanitize "${ROOT_CF_PROXIED}")"
N8N_CF_PROXIED="$(sanitize "${N8N_CF_PROXIED}")"

if [[ -z "${SERVER_IP}" || -z "${CF_API_TOKEN}" || -z "${CF_ZONE_ID}" ]]; then
  if [[ -z "${SERVER_IP}" ]]; then
    SERVER_IP="$(curl -fsS --max-time 10 https://api.ipify.org || true)"
    SERVER_IP="$(sanitize "${SERVER_IP}")"
  fi
fi

if [[ -z "${SERVER_IP}" || -z "${CF_API_TOKEN}" || -z "${CF_ZONE_ID}" ]]; then
  echo "Defina SERVER_IP, CF_API_TOKEN e CF_ZONE_ID antes de executar. (SERVER_IP pode ser autodetectado pela api.ipify.org)"
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl nao encontrado."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 nao encontrado."
  exit 1
fi

api() {
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"

  if [[ -n "${data}" ]]; then
    curl -sS -X "${method}" "https://api.cloudflare.com/client/v4${endpoint}" \
      -H "Authorization: Bearer ${CF_API_TOKEN}" \
      -H "Content-Type: application/json" \
      --data "${data}"
    return
  fi

  curl -sS -X "${method}" "https://api.cloudflare.com/client/v4${endpoint}" \
    -H "Authorization: Bearer ${CF_API_TOKEN}" \
    -H "Content-Type: application/json"
}

api_get() {
  local endpoint="$1"
  shift
  local base_url="https://api.cloudflare.com/client/v4${endpoint}"
  local args=(
    -sS -X GET "${base_url}"
    -H "Authorization: Bearer ${CF_API_TOKEN}"
    -H "Content-Type: application/json"
  )

  if [[ $# -gt 0 ]]; then
    args+=(--get)
    while [[ $# -gt 0 ]]; do
      args+=(--data-urlencode "$1")
      shift
    done
  fi

  curl "${args[@]}"
}

assert_success() {
  local response="$1"
  python3 -c 'import json,sys
d=json.loads(sys.argv[1])
ok=d.get("success", False)
errs=d.get("errors", [])
if not ok:
    print("Cloudflare API erro: " + str(errs), file=sys.stderr)
    sys.exit(1)' "${response}"
}

resolve_zone_id() {
  local zone_input="$1"
  local zone_id_regex='^[a-fA-F0-9]{32}$'

  if [[ "${zone_input}" =~ ${zone_id_regex} ]]; then
    echo "${zone_input}"
    return
  fi

  local response
  response="$(api_get "/zones" "name=${zone_input}")"
  assert_success "${response}"

  local resolved
  resolved="$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); r=d.get("result", []); print(r[0]["id"] if r else "")' "${response}")"
  if [[ -z "${resolved}" ]]; then
    echo "Nao foi possivel resolver o zone id para '${zone_input}'." >&2
    exit 1
  fi

  echo "${resolved}"
}

upsert_a_record() {
  local name="$1"
  local proxied="$2"

  local list_response
  list_response="$(api_get "/zones/${CF_ZONE_ID}/dns_records" "type=A" "name=${name}")"
  assert_success "${list_response}"

  local record_id
  record_id="$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); r=d.get("result", []); print(r[0]["id"] if r else "")' "${list_response}")"

  local payload
  payload="$(python3 -c 'import json,sys; print(json.dumps({"type":"A","name":sys.argv[1],"content":sys.argv[2],"ttl":1,"proxied":sys.argv[3].lower()=="true"}))' "${name}" "${SERVER_IP}" "${proxied}")"

  local response
  if [[ -n "${record_id}" ]]; then
    response="$(api PUT "/zones/${CF_ZONE_ID}/dns_records/${record_id}" "${payload}")"
    assert_success "${response}"
    echo "Atualizado: ${name} -> ${SERVER_IP} (proxied=${proxied})"
    return
  fi

  response="$(api POST "/zones/${CF_ZONE_ID}/dns_records" "${payload}")"
  assert_success "${response}"
  echo "Criado: ${name} -> ${SERVER_IP} (proxied=${proxied})"
}

echo "Configurando DNS no Cloudflare..."
CF_ZONE_ID="$(resolve_zone_id "${CF_ZONE_ID}")"
upsert_a_record "${ROOT_DOMAIN}" "${ROOT_CF_PROXIED}"
upsert_a_record "${N8N_DOMAIN}" "${N8N_CF_PROXIED}"
echo "DNS Cloudflare concluido."
