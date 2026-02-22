#!/usr/bin/env bash
set -euo pipefail

ROOT_DOMAIN="${ROOT_DOMAIN:-fc.danilloguimaraes.com.br}"
N8N_DOMAIN="${N8N_DOMAIN:-n8n.fc.danilloguimaraes.com.br}"
WAHA_DOMAIN="${WAHA_DOMAIN:-waha.fc.danilloguimaraes.com.br}"
N8N_UPSTREAM_HOST="${N8N_UPSTREAM_HOST:-127.0.0.1}"
N8N_UPSTREAM_PORT="${N8N_UPSTREAM_PORT:-5678}"
WAHA_UPSTREAM_HOST="${WAHA_UPSTREAM_HOST:-127.0.0.1}"
WAHA_UPSTREAM_PORT="${WAHA_UPSTREAM_PORT:-3000}"
LETSENCRYPT_EMAIL="${LETSENCRYPT_EMAIL:-}"
CERT_RENEW_WINDOW_DAYS="${CERT_RENEW_WINDOW_DAYS:-30}"

if [[ ! -f /etc/os-release ]]; then
  echo "Nao foi possivel identificar o sistema operacional."
  exit 1
fi

source /etc/os-release
if [[ "${ID:-}" != "ubuntu" ]]; then
  echo "Este script suporta apenas Ubuntu."
  exit 1
fi

sudo_cmd() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

domain_cert_is_valid() {
  local domain="$1"
  local renew_window_seconds=$((CERT_RENEW_WINDOW_DAYS * 24 * 60 * 60))
  local cert_text

  cert_text="$(echo | sudo_cmd openssl s_client -connect 127.0.0.1:443 -servername "${domain}" 2>/dev/null | openssl x509 -noout -text 2>/dev/null || true)"
  if [[ -z "${cert_text}" ]]; then
    return 1
  fi

  if ! printf "%s" "${cert_text}" | sed -n '/Subject Alternative Name/,+1p' | tr -d ' ' | grep -q "DNS:${domain}\(,\|$\)"; then
    return 1
  fi

  if ! echo | sudo_cmd openssl s_client -connect 127.0.0.1:443 -servername "${domain}" 2>/dev/null | openssl x509 -noout -checkend "${renew_window_seconds}" >/dev/null 2>&1; then
    return 1
  fi

  return 0
}

echo "Instalando Nginx e Certbot..."
sudo_cmd apt-get update
sudo_cmd apt-get install -y nginx certbot python3-certbot-nginx

echo "Gerando configuracao de virtual hosts..."
NGINX_SITE_PATH="/etc/nginx/sites-available/fc-danillo"
sudo_cmd tee "${NGINX_SITE_PATH}" > /dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${ROOT_DOMAIN};

    location / {
        return 200 'fc online\n';
        add_header Content-Type text/plain;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name ${N8N_DOMAIN};

    client_max_body_size 20m;

    location / {
        proxy_pass http://${N8N_UPSTREAM_HOST}:${N8N_UPSTREAM_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_read_timeout 3600;
        proxy_send_timeout 3600;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name ${WAHA_DOMAIN};

    client_max_body_size 20m;

    location / {
        proxy_pass http://${WAHA_UPSTREAM_HOST}:${WAHA_UPSTREAM_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_read_timeout 3600;
        proxy_send_timeout 3600;
    }
}
EOF

if [[ -L /etc/nginx/sites-enabled/default ]]; then
  sudo_cmd rm -f /etc/nginx/sites-enabled/default
fi

if [[ ! -L /etc/nginx/sites-enabled/fc-danillo ]]; then
  sudo_cmd ln -s "${NGINX_SITE_PATH}" /etc/nginx/sites-enabled/fc-danillo
fi

echo "Validando e recarregando Nginx..."
sudo_cmd nginx -t
sudo_cmd systemctl enable nginx
sudo_cmd systemctl restart nginx

if [[ -n "${LETSENCRYPT_EMAIL}" ]]; then
  echo "Analisando validade dos certificados por dominio..."
  domains_to_issue=()
  for domain in "${ROOT_DOMAIN}" "${N8N_DOMAIN}" "${WAHA_DOMAIN}"; do
    if domain_cert_is_valid "${domain}"; then
      echo "- Certificado valido para ${domain} (sem renovacao por enquanto)"
    else
      echo "- Dominio ${domain} precisa de emissao/renovacao"
      domains_to_issue+=("${domain}")
    fi
  done

  if [[ "${#domains_to_issue[@]}" -gt 0 ]]; then
    echo "Emitindo/renovando certificado apenas para dominios necessarios..."
    certbot_args=(
      --nginx
      --non-interactive
      --agree-tos
      --email "${LETSENCRYPT_EMAIL}"
      --redirect
    )
    for domain in "${domains_to_issue[@]}"; do
      certbot_args+=(-d "${domain}")
    done
    sudo_cmd certbot "${certbot_args[@]}"
  else
    echo "Todos os dominios ja possuem certificado valido. Pulando certbot."
  fi
else
  echo "LETSENCRYPT_EMAIL nao definido. Pulando emissao de certificado."
  echo "Exemplo: LETSENCRYPT_EMAIL=voce@dominio.com ./setup-nginx.sh"
fi

echo
echo "Configuracao concluida."
echo "- Dominio principal: https://${ROOT_DOMAIN}"
echo "- n8n via proxy: https://${N8N_DOMAIN}"
echo "- WAHA via proxy: https://${WAHA_DOMAIN}"
echo
echo "Se usar Cloudflare com proxy laranja, deixe os registros em 'DNS only' durante a emissao inicial do certificado."
