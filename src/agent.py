"""
Agent CORRIGIDO - Usa o campo 'blog' do GitHub para website
============================================================
"""

import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader

from src.tools import fetch_github_profile, search_candidate_online

load_dotenv()

# --- CONFIGURAÇÃO ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06")


# --- SCHEMAS (ESTRUTURA DE DADOS) ---

class SkillSet(BaseModel):
    languages: List[str] = Field(description="Linguagens de programação citadas que dão MATCH com a vaga")
    frameworks: List[str] = Field(description="Frameworks e ferramentas citadas que dão MATCH com a vaga")
    years_experience: Optional[int] = Field(description="Anos estimados de experiência")

class InterviewQuestion(BaseModel):
    question: str = Field(description="A pergunta técnica ou comportamental")
    expected_answer_topic: str = Field(description="O que o recrutador deve esperar como resposta (tópicos chave)")
    difficulty: str = Field(description="Fácil, Médio ou Difícil")

class CandidateAnalysis(BaseModel):
    candidate_name: str = Field(description="Nome do candidato identificado")
    github_username: Optional[str] = Field(description="Username do GitHub ou None")
    
    # Campos de Análise e Match
    match_score: int = Field(description="Nota de 0 a 100 de aderência ESPECÍFICA à vaga")
    match_analysis: str = Field(description="Explicação detalhada do match")
    missing_skills: List[str] = Field(description="Lista de habilidades que a vaga pede mas o candidato NÃO tem")
    
    # O Novo Campo "Arsenal" (Tudo o que você sabe)
    detected_hard_skills: List[str] = Field(
        description="Lista COMPLETA de todas as skills técnicas identificadas no CV e GitHub (independente da vaga)."
    )
    
    # Senioridade Contextual (O que fizemos antes)
    job_required_seniority: str = Field(description="Senioridade exigida pela VAGA")
    candidate_seniority_for_job: str = Field(description="Senioridade do candidato PARA ESTA VAGA ESPECÍFICA")

    # Novas Funcionalidades
    web_presence_analysis: str = Field(description="Resumo do que foi encontrado na busca web (LinkedIn, Artigos, etc)")
    interview_questions: List[InterviewQuestion] = Field(description="Sugestão de 3 a 5 perguntas para entrevista baseadas nos Gaps ou Pontos Fortes")

    skills: SkillSet

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Erro ao ler PDF: {e}"

# --- FUNÇÃO PRINCIPAL ---
def analyze_candidate_with_tools(cv_text: str, job_description: str, company_name: str) -> CandidateAnalysis:
    
    # 1. Extração de User GitHub e Nome (via GPT rápido)
    print("🤖 Fase 1: Extraindo Identidade...")
    extraction_prompt = f"""
    Analise o texto do CV abaixo.
    1. Extraia o Nome Completo do candidato.
    2. Extraia o username do GitHub (se houver).
    Retorne em JSON: {{"name": "Fulano", "github": "user_ou_none"}}
    Texto: {cv_text[:2000]}
    """
    extract_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": extraction_prompt}],
        response_format={"type": "json_object"}
    )
    identity = json.loads(extract_resp.choices[0].message.content)
    candidate_name = identity.get("name", "Candidato Desconhecido")
    github_user = identity.get("github")
    
    # 2. Executar Tools (GitHub + Web Search)
    github_data = {}
    github_data_context = "Perfil GitHub não encontrado."
    
    # ⭐ NOVO: Variáveis para URLs extraídas
    github_profile_url = None
    github_website = None  # Campo 'blog' do GitHub
    
    if github_user and github_user.lower() not in ["none", "null", ""]:
        clean_user = github_user.split("/")[-1].replace("@", "").strip()
        print(f"🔍 Buscando GitHub: {clean_user}")
        try:
            github_data = fetch_github_profile(clean_user)
            github_data_context = json.dumps(github_data, ensure_ascii=False, indent=2)
            
            # ⭐ EXTRAIR URLs DO GITHUB
            github_profile_url = f"https://github.com/{clean_user}"
            github_website = github_data.get("blog")  # <-- CAMPO IMPORTANTE!
            
            print(f"   ✅ GitHub encontrado: {github_profile_url}")
            if github_website:
                print(f"   ✅ Website do GitHub: {github_website}")
            else:
                print(f"   ⚠️ Website não configurado no GitHub")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            
    # Nova Tool: Busca na Web pelo nome
    web_search_context = search_candidate_online(candidate_name)
    
    # ⭐ NOVO: Construir seção de URLs explícitas
    urls_section = f"""
═══════════════════════════════════════════════════════════════
🔗 URLS ENCONTRADAS (USE ESTAS EXATAMENTE NO RELATÓRIO)
═══════════════════════════════════════════════════════════════
GitHub: {github_profile_url or 'Não encontrado'}
Website Pessoal: {github_website or 'Não encontrado'}
LinkedIn: Extrair do GitHub ou CV
═══════════════════════════════════════════════════════════════
"""

    # 3. Análise Contextual (O Grande Prompt)
    print("🤖 Fase 2: Gerando Relatório Completo...")
    
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
    
    completion = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": final_prompt}],
        response_format=CandidateAnalysis,
    )

    return completion.choices[0].message.parsed
