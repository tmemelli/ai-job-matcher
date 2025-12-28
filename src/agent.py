"""
================================================================================
                            🧠 AGENT.PY - O CÉREBRO DO SISTEMA
================================================================================

Este módulo é o CORAÇÃO do AI Job Matcher Pro. Ele orquestra toda a análise
de candidatos usando Inteligência Artificial (GPT-4o) combinada com dados
externos (GitHub API + Web Search).

RESPONSABILIDADES:
    1. Extrair texto de currículos em PDF
    2. Identificar nome e GitHub do candidato via LLM
    3. Coletar dados externos (GitHub + Web)
    4. Analisar compatibilidade candidato x vaga
    5. Gerar relatório estruturado com score, gaps e perguntas de entrevista

FLUXO DE EXECUÇÃO:
    ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
    │   PDF CV    │────►│  Extração    │────►│ Identidade  │
    │  (Upload)   │     │  de Texto    │     │ (Nome/Git)  │
    └─────────────┘     └──────────────┘     └──────┬──────┘
                                                    │
                        ┌───────────────────────────┴───────────────────────┐
                        │                                                   │
                        ▼                                                   ▼
                ┌──────────────┐                                   ┌──────────────┐
                │  GitHub API  │                                   │  Web Search  │
                │  (Repos,Bio) │                                   │  (LinkedIn)  │
                └──────┬───────┘                                   └──────┬───────┘
                       │                                                  │
                       └────────────────────┬─────────────────────────────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │   GPT-4o     │
                                    │  Análise     │
                                    │  Completa    │
                                    └──────┬───────┘
                                           │
                                           ▼
                                   ┌───────────────┐
                                   │   Relatório   │
                                   │  Estruturado  │
                                   │  (Pydantic)   │
                                   └───────────────┘

DEPENDÊNCIAS EXTERNAS:
    - OpenAI API: Para análise via GPT-4o e GPT-4o-mini
    - GitHub API: Para buscar perfil e repositórios (via tools.py)
    - Tavily API: Para busca web de presença online (via tools.py)

AUTOR: Thiago Memelli
VERSÃO: 1.0.0
================================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import os          # Para acessar variáveis de ambiente (.env)
import json        # Para parsear respostas JSON do LLM
from typing import List, Optional  # Type hints para melhor legibilidade

# Pydantic: Biblioteca para validação de dados e criação de schemas estruturados
# O GPT-4o usa esses schemas para retornar dados no formato exato que precisamos
from pydantic import BaseModel, Field

# Cliente oficial da OpenAI para Python
from openai import OpenAI

# Carrega variáveis do arquivo .env (OPENAI_API_KEY, etc.)
from dotenv import load_dotenv

# Biblioteca para extrair texto de arquivos PDF
from pypdf import PdfReader

# Nossas ferramentas customizadas (GitHub API + Web Search)
# Estas funções estão definidas em tools.py
from src.tools import fetch_github_profile, search_candidate_online


# ==============================================================================
# CONFIGURAÇÃO INICIAL
# ==============================================================================

# Carrega as variáveis de ambiente do arquivo .env para o sistema
# Isso permite usar os.getenv() para acessar OPENAI_API_KEY, etc.
load_dotenv()

# Inicializa o cliente da OpenAI com a chave de API
# A chave é lida da variável de ambiente OPENAI_API_KEY
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define qual modelo GPT será usado na análise principal
# Pode ser sobrescrito via variável de ambiente OPENAI_MODEL
# Default: gpt-4o-2024-08-06 (versão estável com Structured Outputs)
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06")


# ==============================================================================
# SCHEMAS PYDANTIC - ESTRUTURA DOS DADOS DE SAÍDA
# ==============================================================================
# 
# Estes schemas definem EXATAMENTE o formato dos dados que o GPT-4o deve retornar.
# O recurso "Structured Outputs" da OpenAI garante que a resposta sempre
# seguirá este formato, eliminando erros de parsing e alucinações de estrutura.
#
# Pense nestes schemas como um "contrato" entre nosso código e o LLM.
# ==============================================================================


class SkillSet(BaseModel):
    """
    Representa o conjunto de habilidades técnicas do candidato que
    fazem MATCH com os requisitos da vaga.
    
    Attributes:
        languages: Lista de linguagens de programação que o candidato
                   domina E que a vaga solicita. Ex: ["Python", "JavaScript"]
        
        frameworks: Lista de frameworks e ferramentas que o candidato
                    conhece E que a vaga pede. Ex: ["FastAPI", "React", "Docker"]
        
        years_experience: Estimativa de anos de experiência do candidato
                          na área. Pode ser None se não for possível determinar.
    
    Example:
        >>> skills = SkillSet(
        ...     languages=["Python", "SQL"],
        ...     frameworks=["FastAPI", "Pandas"],
        ...     years_experience=3
        ... )
    """
    languages: List[str] = Field(
        description="Linguagens de programação citadas que dão MATCH com a vaga"
    )
    frameworks: List[str] = Field(
        description="Frameworks e ferramentas citadas que dão MATCH com a vaga"
    )
    years_experience: Optional[int] = Field(
        description="Anos estimados de experiência"
    )


class InterviewQuestion(BaseModel):
    """
    Representa uma pergunta sugerida para a entrevista técnica.
    
    O LLM gera perguntas personalizadas baseadas nos GAPS identificados
    entre o perfil do candidato e os requisitos da vaga.
    
    Attributes:
        question: A pergunta completa a ser feita ao candidato.
                  Ex: "Descreva sua experiência com microsserviços em Python."
        
        expected_answer_topic: Resumo do que o recrutador deve esperar
                               como resposta satisfatória.
                               Ex: "Candidato deve mencionar Docker, APIs REST, 
                               e comunicação entre serviços."
        
        difficulty: Nível de dificuldade da pergunta.
                    Valores possíveis: "Fácil", "Médio", "Difícil"
    
    Example:
        >>> question = InterviewQuestion(
        ...     question="Como você implementaria rate limiting em uma API?",
        ...     expected_answer_topic="Redis, token bucket, middleware",
        ...     difficulty="Médio"
        ... )
    """
    question: str = Field(
        description="A pergunta técnica ou comportamental"
    )
    expected_answer_topic: str = Field(
        description="O que o recrutador deve esperar como resposta (tópicos chave)"
    )
    difficulty: str = Field(
        description="Fácil, Médio ou Difícil"
    )


class CandidateAnalysis(BaseModel):
    """
    Schema principal que representa a análise COMPLETA de um candidato.
    
    Este é o objeto final retornado pela função analyze_candidate_with_tools().
    Contém todas as informações necessárias para o recrutador tomar uma decisão.
    
    Attributes:
        candidate_name: Nome completo do candidato extraído do CV.
        
        github_username: Username do GitHub (se encontrado no CV).
                         None se não foi possível identificar.
        
        match_score: Nota de 0 a 100 indicando a compatibilidade do
                     candidato com a vaga. 
                     - 80-100: Excelente fit
                     - 60-79: Bom fit, alguns gaps
                     - 40-59: Fit parcial, gaps significativos
                     - 0-39: Baixa compatibilidade
        
        match_analysis: Texto explicativo detalhando os pontos fortes
                        e fracos do candidato em relação à vaga.
        
        missing_skills: Lista de habilidades que a VAGA EXIGE mas que
                        o candidato NÃO POSSUI. Útil para identificar gaps.
        
        detected_hard_skills: Lista COMPLETA de todas as tecnologias
                              que o candidato conhece (extraídas do CV + GitHub),
                              independente de a vaga pedir ou não.
                              Útil para descobrir potencial oculto.
        
        job_required_seniority: Nível de senioridade que a VAGA pede.
                                Ex: "Pleno", "Sênior", "Tech Lead"
        
        candidate_seniority_for_job: Nível de senioridade do candidato
                                     ESPECIFICAMENTE para esta vaga.
                                     IMPORTANTE: Um Sênior em Backend pode
                                     ser Júnior em Data Science!
        
        web_presence_analysis: Resumo da presença online do candidato
                               com URLs do GitHub, LinkedIn e Website.
        
        interview_questions: Lista de 3-5 perguntas sugeridas para
                             a entrevista técnica, focadas nos gaps.
        
        skills: Objeto SkillSet com as habilidades que dão match.
    """
    # --- Identificação ---
    candidate_name: str = Field(
        description="Nome do candidato identificado"
    )
    github_username: Optional[str] = Field(
        description="Username do GitHub ou None"
    )
    
    # --- Análise de Compatibilidade ---
    match_score: int = Field(
        description="Nota de 0 a 100 de aderência ESPECÍFICA à vaga"
    )
    match_analysis: str = Field(
        description="Explicação detalhada do match"
    )
    missing_skills: List[str] = Field(
        description="Lista de habilidades que a vaga pede mas o candidato NÃO tem"
    )
    
    # --- Arsenal Técnico (Todas as Skills) ---
    detected_hard_skills: List[str] = Field(
        description="Lista COMPLETA de todas as skills técnicas identificadas "
                    "no CV e GitHub (independente da vaga)."
    )
    
    # --- Análise de Senioridade ---
    job_required_seniority: str = Field(
        description="Senioridade exigida pela VAGA"
    )
    candidate_seniority_for_job: str = Field(
        description="Senioridade do candidato PARA ESTA VAGA ESPECÍFICA"
    )

    # --- Presença Online ---
    web_presence_analysis: str = Field(
        description="Resumo do que foi encontrado na busca web "
                    "(LinkedIn, Artigos, etc)"
    )
    
    # --- Preparação para Entrevista ---
    interview_questions: List[InterviewQuestion] = Field(
        description="Sugestão de 3 a 5 perguntas para entrevista "
                    "baseadas nos Gaps ou Pontos Fortes"
    )

    # --- Skills que dão Match ---
    skills: SkillSet


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrai todo o texto de um arquivo PDF.
    
    Esta função é o primeiro passo do pipeline: converter o CV em PDF
    para texto plano que pode ser analisado pelo LLM.
    
    Args:
        pdf_path: Caminho completo para o arquivo PDF.
                  Ex: "/tmp/curriculum.pdf" ou "data/resume.pdf"
    
    Returns:
        String contendo todo o texto extraído do PDF.
        Cada página é separada por uma quebra de linha.
        
        Em caso de erro, retorna uma string começando com "Erro ao ler PDF:"
    
    Example:
        >>> texto = extract_text_from_pdf("data/resume.pdf")
        >>> print(texto[:100])
        "João Silva - Desenvolvedor Python\nExperiência: 5 anos..."
    
    Raises:
        Não levanta exceções - erros são capturados e retornados como string.
    
    Note:
        - Usa a biblioteca pypdf (moderna, mantida ativamente)
        - PDFs com imagens ou escaneados podem não ter texto extraível
        - Para PDFs complexos, considere usar OCR (Tesseract)
    """
    try:
        # Abre o arquivo PDF usando pypdf
        reader = PdfReader(pdf_path)
        
        # Inicializa string vazia para acumular o texto
        text = ""
        
        # Itera sobre cada página do PDF
        for page in reader.pages:
            # Extrai o texto da página e adiciona quebra de linha
            text += page.extract_text() + "\n"
        
        return text
    
    except Exception as e:
        # Em caso de qualquer erro, retorna mensagem informativa
        # ao invés de quebrar a aplicação
        return f"Erro ao ler PDF: {e}"


# ==============================================================================
# FUNÇÃO PRINCIPAL - O MOTOR DO SISTEMA
# ==============================================================================


def analyze_candidate_with_tools(
    cv_text: str, 
    job_description: str, 
    company_name: str
) -> CandidateAnalysis:
    """
    Realiza a análise COMPLETA de um candidato usando IA e dados externos.
    
    Esta é a função principal do módulo. Ela orquestra todo o pipeline:
    1. Extrai identidade do candidato (nome + GitHub) via GPT-4o-mini
    2. Busca dados no GitHub via API
    3. Busca presença online via Web Search
    4. Consolida tudo e envia para GPT-4o fazer a análise final
    5. Retorna objeto estruturado CandidateAnalysis
    
    Args:
        cv_text: Texto completo do currículo (extraído do PDF).
                 Deve conter informações como nome, experiência, skills.
        
        job_description: Descrição completa da vaga.
                         Deve incluir requisitos técnicos, senioridade desejada,
                         responsabilidades e benefícios.
        
        company_name: Nome da empresa que está contratando.
                      Usado para contextualizar a análise de fit cultural.
    
    Returns:
        CandidateAnalysis: Objeto Pydantic contendo:
            - match_score (0-100)
            - match_analysis (explicação)
            - missing_skills (gaps)
            - detected_hard_skills (arsenal completo)
            - interview_questions (perguntas sugeridas)
            - E mais... (ver docstring da classe)
    
    Example:
        >>> cv = extract_text_from_pdf("candidato.pdf")
        >>> vaga = "Procuramos Desenvolvedor Python Sênior com FastAPI..."
        >>> resultado = analyze_candidate_with_tools(cv, vaga, "TechCorp")
        >>> print(f"Match: {resultado.match_score}%")
        Match: 85%
    
    Note:
        - Requer OPENAI_API_KEY configurada no ambiente
        - Faz múltiplas chamadas de API (OpenAI + GitHub + Web Search)
        - Tempo médio de execução: 10-30 segundos
    """
    
    # ==========================================================================
    # FASE 1: EXTRAÇÃO DE IDENTIDADE
    # ==========================================================================
    # Objetivo: Descobrir o nome do candidato e seu username do GitHub
    # Método: Usa GPT-4o-mini (mais rápido e barato) para extrair do CV
    # ==========================================================================
    
    print("🤖 Fase 1: Extraindo Identidade...")
    
    # Prompt para extrair nome e GitHub do texto do CV
    # Usamos apenas os primeiros 2000 caracteres para economizar tokens
    # (nome e GitHub geralmente estão no início do CV)
    extraction_prompt = f"""
    Analise o texto do CV abaixo.
    1. Extraia o Nome Completo do candidato.
    2. Extraia o username do GitHub (se houver).
    Retorne em JSON: {{"name": "Fulano", "github": "user_ou_none"}}
    Texto: {cv_text[:2000]}
    """
    
    # Chamada ao GPT-4o-mini com resposta forçada em JSON
    extract_resp = client.chat.completions.create(
        model="gpt-4o-mini",  # Modelo menor = mais rápido e barato
        messages=[{"role": "user", "content": extraction_prompt}],
        response_format={"type": "json_object"}  # Garante resposta em JSON válido
    )
    
    # Parseia a resposta JSON
    identity = json.loads(extract_resp.choices[0].message.content)
    
    # Extrai os campos com valores default para evitar erros
    candidate_name = identity.get("name", "Candidato Desconhecido")
    github_user = identity.get("github")
    
    # ==========================================================================
    # FASE 2: COLETA DE DADOS EXTERNOS
    # ==========================================================================
    # Objetivo: Enriquecer o perfil com dados do GitHub e Web
    # Ferramentas: fetch_github_profile() e search_candidate_online()
    # ==========================================================================
    
    # --- 2.1: Inicialização das variáveis ---
    github_data = {}  # Dados brutos da API do GitHub
    github_data_context = "Perfil GitHub não encontrado."  # Texto para o prompt
    
    # URLs que serão extraídas para exibição na interface
    github_profile_url = None  # Ex: https://github.com/tmemelli
    github_website = None      # Campo 'blog' do perfil GitHub (website pessoal)
    
    # --- 2.2: Busca no GitHub (se username foi encontrado) ---
    # Verifica se o username não é vazio, "none" ou "null"
    if github_user and github_user.lower() not in ["none", "null", ""]:
        
        # Limpa o username (remove prefixos como @ ou URLs parciais)
        clean_user = github_user.split("/")[-1].replace("@", "").strip()
        
        print(f"🔍 Buscando GitHub: {clean_user}")
        
        try:
            # Chama a função de tools.py que acessa a GitHub API
            github_data = fetch_github_profile(clean_user)
            
            # Converte para JSON formatado (será incluído no prompt do GPT)
            github_data_context = json.dumps(github_data, ensure_ascii=False, indent=2)
            
            # =====================================================
            # EXTRAÇÃO DE URLs DO GITHUB
            # =====================================================
            # O campo 'blog' da API do GitHub contém o website
            # pessoal que o usuário configurou no perfil.
            # Este é o SEGREDO para pegar o website corretamente!
            # =====================================================
            
            github_profile_url = f"https://github.com/{clean_user}"
            github_website = github_data.get("blog")  # <-- CAMPO IMPORTANTE!
            
            print(f"   ✅ GitHub encontrado: {github_profile_url}")
            
            if github_website:
                print(f"   ✅ Website do GitHub: {github_website}")
            else:
                print(f"   ⚠️ Website não configurado no GitHub")
                
        except Exception as e:
            # Se falhar, apenas loga o erro e continua
            # O sistema ainda funciona sem dados do GitHub
            print(f"   ❌ Erro: {e}")
    
    # --- 2.3: Busca na Web (LinkedIn, artigos, etc.) ---
    # Usa Tavily API (ou DuckDuckGo como fallback) para buscar
    # presença online do candidato
    web_search_context = search_candidate_online(candidate_name)
    
    # ==========================================================================
    # FASE 3: PREPARAÇÃO DO CONTEXTO PARA O LLM
    # ==========================================================================
    # Objetivo: Organizar todas as informações coletadas em um formato
    #           que o GPT-4o possa processar eficientemente
    # ==========================================================================
    
    # Monta seção de URLs para incluir no prompt
    # Isso garante que o LLM use URLs REAIS ao invés de inventar
    urls_section = f"""
═══════════════════════════════════════════════════════════════
🔗 URLS ENCONTRADAS (USE ESTAS EXATAMENTE NO RELATÓRIO)
═══════════════════════════════════════════════════════════════
GitHub: {github_profile_url or 'Não encontrado'}
Website Pessoal: {github_website or 'Não encontrado'}
LinkedIn: Extrair do GitHub ou CV
═══════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # FASE 4: ANÁLISE PRINCIPAL COM GPT-4o
    # ==========================================================================
    # Objetivo: Usar o modelo mais poderoso para analisar tudo e gerar
    #           o relatório estruturado final
    # Método: Prompt detalhado + Structured Outputs (Pydantic)
    # ==========================================================================
    
    print("🤖 Fase 2: Gerando Relatório Completo...")
    
    # Monta o prompt principal com todas as instruções
    # Este prompt é o "cérebro" da análise - define exatamente o que queremos
    final_prompt = f"""
    Você é um Recrutador Especialista Tech da empresa **{company_name}**.
    
    SUA MISSÃO:
    Avaliar a compatibilidade entre um candidato e uma vaga.
    
    ENTRADAS:
    1. VAGA: {job_description}
    2. CANDIDATO (CV): {cv_text}
    
    GITHUB (API):
    {github_data_context}
    
    {urls_section}
    
    WEB SEARCH (RESULTADOS):
    {web_search_context}
    
    ⚠️ REGRAS CRÍTICAS:
    1. O PDF (Currículo) é a FONTE SOBERANA para experiência profissional.
    2. Para 'web_presence_analysis', você DEVE incluir as URLs encontradas acima.
       - Se tem GitHub: CITE a URL completa (https://github.com/...)
       - Se tem Website Pessoal: CITE a URL completa (https://...)
       - Se tem LinkedIn: CITE a URL completa
    3. NÃO INVENTE URLs. Use apenas as que foram fornecidas acima.
    4. Se a busca web falhou mas temos dados do GitHub, use os dados do GitHub.

    INSTRUÇÕES:
    1. Analise o Match Score (0-100) com rigor.
    2. Analise se o candidato tem fit técnico e cultural para a **{company_name}**.
    3. Identifique 'detected_hard_skills': Liste TODAS as tecnologias que o candidato domina.
    4. Compare senioridade da vaga vs senioridade do candidato PARA A VAGA.
    5. Identifique 'job_required_seniority': O que a vaga pede?
    6. Identifique 'candidate_seniority_for_job': Qual a senioridade do candidato NESTA ÁREA?
    7. Compare as skills do candidato EXATAMENTE com o que a vaga pede.
    8. Liste o que falta (missing_skills).
    9. Dê uma nota de Match (match_score) rigorosa.
    
    10. ⭐ IMPORTANTE para 'web_presence_analysis':
        - COMECE listando as URLs encontradas (GitHub, Website, LinkedIn)
        - Depois de listar as URLs, PULE UMA LINHA antes do resumo
        - Formato esperado:
          "GitHub: [URL]. Website: [URL]. LinkedIn: [URL].
          
          [Resumo do perfil em 2-3 frases]"
    
    11. Gere 3-5 perguntas de entrevista técnicas baseadas no perfil.
    12. Responda em Português do Brasil.
    """
    
    # ==========================================================================
    # CHAMADA FINAL À API COM STRUCTURED OUTPUTS
    # ==========================================================================
    # O método client.beta.chat.completions.parse() é especial:
    # Ele FORÇA o GPT-4o a retornar dados no formato exato do schema Pydantic.
    # Isso elimina erros de parsing e garante type safety.
    # ==========================================================================
    
    completion = client.beta.chat.completions.parse(
        model=MODEL_NAME,                        # gpt-4o-2024-08-06
        messages=[{"role": "user", "content": final_prompt}],
        response_format=CandidateAnalysis,       # Schema Pydantic como formato
    )

    # Retorna o objeto já parseado e validado pelo Pydantic
    # completion.choices[0].message.parsed é do tipo CandidateAnalysis
    return completion.choices[0].message.parsed
