<div align="center">

# 🎯 AI Job Matcher Pro

### Agente Autônomo de Recrutamento com Inteligência Artificial

<br>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-1.2-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.12-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://pydantic.dev)

<br>

[![CI Status](https://img.shields.io/github/actions/workflow/status/tmemelli/ai-job-matcher/ci.yml?branch=main&style=flat-square&label=CI%20Pipeline)](https://github.com/tmemelli/ai-job-matcher/actions)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](http://makeapullrequest.com)

<br>

**Um recrutador sênior digital que não apenas lê currículos — ele investiga, valida e prepara entrevistas.**

[Demonstração](#-demonstração) •
[Instalação](#-instalação) •
[Arquitetura](#-arquitetura) •
[Como Funciona](#-como-funciona) •
[Roadmap](#-roadmap)

</div>

> **🔐 Credenciais de Acesso (Live Demo):**
> Para testar a aplicação online, utilize a senha: **`visitante`**

---

## 💡 O Problema

Recrutadores gastam em média **23 horas por semana** triturando currículos. A maioria das ferramentas de ATS apenas faz *keyword matching* — uma abordagem rasa que perde nuances cruciais como:

- Um desenvolvedor Python pode não ter "FastAPI" no currículo, mas ter 3 anos construindo APIs REST
- Senioridade em uma área **não transfere** automaticamente para outra
- Perfis no LinkedIn e GitHub contam histórias que o PDF não conta

---

## 🚀 A Solução

O **AI Job Matcher Pro** opera como um agente autônomo com múltiplas ferramentas. Ele não apenas analisa — ele **investiga ativamente**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   📄 CV (PDF)  ──►  🤖 AGENTE  ──►  🔍 GitHub API  ──►  🌐 Web Search      │
│                         │                                                   │
│                         ▼                                                   │
│              ┌──────────────────────┐                                       │
│              │   GPT-4o Analysis    │                                       │
│              │  • Match Score       │                                       │
│              │  • Gap Analysis      │                                       │
│              │  • Seniority Check   │                                       │
│              │  • Interview Prep    │                                       │
│              └──────────────────────┘                                       │
│                         │                                                   │
│                         ▼                                                   │
│              📊 Relatório Executivo                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🎯 Match Score Contextual
Vai além de keywords. Analisa **contexto semântico** entre requisitos da vaga e experiência real do candidato.

### 🔬 Validação Multi-Source
```python
# O agente executa automaticamente:
github_data = fetch_github_profile(username)     # Repos, stars, linguagens
web_results = search_candidate_online(name)      # LinkedIn, artigos, portfólio
```

### 📊 Análise de Senioridade Contextual
> **Insight crítico:** Um Arquiteto de Software Sênior aplicando para Chef de Cozinha é um **iniciante** naquela vaga.

O sistema distingue:
- `job_required_seniority` — O que a vaga pede
- `candidate_seniority_for_job` — Nível real do candidato **para aquela posição específica**

### 🎤 Gerador de Entrevistas
Cria perguntas técnicas e comportamentais personalizadas baseadas nos **gaps identificados**:

```python
class InterviewQuestion(BaseModel):
    question: str                    # A pergunta
    expected_answer_topic: str       # O que esperar na resposta
    difficulty: str                  # Fácil | Médio | Difícil
```

### 🛡️ Arsenal Técnico Completo
Detecta **todas** as tecnologias do candidato, não apenas as que a vaga pede — útil para descobrir potencial oculto.

---

## 🖼️ Demonstração

<div align="center">

| Dashboard Principal | Análise de Gaps |
|:---:|:---:|
| ![Dashboard](https://via.placeholder.com/400x300/1a1a2e/eaeaea?text=Dashboard+Principal) | ![Gaps](https://via.placeholder.com/400x300/16213e/eaeaea?text=Gap+Analysis) |

| Modo Entrevista | Presença Online |
|:---:|:---:|
| ![Interview](https://via.placeholder.com/400x300/0f3460/eaeaea?text=Interview+Mode) | ![Web](https://via.placeholder.com/400x300/533483/eaeaea?text=Web+Presence) |

</div>

> 📸 *Substitua pelos screenshots reais do seu projeto*

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Propósito |
|--------|------------|-----------|
| **LLM** | OpenAI GPT-4o | Análise contextual e geração de insights |
| **Orquestração** | LangChain Core | Composição de tools e chains |
| **Validação** | Pydantic v2 | Structured Outputs com type safety |
| **Interface** | Streamlit | Dashboard interativo |
| **Tools** | DuckDuckGo Search | OSINT para validação de presença online |
| **APIs** | GitHub REST API | Análise de repositórios e atividade |
| **PDF** | pypdf | Extração de texto de currículos |
| **CI/CD** | GitHub Actions | Smoke tests automatizados |

---

## 📦 Instalação

### Pré-requisitos

- Python 3.11+
- Chave de API da OpenAI

### Quick Start

```bash
# 1. Clone o repositório
git clone https://github.com/tmemelli/ai-job-matcher.git
cd ai-job-matcher

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: .\venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais
```

### Configuração do `.env`

```env
# Obrigatório
OPENAI_API_KEY=sk-your-key-here

# Opcional: modelo (default: gpt-4o-2024-08-06)
OPENAI_MODEL=gpt-4o-2024-08-06

# Senha de acesso (Defina a senha que preferir para seu ambiente local)
APP_PASSWORD=1234
```

### Executar

```bash
streamlit run src/app.py
```

Acesse: `http://localhost:8501`

---

## 🏗️ Arquitetura

```
ai-job-matcher/
│
├── 📂 .github/
│   └── workflows/
│       └── ci.yml              # Pipeline de integração contínua
│
├── 📂 src/
│   ├── __init__.py
│   ├── agent.py                # 🧠 Cérebro: orquestração e análise LLM
│   ├── tools.py                # 🔧 Ferramentas: GitHub API + Web Search
│   └── app.py                  # 🖥️ Interface: Dashboard Streamlit
│
├── 📂 data/
│   └── resume.pdf              # Exemplo de currículo para testes
│
├── .env                        # Variáveis de ambiente (não commitado)
├── .env.example                # Template de configuração
├── .gitignore
├── requirements.txt
└── README.md
```

### Fluxo de Dados

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│   app.py   │────►│  agent.py  │────►│  tools.py  │
│            │     │            │     │            │
│ • Upload   │     │ • Extract  │     │ • GitHub   │
│ • Display  │     │ • Analyze  │     │ • Search   │
│ • Interact │     │ • Generate │     │            │
└────────────┘     └────────────┘     └────────────┘
      │                  │                  │
      │                  ▼                  │
      │           ┌────────────┐            │
      │           │  OpenAI    │            │
      └──────────►│  GPT-4o    │◄───────────┘
                  │            │
                  │ Structured │
                  │  Outputs   │
                  └────────────┘
```

---

## 🔍 Como Funciona

### 1. Extração de Identidade
```python
# Fase 1: GPT-4o-mini extrai nome e GitHub do CV
identity = {"name": "João Silva", "github": "joaosilva"}
```

### 2. Coleta Multi-Source
```python
# Fase 2: Tools buscam dados externos
github_data = fetch_github_profile("joaosilva")
web_data = search_candidate_online("João Silva")
```

### 3. Análise Contextual Profunda
```python
# Fase 3: GPT-4o analisa tudo com Structured Outputs
result: CandidateAnalysis = analyze_candidate_with_tools(
    cv_text=cv,
    job_description=job,
    company_name="TechCorp"
)
```

### 4. Output Estruturado
```python
class CandidateAnalysis(BaseModel):
    candidate_name: str
    github_username: Optional[str]
    match_score: int                      # 0-100
    match_analysis: str
    missing_skills: List[str]
    detected_hard_skills: List[str]       # Arsenal completo
    job_required_seniority: str
    candidate_seniority_for_job: str      # Contextual!
    web_presence_analysis: str
    interview_questions: List[InterviewQuestion]
    skills: SkillSet
```

---

## 🧪 Testes e CI/CD

O projeto usa GitHub Actions para garantir qualidade:

```yaml
# .github/workflows/ci.yml
- name: 🧪 Smoke Test
  run: |
    python -c "from src.agent import analyze_candidate_with_tools; print('✅ Agent OK')"
    python -c "from src.tools import search_candidate_online; print('✅ Tools OK')"
```

A cada push na `main`:
1. ✅ Setup do ambiente Python 3.11
2. ✅ Instalação de dependências
3. ✅ Smoke tests nos módulos críticos

---

## 🗺️ Roadmap

### v1.0 (Atual)
- [x] Análise de CV via GPT-4o
- [x] Integração GitHub API
- [x] Web Search (DuckDuckGo)
- [x] Gerador de perguntas de entrevista
- [x] Dashboard Streamlit
- [x] CI/CD básico

### v1.1 (Próximo)
- [ ] Suporte a múltiplos candidatos (batch)
- [ ] Export PDF do relatório
- [ ] Histórico de análises (SQLite)
- [ ] Rate limiting para APIs

### v2.0 (Futuro)
- [ ] RAG com base de vagas anteriores
- [ ] Integração LinkedIn API (OAuth)
- [ ] Multi-tenant com autenticação
- [ ] Deploy em cloud (Railway/Render)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---

<div align="center">

### Desenvolvido com 🧡 por Thiago Memelli

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/thiagomemelli/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/tmemelli)

<br>

⭐ **Se este projeto te ajudou, deixe uma estrela!** ⭐

</div>
