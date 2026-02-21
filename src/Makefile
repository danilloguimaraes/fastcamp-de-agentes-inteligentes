ifneq (,$(wildcard .env))
include .env
export
endif

deploy:
	docker compose down -v && docker compose up -d