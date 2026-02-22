# Fastcamp
## Material

### 1 - Vídeo: Fundamentos de Agentes de IA (I)
- [What are AI Agents?](https://www.youtube.com/watch?v=F8NKVhkZZWI)
- [Andrew Ng Explores The Rise Of AI Agents And Agentic Reasoning | BUILD 2024 Keynote](https://www.youtube.com/watch?v=KrRD7r7y7NY)

### 2 - Prática: Python: Criando um ReAct Agent do Zero (I)
- [Python: Create a ReAct Agent from Scratch](https://www.youtube.com/watch?v=hKVhRA9kfeM)

### 3 - Prática: Validação de dados com Pydantic (I)
- [Why Python Needs Pydantic for Real Applications](https://www.youtube.com/watch?v=502XOB0u8OY&t=46s)

### 4 - Vídeo: Introdução ao n8n (II)
- [n8n no Docker em 6 minutos](https://www.youtube.com/watch?v=CAedO3UaiU8) -
- [n8n - The very quick quickstart](https://docs.n8n.io/try-it-out/quickstart/)
- [n8n - Your first workflow](https://docs.n8n.io/try-it-out/tutorial-first-workflow/)
- [n8n - Starting with Docker instalation](https://docs.n8n.io/hosting/installation/docker/#starting-n8n)

### 5 - Prática: Construindo um fluxo n8n(II)
- [N8N + WhatsApp](https://www.youtube.com/watch?v=FyQivMjb3_8)
- [Waha - Install & Update](https://waha.devlike.pro/docs/how-to/install/)
- [How to make an AI chatbot: A step-by-step guide](https://blog.n8n.io/how-to-make-ai-chatbot/)

## Atividades do curso
As atividades dos cards estão disponíveis no diretório [atividades_aulas](./atividades_aulas/)

## Projeto
O código fonte do projeto está disponível no diretório [src](./src/)

### Deploy n8n com Nginx + domínio
- Use sempre o diretório desejado no servidor (exemplo):
- `cd /root/workspace/fastcamp-de-agentes-inteligentes/src`

- Configure o arquivo `.env` com:
- `ROOT_DOMAIN=fc.danilloguimaraes.com.br`
- `N8N_DOMAIN=n8n.fc.danilloguimaraes.com.br`
- `WAHA_DOMAIN=waha.fc.danilloguimaraes.com.br`
- `N8N_PORT=5678` (porta interna do container)
- `N8N_EDITOR_BASE_URL=https://n8n.fc.danilloguimaraes.com.br/`
- `WAHA_API_KEY=<sua-chave-waha>`
- `WAHA_MEDIA_STORAGE=POSTGRESQL`
- `WAHA_MEDIA_POSTGRESQL_URL=postgres://n8n:n8n@postgres:5432/n8n?sslmode=disable`
- `SERVER_IP=<ip-publico-da-vm>`
- `LETSENCRYPT_EMAIL=<seu-email>`
- `CF_API_TOKEN=<token-cloudflare-com-zone-dns-edit>`
- `CF_ZONE_ID=danilloguimaraes.com.br` (ou o Zone ID em formato UUID)

- Fluxo automatizado (DNS cinza + deploy + Nginx/SSL + UFW + healthcheck):
- `make bootstrap`
- O `deploy` padrao preserva volumes para evitar startup lento em toda execucao.
- Para reset completo de dados (Postgres/n8n), use `make deploy-reset`.
- Esse passo cria/atualiza dois registros no Cloudflare:
- `fc.danilloguimaraes.com.br`
- `n8n.fc.danilloguimaraes.com.br`
- `waha.fc.danilloguimaraes.com.br`

- Depois de emitir o certificado SSL, habilite o proxy laranja de forma segura:
- `make cloudflare-dns-orange-safe`
- Isso deixa `fc.danilloguimaraes.com.br` em laranja e `n8n.fc.danilloguimaraes.com.br`/`waha.fc.danilloguimaraes.com.br` em cinza.
- Motivo: o wildcard SSL universal da Cloudflare nao cobre `n8n.fc.*` e `waha.fc.*` sem certificado avancado.
- Se voce ja tiver certificado Cloudflare que cubra `*.fc.danilloguimaraes.com.br`, use:
- `make cloudflare-dns-orange-all`

- Fluxo completo em um comando (inclui proxy laranja seguro ao final):
- `make bootstrap-complete`
- Esse fluxo agora executa validação final automática (`docker compose ps` + checks HTTP).
- O setup do Nginx executa certbot por dominio (independente) com `--keep-until-expiring`, evitando renovacao desnecessaria e prompt interativo.

- Se quiser validar manualmente:
- `make healthcheck`
- `HEALTHCHECK_RETRIES=60 HEALTHCHECK_DELAY_SECONDS=5 make healthcheck`
- `make validate-final`
- `VALIDATE_RETRIES=24 VALIDATE_DELAY_SECONDS=5 make validate-final`
- Quando `SERVER_IP` estiver definido, os checks HTTPS usam `--resolve` para validar a origem e evitar falso negativo por propagacao/DNS do Cloudflare.

- Segurança:
- após concluir a configuração, revogue o token Cloudflare usado no bootstrap e gere um novo token.
