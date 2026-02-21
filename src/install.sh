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

echo "Atualizando pacotes e instalando dependencias..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release make

echo "Configurando chave GPG e repositorio oficial do Docker..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Instalando Docker Engine e Docker Compose..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

TARGET_USER="${SUDO_USER:-$USER}"
if [[ "${TARGET_USER}" != "root" ]]; then
  echo "Adicionando usuario '${TARGET_USER}' ao grupo docker..."
  sudo usermod -aG docker "${TARGET_USER}"
fi

echo
echo "Instalacao concluida."
docker --version || true
docker compose version || true
echo
echo "Se o comando docker pedir permissao, faca logout/login antes de usar."
