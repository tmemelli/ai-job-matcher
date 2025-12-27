<div align="center">

# 🎯 AI Job Matcher Pro

### Agente Autônomo de Recrutamento com Inteligência Artificial

<br>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.12-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://pydantic.dev)

<br>

[![CI Status](https://img.shields.io/github/actions/workflow/status/tmemelli/ai-job-matcher/ci.yml?branch=main&style=flat-square&label=CI%20Pipeline)](https://github.com/tmemelli/ai-job-matcher/actions)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](http://makeapullrequest.com)

<br>

**Um recrutador sênior digital que não apenas lê currículos — ele investiga, valida e prepara entrevistas.**

[Demonstração](#️-demonstração-da-aplicação) •
[Instalação](#-instalação) •
[Arquitetura](#️-arquitetura) •
[Como Funciona](#-como-funciona) •
[Roadmap](#️-roadmap)

</div>

> **🔐 Credenciais de Acesso (Live Demo):**
### 🔴 [CLIQUE AQUI PARA TESTAR AO VIVO](https://ai-job-matcher-thiago-memelli.streamlit.app) 🔴
**(Senha de Acesso: `visitante`)**

---

## 💡 O Problema

Recrutadores gastam em média **23 horas por semana** triturando currículos. A maioria das ferramentas de ATS apenas faz *keyword matching* — uma abordagem rasa que falha em:

- **Distinguir Senioridade:** Um "Sênior" em Data Science pode ser "Júnior" em DevOps.
- **Validar Presença:** Não verificam se o GitHub ou Portfólio citados realmente sustentam o que está no PDF.
- **Contexto:** Perdem candidatos ótimos que usam sinônimos para as tecnologias pedidas.

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

## 🖼️ Demonstração da Aplicação

Visão geral das principais funcionalidades do sistema:

<div align="center">

| Dashboard Executivo | Análise de Gaps |
|:---:|:---:|
| ![Dashboard Principal](assets/dashboard.png) | ![Análise de Gaps](assets/gaps.png) |
| *Score de compatibilidade e Senioridade* | *Identificação visual de skills faltantes* |

| Modo Entrevista | Acesso Seguro |
|:---:|:---:|
| ![Perguntas de Entrevista](assets/interview.png) | ![Tela de Login](assets/login.png) |
| *Perguntas técnicas geradas por IA* | *Controle de acesso para recrutadores* |

</div>

---

## 🧪 Estudo de Caso Real: Vaga ilegra vs. Candidato

Para validar a precisão do agente, submetemos o sistema a um teste cego com uma vaga real e competitiva.

**1. O Cenário (Vaga LinkedIn)**
* **Empresa:** ilegra
* **Cargo:** Python Developer (Sênior)
* **Stack Exigida:** Python, AWS (Lambda, DynamoDB), Docker, Terraform.

**2. A Análise do Agente**
O sistema processou o currículo contra a vaga e gerou os seguintes insights (baseados nos prints acima):

* **✅ Match Score: 85%**
    * O agente identificou uma alta compatibilidade. Diferente de um ATS comum que poderia descartar o candidato por falta de palavras-chave exatas de infraestrutura, a IA entendeu que a base sólida de Engenharia de Software (Clean Arch, TDD, SOLID) sustentava o nível **Sênior**.
* **🎯 Validação de Senioridade**
    * **Vaga Pede:** Sênior
    * **Candidato:** Validado como **Sênior** pelo agente (não houve rebaixamento de nível, apesar dos gaps).
* **⚠️ Identificação de Gaps Precisos**
    * O sistema alertou especificamente: *"Falta experiência explícita com AWS (Lambda, API Gateway, DynamoDB)"* e *"Forte vivência com Terraform"*. Isso direciona o recrutador para investigar o quanto o candidato estaria disposto a aprender essas ferramentas.
* **🎤 Perguntas Geradas**
    * Para mitigar o risco, o agente gerou uma pergunta técnica difícil sobre *"Desafios em projetos Serverless"*, permitindo validar se o candidato tem conceitos teóricos mesmo sem a prática da ferramenta específica.

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Propósito |
|--------|------------|-----------|
| **LLM** | OpenAI GPT-4o | Análise contextual e geração de insights |
| **Orquestração** | LangChain Core | Composição de tools e chains |
| **Validação** | Pydantic v2 | Structured Outputs com type safety |
| **Interface** | Streamlit | Dashboard interativo |
| **Tools** | Tavily + DuckDuckGo | Busca web com fallback |
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

# Opcional: chave API Tavily para busca web (se aplicável)
TAVILY_API_KEY=your-tavily-api-key-here
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
- name: ✅ Verificar imports
- name: 🧪 Verificar sintaxe  
- name: 📄 Testar extração de PDF
- name: 🐙 Testar GitHub API
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
- [x] Web Search (Tavily + DuckDuckGo)
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

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais informações.
---

## 🙏 Agradecimentos

- **Streamlit** - Pela capacidade de criar dashboards interativos em minutos
- **OpenAI** - Pelos modelos GPT-4o que dão vida à inteligência do agente
- **Pydantic** - Pela validação rigorosa de dados e *Structured Outputs*
- **Tavily** - Pela API de busca otimizada para agentes de IA
- **PyPDF** - Pela extração eficiente de dados de arquivos PDF

---

## 📞 Contato & Suporte

Se você é um **recrutador** ou **hiring manager** procurando um desenvolvedor que une Engenharia de Software com Inteligência Artificial:

📧 **Email**: [tmemelli@gmail.com](mailto:tmemelli@gmail.com)
💼 **LinkedIn**: [https://www.linkedin.com/in/thiagomemelli/](https://www.linkedin.com/in/thiagomemelli/)
📱 **Telefone**: [+55 27 98903-0474](tel:+5527989030474)
🌐 **Portfolio**: [https://thiagomemelli.com.br/](https://thiagomemelli.com.br/)

**Estou disponível para:**
- Posições de AI Engineer & Backend Python
- Desenvolvimento de Agentes Autônomos (RAG/Function Calling)
- Automação de Processos de Negócio
- Consultoria em Integração de LLMs
- Oportunidades no Brasil ou Exterior (Remoto)

---

<div align="center">

### ⭐ Se este projeto te impressionou, considere dar uma estrela no repo!

**Desenvolvido com 🧡 e Inteligência Artificial por Thiago Memelli**

*Projeto de Agente Autônomo - Dezembro 2025*

</div>