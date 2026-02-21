#!/usr/bin/env bash
set -euo pipefail

ROOT_DOMAIN="${ROOT_DOMAIN:-fc.danilloguimaraes.com.br}"
N8N_DOMAIN="${N8N_DOMAIN:-n8n.fc.danilloguimaraes.com.br}"
N8N_UPSTREAM_URL="${N8N_UPSTREAM_URL:-http://127.0.0.1:5678}"
HEALTHCHECK_RETRIES="${HEALTHCHECK_RETRIES:-12}"
HEALTHCHECK_DELAY_SECONDS="${HEALTHCHECK_DELAY_SECONDS:-5}"

check_http_once() {
  local url="$1"
  local label="$2"

  if curl -fsS -o /dev/null --max-time 10 "${url}"; then
    echo "[OK] ${label}: ${url}"
    return
  fi

  echo "[ERRO] ${label}: ${url}"
  exit 1
}

check_http_with_retry() {
  local url="$1"
  local label="$2"
  local attempt=1

  while [[ "${attempt}" -le "${HEALTHCHECK_RETRIES}" ]]; do
    if curl -fsS -o /dev/null --max-time 10 "${url}"; then
      echo "[OK] ${label}: ${url}"
      return
    fi

    if [[ "${attempt}" -eq "${HEALTHCHECK_RETRIES}" ]]; then
      echo "[ERRO] ${label}: ${url} (apos ${HEALTHCHECK_RETRIES} tentativas)"
      exit 1
    fi

    echo "[AGUARDANDO] ${label}: tentativa ${attempt}/${HEALTHCHECK_RETRIES}. Novo teste em ${HEALTHCHECK_DELAY_SECONDS}s..."
    sleep "${HEALTHCHECK_DELAY_SECONDS}"
    attempt=$((attempt + 1))
  done
}

echo "Validando Docker..."
docker ps >/dev/null

echo "Validando endpoints..."
check_http_with_retry "${N8N_UPSTREAM_URL}" "n8n local"
check_http_once "https://${ROOT_DOMAIN}" "dominio principal"
check_http_once "https://${N8N_DOMAIN}" "n8n publico"

echo "Healthcheck concluido."
