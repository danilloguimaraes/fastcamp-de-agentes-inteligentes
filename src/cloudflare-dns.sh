#!/usr/bin/env bash
set -euo pipefail

ROOT_DOMAIN="${ROOT_DOMAIN:-fc.danilloguimaraes.com.br}"
N8N_DOMAIN="${N8N_DOMAIN:-n8n.fc.danilloguimaraes.com.br}"
SERVER_IP="${SERVER_IP:-}"
CF_API_TOKEN="${CF_API_TOKEN:-}"
CF_ZONE_ID="${CF_ZONE_ID:-}"
CF_PROXIED="${CF_PROXIED:-false}"

if [[ -z "${SERVER_IP}" || -z "${CF_API_TOKEN}" || -z "${CF_ZONE_ID}" ]]; then
  echo "Defina SERVER_IP, CF_API_TOKEN e CF_ZONE_ID antes de executar."
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

assert_success() {
  local response="$1"
  python3 -c 'import json,sys; d=json.loads(sys.argv[1]); 
ok=d.get("success", False)
errs=d.get("errors", [])
print("" if ok else ("Cloudflare API erro: " + str(errs)))
sys.exit(0 if ok else 1)' "${response}"
}

upsert_a_record() {
  local name="$1"
  local proxied="$2"

  local list_response
  list_response="$(api GET "/zones/${CF_ZONE_ID}/dns_records?type=A&name=${name}")"
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
upsert_a_record "${ROOT_DOMAIN}" "${CF_PROXIED}"
upsert_a_record "${N8N_DOMAIN}" "${CF_PROXIED}"
echo "DNS Cloudflare concluido."
