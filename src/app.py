"""
App CORRIGIDO - Renderiza links corretamente
============================================
"""

import streamlit as st
import os
import sys
import tempfile
import re
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agent import analyze_candidate_with_tools, extract_text_from_pdf

load_dotenv()

st.set_page_config(page_title="Job Matcher AI", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .css-card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .metric-value { font-size: 28px; font-weight: bold; color: #1f77b4; }
    .metric-label { font-size: 14px; color: #6c757d; }
    .skill-tag { display: inline-block; background-color: #e1ecf4; color: #39739d; padding: 5px 10px; border-radius: 15px; font-size: 12px; margin: 2px; }
    .skill-tag-gray { display: inline-block; background-color: #f0f2f6; color: #555; padding: 5px 10px; border-radius: 15px; font-size: 12px; margin: 2px; }
    .missing-tag { display: inline-block; background-color: #f8d7da; color: #721c24; padding: 5px 10px; border-radius: 15px; font-size: 12px; margin: 2px; }
</style>
""", unsafe_allow_html=True)


def extract_urls_from_text(text: str) -> dict:
    """Extrai URLs do texto da análise"""
    urls = {
        "github": None,
        "website": None,
        "linkedin": None
    }
    
    # GitHub
    github_match = re.search(r'https?://github\.com/[a-zA-Z0-9_-]+', text)
    if github_match:
        urls["github"] = github_match.group()
    
    # Website pessoal (não github, não linkedin)
    website_matches = re.findall(r'https?://[^\s<>"\']+', text)
    for url in website_matches:
        url_lower = url.lower()
        if 'github.com' not in url_lower and 'linkedin.com' not in url_lower:
            if any(ext in url_lower for ext in ['.com.br', '.com', '.io', '.dev', '.me']):
                urls["website"] = url.rstrip('.,;:')
                break
    
    # LinkedIn
    linkedin_match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?', text)
    if linkedin_match:
        urls["linkedin"] = linkedin_match.group().rstrip('/')
    
    return urls


def main():
    st.markdown("<h1 style='text-align: center;'>🎯 AI Job Matcher Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>Analise o 'Fit' do candidato para sua vaga específica</p>", unsafe_allow_html=True)
    st.markdown("---")

    # --- 🔒 TRAVA DE SEGURANÇA ---
    with st.sidebar:
        st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3064/3064197.png", width=50)
        app_password = st.text_input("🔒 Senha de Acesso", type="password", help="Peça a senha ao administrador")
        
        SENHA_CORRETA = os.getenv("APP_PASSWORD")
        
        if not SENHA_CORRETA:
            st.error("Erro de Configuração: Senha não definida no servidor.")
            st.stop()

        if not app_password:
            st.info("Digite a senha para liberar o sistema.")
            st.stop()

        if app_password != SENHA_CORRETA:
            st.error("⚠️ Senha incorreta.")
            st.stop()
            
    with st.sidebar:
        st.header("🏢 Contexto da Vaga")
        company_name = st.text_input("Empresa", placeholder="Ex: Google")
        job_description = st.text_area("Descrição da Vaga", height=300)
        
    col_upload, _ = st.columns([1, 0.1]) 
    with col_upload:
        uploaded_file = st.file_uploader("📂 Upload do Currículo (PDF)", type="pdf")

    if uploaded_file and job_description:
        if st.button("🚀 Analisar Compatibilidade", type="primary", use_container_width=True):
            with st.spinner(f"Analisando candidato, LinkedIn, GitHub e presença Web..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    text = extract_text_from_pdf(tmp_path)
                    result = analyze_candidate_with_tools(text, job_description, company_name)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # --- CABEÇALHO DO CANDIDATO ---
                    st.markdown(f"""
                    <div class="css-card">
                        <h2 style="margin:0; color:#2c3e50;">👤 {result.candidate_name}</h2>
                        <p style="color:grey; margin:0;">GitHub: @{result.github_username or 'N/A'}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    col_metrics, col_details = st.columns([1, 2])
                    
                    with col_metrics:
                        match_color = "green" if result.match_score >= 80 else "orange" if result.match_score >= 60 else "red"
                        
                        # SCORE CARD + COMPARATIVO
                        st.markdown(f"""
                        <div class="css-card" style="text-align:center;">
                            <div class="metric-label">Job Match Score</div>
                            <div class="metric-value" style="color:{match_color}; font-size: 42px;">{result.match_score}%</div>
                            <hr>
                            <p style="font-size:12px; color:grey; margin-bottom: 5px;">Comparativo de Nível</p>
                            <div style="margin-bottom: 10px;">
                                <span style="font-size:14px; font-weight:bold; color:#6c757d;">Vaga Pede:</span><br>
                                <span style="font-size:18px; color:#2c3e50;">{result.job_required_seniority}</span>
                            </div>
                            <div>
                                <span style="font-size:14px; font-weight:bold; color:#6c757d;">Seu Nível:</span><br>
                                <span style="font-size:18px; color:#d9534f;">{result.candidate_seniority_for_job}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # ⭐ PRESENÇA ONLINE COM BOTÕES CLICÁVEIS
                        st.markdown("### 🌐 Presença Online")
                        
                        # Extrair URLs do texto de análise
                        urls = extract_urls_from_text(result.web_presence_analysis)
                        
                        # GitHub
                        github_url = urls.get("github") or (f"https://github.com/{result.github_username}" if result.github_username else None)
                        if github_url:
                            st.link_button("🐙 GitHub", github_url, use_container_width=True)
                        else:
                            st.button("🐙 GitHub - Não encontrado", disabled=True, use_container_width=True)
                        
                        # Website
                        website_url = urls.get("website")
                        if website_url:
                            st.link_button("🌍 Website Pessoal", website_url, use_container_width=True)
                        else:
                            st.button("🌍 Website - Não encontrado", disabled=True, use_container_width=True)
                        
                        # LinkedIn
                        linkedin_url = urls.get("linkedin")
                        if linkedin_url:
                            st.link_button("💼 LinkedIn", linkedin_url, use_container_width=True)
                        else:
                            st.button("💼 LinkedIn - Não encontrado", disabled=True, use_container_width=True)
                        
                        # Resumo textual
                        st.info(result.web_presence_analysis)

                    with col_details:
                        # ANÁLISE
                        st.markdown(f"""
                        <div class="css-card">
                            <h3 style="margin-top:0;">📊 Análise de Compatibilidade</h3>
                            <p style="color:#444;">{result.match_analysis}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # SKILLS MATCH (VERDE)
                        st.markdown("### ✅ Stack Match (Requisitos Atendidos)")
                        skills_html = ""
                        for s in result.skills.languages + result.skills.frameworks:
                            skills_html += f'<span class="skill-tag">{s}</span>'
                        st.markdown(f"""<div class="css-card">{skills_html}</div>""", unsafe_allow_html=True)

                        # GAPS (VERMELHO)
                        if result.missing_skills:
                            st.markdown("### ⚠️ Gaps (Faltantes)")
                            missing_html = ""
                            for gap in result.missing_skills:
                                missing_html += f'<span class="missing-tag">{gap}</span>'
                            st.markdown(f"""<div class="css-card">{missing_html}</div>""", unsafe_allow_html=True)

                        # ARSENAL COMPLETO (CINZA)
                        st.markdown("### 🛠️ Arsenal Técnico Completo (Detectado)")
                        full_stack_html = ""
                        for skill in result.detected_hard_skills[:20]:
                            full_stack_html += f'<span class="skill-tag-gray">{skill}</span>'
                        st.markdown(f"""<div class="css-card">{full_stack_html}</div>""", unsafe_allow_html=True)

                    # --- SEÇÃO DE ENTREVISTA ---
                    st.markdown("---")
                    st.subheader("🎤 Modo Entrevista (Sugestões de Perguntas)")
                    
                    for i, q in enumerate(result.interview_questions):
                        with st.expander(f"Pergunta {i+1}: {q.difficulty} ({q.question[:50]}...)"):
                            st.markdown(f"**Pergunta:** {q.question}")
                            st.markdown(f"**O que esperar na resposta:** {q.expected_answer_topic}")

                except Exception as e:
                    st.error(f"Erro: {e}")
                    import traceback
                    st.code(traceback.format_exc())
                finally:
                    if os.path.exists(tmp_path): os.unlink(tmp_path)

if __name__ == "__main__":
    main()
