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

### 6 - Prática: Embedding (II)
- [How to Get Started With Qdrant Cloud](https://qdrant.tech/documentation/cloud-quickstart/)
    - What is QDrant? Qdrant is an AI-native vector database for iterating on high-dimensional (embbedings) vectors efficiently. 
    - What is its purpose? Its primary purpose is to enable semantic search and similarity-based retrieval at scale.
    - Why Vector Databases Exist? Traditional databases index structured fields (text, numbers, dates). Modern AI systems generate embeddings (dense numerical vectors representing meaning). Example: A sentence transformed into a 768-dimensional vector or an image transformed into a 512-dimensional vector. You don’t search these with SQL equality. You search them using nearest-neighbor similarity.
    - While dense vectors excel at capturing context, they can sometimes miss specific technical terms or unique identifiers. To bridge this gap, Qdrant also utilizes sparse vectors designed to capture precise lexical matches for specific keywords. Learn more in this guide.
    - Additional source: https://qdrant.tech/documentation/overview/

That is where Qdrant fits.
- [n8n AI Agents with Qdrant Vector Store Knowledge Base](https://www.youtube.com/watch?v=cCDAY0nb0T0)

### 7 - Leitura: n8n (II)
- [Introducing the Self-hosted AI Starter Kit: Run AI locally for privacy-first solutions](https://blog.n8n.io/self-hosted-ai/)
- [What You Need to Know Before Using It](https://autogpt.net/ai-tool/n8n/)

### 8 - Pratica: Agentes com Google ADK (III)
- [How To Get Your FREE Google Gemini API Key](https://www.youtube.com/watch?v=6BRyynZkvf0)
  - Aprende-se como gerar uma apikey do gemini api.  
- [Quickstart Google ADK](https://google.github.io/adk-docs/get-started/quickstart/)
  - Ensina a construir uma estrutura para adequar um projeto de agentes utilizando o adk. 
  - ADK é um framework projetado para facilitar o desenvolviemnto de aplicações que utilizam LLMs. 
  - O que mais vimos 
    - Tool Definition & Usage: Python functions (tools) that grant agents specific abilities (like fetching data) and instructing agents on how to use them effectively.
    - Multi-LLM Flexibility: Configuring agents to utilize various leading LLMs (Gemini, GPT-4o, Claude Sonnet) via LiteLLM integration, allowing you to choose the best model for each task. 
    - Agent Delegation & Collaboration:  Designing specialized sub-agents and enabling automatic routing (auto flow) of user requests to the most appropriate agent within a team. 
    - Session State for Memory: Utilizing Session State and ToolContext to enable agents to remember information across conversational turns, leading to more contextual interactions.
    - Safety Guardrails with Callbacks: Implementing before_model_callback and before_tool_callback to inspect, modify, or block requests/tool usage based on predefined rules, enhancing application safety and control.

- [Construa sua primeira equipe de agentes inteligentes: um bot meteorológico progressivo com ADK](https://google.github.io/adk-docs/tutorials/agent-team/)
- [Kit de Desenvolvimento de Agentes](https://google.github.io/adk-docs/)

## Atividades do curso
As atividades dos cards estão disponíveis no diretório [atividades_aulas](./atividades_aulas/)

## Projeto
O código fonte do projeto está disponível no diretório [src](./src/)