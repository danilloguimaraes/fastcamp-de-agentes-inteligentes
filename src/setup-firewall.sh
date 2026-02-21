#!/usr/bin/env bash
set -euo pipefail

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

echo "Instalando e configurando UFW..."
sudo_cmd apt-get update
sudo_cmd apt-get install -y ufw

sudo_cmd ufw allow OpenSSH
sudo_cmd ufw allow 80/tcp
sudo_cmd ufw allow 443/tcp
sudo_cmd ufw --force enable
sudo_cmd ufw status verbose
