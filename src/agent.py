import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
# import google.generativeai as genai
# Importamos as duas ferramentas agora
from src.tools import fetch_github_profile, search_candidate_online

load_dotenv()

# --- CONFIGURAÇÃO ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06")
# OPÇÃO A: OpenAI (GPT-4o)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06")
# OPÇÃO B: Google (Gemini)
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# MODEL_NAME = "gemini-1.5-flash"

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
    github_data_context = "Perfil GitHub não encontrado."
    if github_user and github_user.lower() not in ["none", "null", ""]:
        clean_user = github_user.split("/")[-1].replace("@", "").strip()
        try:
            raw_data = fetch_github_profile(clean_user)
            github_data_context = json.dumps(raw_data, ensure_ascii=False)
        except Exception:
            pass
            
    # Nova Tool: Busca na Web pelo nome
    web_search_context = search_candidate_online(candidate_name)

    # 3. Análise Contextual (O Grande Prompt)
    print("🤖 Fase 2: Gerando Relatório Completo...")
    
    final_prompt = f"""
    Você é um Recrutador Especialista Tech da empresa **{company_name}**.
    
    VAGA:
    {job_description}
    
    CANDIDATO (CV):
    {cv_text}
    
    GITHUB (API):
    {github_data_context}
    
    WEB SEARCH (RESULTADOS):
    {web_search_context}
    
    INSTRUÇÕES:
    1. Analise o Match Score (0-100) com rigor.
    2. Analise se o candidato tem fit técnico e cultural para a **{company_name}**.
    3. Identifique 'detected_hard_skills': Liste TODAS as tecnologias que o candidato domina (mesmo as que não estão na vaga).
    4. Compare senioridade da vaga vs senioridade do candidato PARA A VAGA.
    5. Identifique 'job_required_seniority': O que a vaga pede? (Ex: Coordenador).
    6. Identifique 'candidate_seniority_for_job': Qual a senioridade do candidato NESTA ÁREA ESPECÍFICA?
       - ATENÇÃO: Se o candidato é Sênior em T.I., mas a vaga é de Cozinheiro, a senioridade dele para a vaga é "Nenhuma" ou "Iniciante". NÃO use a senioridade de outra área.
    7. Compare as skills do candidato EXATAMENTE com o que a vaga pede.
    8. Liste o que falta (missing_skills).
    9. Dê uma nota de Match (match_score) rigorosa baseada na vaga, não apenas no perfil genérico.
    10. Use o contexto da Web Search para validar se ele tem presença online (artigos, LinkedIn ativo, etc) em 'web_presence_analysis'.
    11. Gere 3 perguntas de entrevista técnicas desafiadoras baseadas no perfil dele.
    12. Responda em Português do Brasil.
    """
    
    completion = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": final_prompt}],
        response_format=CandidateAnalysis,
    )

    return completion.choices[0].message.parsed