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
- Atualize o arquivo `src/.env` com:
- `SERVER_IP` (IP público da VM)
- `LETSENCRYPT_EMAIL`
- `CF_API_TOKEN` e `CF_ZONE_ID` (Cloudflare)
- Execução automatizada (Cloudflare DNS cinza + deploy + Nginx/SSL + UFW + healthcheck):
- `cd src && make bootstrap`
- Após SSL emitido, habilite proxy laranja no Cloudflare:
- `cd src && make cloudflare-dns-orange`
