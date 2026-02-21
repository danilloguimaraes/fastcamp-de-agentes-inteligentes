#!/usr/bin/env bash
set -euo pipefail

ROOT_DOMAIN="${ROOT_DOMAIN:-fc.danilloguimaraes.com.br}"
N8N_DOMAIN="${N8N_DOMAIN:-n8n.fc.danilloguimaraes.com.br}"
N8N_UPSTREAM_URL="${N8N_UPSTREAM_URL:-http://127.0.0.1:5678}"

check_http() {
  local url="$1"
  local label="$2"

  if curl -fsS -o /dev/null --max-time 10 "${url}"; then
    echo "[OK] ${label}: ${url}"
    return
  fi

  echo "[ERRO] ${label}: ${url}"
  exit 1
}

echo "Validando Docker..."
docker ps >/dev/null

echo "Validando endpoints..."
check_http "${N8N_UPSTREAM_URL}" "n8n local"
check_http "https://${ROOT_DOMAIN}" "dominio principal"
check_http "https://${N8N_DOMAIN}" "n8n publico"

echo "Healthcheck concluido."
