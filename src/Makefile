MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
ENV_FILE := $(MAKEFILE_DIR).env
COMPOSE_FILE := $(MAKEFILE_DIR)docker-compose.yml

ifneq (,$(wildcard $(ENV_FILE)))
include $(ENV_FILE)
export
endif

.PHONY: deploy

deploy:
	docker compose -f "$(COMPOSE_FILE)" --env-file "$(ENV_FILE)" down -v
	docker compose -f "$(COMPOSE_FILE)" --env-file "$(ENV_FILE)" up -d