MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
ENV_FILE := $(MAKEFILE_DIR).env
COMPOSE_FILE := $(MAKEFILE_DIR)docker-compose.yml

ifneq (,$(wildcard $(ENV_FILE)))
include $(ENV_FILE)
export
endif

.PHONY: deploy setup-nginx setup-firewall healthcheck validate-final cloudflare-dns-gray cloudflare-dns-orange bootstrap bootstrap-complete

deploy:
	docker compose -f "$(COMPOSE_FILE)" --env-file "$(ENV_FILE)" down -v
	docker compose -f "$(COMPOSE_FILE)" --env-file "$(ENV_FILE)" up -d

setup-nginx:
	chmod +x "$(MAKEFILE_DIR)setup-nginx.sh"
	LETSENCRYPT_EMAIL="$(LETSENCRYPT_EMAIL)" ROOT_DOMAIN="$(ROOT_DOMAIN)" N8N_DOMAIN="$(N8N_DOMAIN)" "$(MAKEFILE_DIR)setup-nginx.sh"

setup-firewall:
	chmod +x "$(MAKEFILE_DIR)setup-firewall.sh"
	"$(MAKEFILE_DIR)setup-firewall.sh"

healthcheck:
	chmod +x "$(MAKEFILE_DIR)healthcheck.sh"
	ROOT_DOMAIN="$(ROOT_DOMAIN)" N8N_DOMAIN="$(N8N_DOMAIN)" "$(MAKEFILE_DIR)healthcheck.sh"

validate-final:
	chmod +x "$(MAKEFILE_DIR)validate-final.sh"
	ROOT_DOMAIN="$(ROOT_DOMAIN)" N8N_DOMAIN="$(N8N_DOMAIN)" "$(MAKEFILE_DIR)validate-final.sh"

cloudflare-dns-gray:
	chmod +x "$(MAKEFILE_DIR)cloudflare-dns.sh"
	CF_API_TOKEN="$(CF_API_TOKEN)" CF_ZONE_ID="$(CF_ZONE_ID)" SERVER_IP="$(SERVER_IP)" ROOT_DOMAIN="$(ROOT_DOMAIN)" N8N_DOMAIN="$(N8N_DOMAIN)" CF_PROXIED=false "$(MAKEFILE_DIR)cloudflare-dns.sh"

cloudflare-dns-orange:
	chmod +x "$(MAKEFILE_DIR)cloudflare-dns.sh"
	CF_API_TOKEN="$(CF_API_TOKEN)" CF_ZONE_ID="$(CF_ZONE_ID)" SERVER_IP="$(SERVER_IP)" ROOT_DOMAIN="$(ROOT_DOMAIN)" N8N_DOMAIN="$(N8N_DOMAIN)" CF_PROXIED=true "$(MAKEFILE_DIR)cloudflare-dns.sh"

bootstrap:
	$(MAKE) cloudflare-dns-gray
	$(MAKE) deploy
	$(MAKE) setup-nginx
	$(MAKE) setup-firewall
	$(MAKE) healthcheck

bootstrap-complete:
	$(MAKE) bootstrap
	$(MAKE) cloudflare-dns-orange
	$(MAKE) validate-final