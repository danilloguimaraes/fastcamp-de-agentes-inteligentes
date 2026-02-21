#!/usr/bin/env bash
set -euo pipefail

ROOT_DOMAIN="${ROOT_DOMAIN:-fc.danilloguimaraes.com.br}"
N8N_DOMAIN="${N8N_DOMAIN:-n8n.fc.danilloguimaraes.com.br}"
N8N_UPSTREAM_URL="${N8N_UPSTREAM_URL:-http://127.0.0.1:5678}"
VALIDATE_RETRIES="${VALIDATE_RETRIES:-12}"
VALIDATE_DELAY_SECONDS="${VALIDATE_DELAY_SECONDS:-5}"

check_http_with_retry() {
  local url="$1"
  local label="$2"
  local attempt=1

  while [[ "${attempt}" -le "${VALIDATE_RETRIES}" ]]; do
    if curl -fsS -o /dev/null --max-time 10 "${url}"; then
      echo "[OK] ${label}: ${url}"
      return
    fi

    if [[ "${attempt}" -eq "${VALIDATE_RETRIES}" ]]; then
      echo "[ERRO] ${label}: ${url} (apos ${VALIDATE_RETRIES} tentativas)"
      exit 1
    fi

    echo "[AGUARDANDO] ${label}: tentativa ${attempt}/${VALIDATE_RETRIES}. Novo teste em ${VALIDATE_DELAY_SECONDS}s..."
    sleep "${VALIDATE_DELAY_SECONDS}"
    attempt=$((attempt + 1))
  done
}

echo "Containers do projeto:"
docker compose ps

echo "Validando endpoints finais..."
check_http_with_retry "${N8N_UPSTREAM_URL}" "n8n local"
check_http_with_retry "https://${ROOT_DOMAIN}" "dominio principal"
check_http_with_retry "https://${N8N_DOMAIN}" "n8n publico"

echo "Validacao final concluida."
