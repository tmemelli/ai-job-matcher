"""
================================================================================
                        🖥️ APP.PY - A INTERFACE DO USUÁRIO
================================================================================

Este módulo é a FACE do AI Job Matcher Pro. É aqui que recrutadores interagem
com o sistema através de um dashboard web construído com Streamlit.

RESPONSABILIDADES:
    1. Autenticação de usuários (proteção por senha)
    2. Upload e processamento de currículos PDF
    3. Captura da descrição da vaga
    4. Exibição dos resultados da análise
    5. Apresentação das perguntas de entrevista

FLUXO DA INTERFACE:
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                         SIDEBAR (Lateral)                               │
    │  ┌─────────────────────────────────────────────────────────────────┐    │
    │  │  🔒 Autenticação                                                │    │
    │  │  ────────────────                                               │    │
    │  │  [Senha: ••••••••]                                              │    │
    │  │                                                                 │    │
    │  │  🏢 Contexto da Vaga                                            │    │
    │  │  ────────────────                                               │    │
    │  │  Empresa: [___________]                                         │    │
    │  │  Descrição: [                                                   │    │
    │  │              Textarea                                           │    │
    │  │              da vaga                                            │    │
    │  │            ]                                                    │    │
    │  └─────────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                         ÁREA PRINCIPAL                                  │
    │  ┌─────────────────────────────────────────────────────────────────┐    │
    │  │  📂 Upload do Currículo (PDF)                                   │    │
    │  │  [Arraste ou clique para upload]                                │    │
    │  │                                                                 │    │
    │  │  [🚀 Analisar Compatibilidade]                                  │    │
    │  └─────────────────────────────────────────────────────────────────┘    │
    │                                                                         │
    │  ┌──────────────────┐  ┌────────────────────────────────────────────┐   │
    │  │   MÉTRICAS       │  │   DETALHES                                 │   │
    │  │   ──────────     │  │   ────────                                 │   │
    │  │   Score: 85%     │  │   📊 Análise de Compatibilidade            │   │
    │  │   Vaga: Sênior   │  │   ✅ Stack Match                           │   │
    │  │   Candidato: Pl. │  │   ⚠️ Gaps                                  │   │
    │  │                  │  │   🛠️ Arsenal Técnico                       │   │
    │  │   🌐 Presença    │  │                                            │   │
    │  │   [GitHub]       │  │                                            │   │
    │  │   [LinkedIn]     │  │                                            │   │
    │  │   [Website]      │  │                                            │   │
    │  └──────────────────┘  └────────────────────────────────────────────┘   │
    │                                                                         │
    │  ┌─────────────────────────────────────────────────────────────────┐    │
    │  │  🎤 Modo Entrevista                                             │    │
    │  │  ► Pergunta 1: Médio (Como você implementaria...)               │    │
    │  │  ► Pergunta 2: Difícil (Descreva um cenário...)                 │    │
    │  │  ► Pergunta 3: Fácil (O que é...)                               │    │
    │  └─────────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────────┘

TECNOLOGIAS:
    - Streamlit: Framework para dashboards interativos em Python
    - HTML/CSS: Customização visual dos componentes
    - Regex: Extração de URLs do texto de análise

SEGURANÇA:
    - Autenticação por senha (variável APP_PASSWORD)
    - Arquivos temporários são deletados após processamento
    - Nenhum dado é persistido no servidor

DEPENDÊNCIAS:
    - streamlit: Framework de interface
    - python-dotenv: Carregamento de variáveis de ambiente
    - agent.py: Lógica de análise (importado)

VARIÁVEIS DE AMBIENTE:
    - APP_PASSWORD: Senha de acesso ao sistema (OBRIGATÓRIO)

AUTOR: Thiago Memelli
VERSÃO: 1.0.0
================================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import streamlit as st    # Framework para criação de dashboards web
import os                 # Acesso a variáveis de ambiente e sistema de arquivos
import sys                # Manipulação do path de imports
import tempfile           # Criação de arquivos temporários para PDFs
import re                 # Expressões regulares para extração de URLs

# Carrega variáveis de ambiente do arquivo .env
from dotenv import load_dotenv


# ==============================================================================
# CONFIGURAÇÃO DE PATH
# ==============================================================================
# Adiciona o diretório pai ao path para permitir imports do módulo src
# Isso é necessário porque Streamlit executa o app de diferentes diretórios
# ==============================================================================

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa as funções do módulo agent.py (o cérebro do sistema)
from src.agent import analyze_candidate_with_tools, extract_text_from_pdf


# ==============================================================================
# INICIALIZAÇÃO
# ==============================================================================

# Carrega as variáveis de ambiente (.env)
load_dotenv()

# Configura a página do Streamlit
# - page_title: Título que aparece na aba do navegador
# - page_icon: Emoji que aparece na aba
# - layout: "wide" usa toda a largura da tela
st.set_page_config(
    page_title="Job Matcher AI", 
    page_icon="🎯", 
    layout="wide"
)


# ==============================================================================
# ESTILOS CSS CUSTOMIZADOS
# ==============================================================================
# Streamlit permite injetar CSS customizado para estilizar componentes.
# Usamos isso para criar cards, tags de skills e melhorar a aparência geral.
# ==============================================================================

st.markdown("""
<style>
    /* Cor de fundo da aplicação */
    .stApp { background-color: #f8f9fa; }
    
    /* Card genérico com sombra suave */
    .css-card { 
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
        margin-bottom: 20px; 
    }
    
    /* Valor grande das métricas (ex: 85%) */
    .metric-value { 
        font-size: 28px; 
        font-weight: bold; 
        color: #1f77b4; 
    }
    
    /* Label das métricas (ex: "Job Match Score") */
    .metric-label { 
        font-size: 14px; 
        color: #6c757d; 
    }
    
    /* Tag de skill que dá match (azul) */
    .skill-tag { 
        display: inline-block; 
        background-color: #e1ecf4; 
        color: #39739d; 
        padding: 5px 10px; 
        border-radius: 15px; 
        font-size: 12px; 
        margin: 2px; 
    }
    
    /* Tag de skill do arsenal completo (cinza) */
    .skill-tag-gray { 
        display: inline-block; 
        background-color: #f0f2f6; 
        color: #555; 
        padding: 5px 10px; 
        border-radius: 15px; 
        font-size: 12px; 
        margin: 2px; 
    }
    
    /* Tag de skill faltante/gap (vermelho) */
    .missing-tag { 
        display: inline-block; 
        background-color: #f8d7da; 
        color: #721c24; 
        padding: 5px 10px; 
        border-radius: 15px; 
        font-size: 12px; 
        margin: 2px; 
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================


def extract_urls_from_text(text: str) -> dict:
    """
    Extrai URLs de GitHub, LinkedIn e website pessoal do texto de análise.
    
    O LLM retorna a análise de presença web como texto livre. Esta função
    usa expressões regulares para extrair as URLs mencionadas, permitindo
    criar botões clicáveis na interface.
    
    Args:
        text: Texto da análise de presença web retornado pelo LLM.
              Ex: "GitHub: https://github.com/user. LinkedIn: https://..."
    
    Returns:
        Dict com as URLs encontradas:
            {
                "github": "https://github.com/user" | None,
                "website": "https://meusite.com.br" | None,
                "linkedin": "https://linkedin.com/in/user" | None
            }
    
    Example:
        >>> text = "GitHub: https://github.com/tmemelli. Site: https://thiagomemelli.com.br"
        >>> urls = extract_urls_from_text(text)
        >>> print(urls["github"])
        "https://github.com/tmemelli"
    
    Note:
        - A ordem de prioridade para website exclui github e linkedin
        - URLs são limpas de pontuação final (.,;:)
        - Regex são case-insensitive para domínios
    """
    # Inicializa dicionário com valores None
    urls = {
        "github": None,
        "website": None,
        "linkedin": None
    }
    
    # =========================================================================
    # EXTRAÇÃO 1: GitHub
    # =========================================================================
    # Padrão: https://github.com/username
    # Captura apenas o username, não subpáginas como /repo/issues
    # =========================================================================
    
    github_match = re.search(r'https?://github\.com/[a-zA-Z0-9_-]+', text)
    if github_match:
        urls["github"] = github_match.group()
    
    # =========================================================================
    # EXTRAÇÃO 2: Website Pessoal
    # =========================================================================
    # Estratégia: Encontra todas as URLs e filtra as que NÃO são github/linkedin
    # Prioriza domínios comuns: .com.br, .com, .io, .dev, .me
    # =========================================================================
    
    # Encontra todas as URLs no texto
    website_matches = re.findall(r'https?://[^\s<>"\']+', text)
    
    for url in website_matches:
        url_lower = url.lower()
        
        # Ignora GitHub e LinkedIn (já tratados separadamente)
        if 'github.com' not in url_lower and 'linkedin.com' not in url_lower:
            # Verifica se é um domínio válido de website
            if any(ext in url_lower for ext in ['.com.br', '.com', '.io', '.dev', '.me']):
                # Remove pontuação que pode ter sido capturada no final
                urls["website"] = url.rstrip('.,;:')
                break  # Pega apenas o primeiro match válido
    
    # =========================================================================
    # EXTRAÇÃO 3: LinkedIn
    # =========================================================================
    # Padrão: https://linkedin.com/in/username ou https://www.linkedin.com/in/username
    # O (?: ) cria grupo não-capturador para o www opcional
    # =========================================================================
    
    linkedin_match = re.search(
        r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?', 
        text
    )
    if linkedin_match:
        # Remove barra final para consistência
        urls["linkedin"] = linkedin_match.group().rstrip('/')
    
    return urls


# ==============================================================================
# FUNÇÃO PRINCIPAL - PONTO DE ENTRADA DA APLICAÇÃO
# ==============================================================================


def main():
    """
    Função principal que renderiza toda a interface do dashboard.
    
    Esta função é o ponto de entrada da aplicação Streamlit. Ela:
    1. Renderiza o cabeçalho
    2. Gerencia autenticação na sidebar
    3. Captura inputs (vaga + PDF)
    4. Processa a análise via agent.py
    5. Exibe os resultados formatados
    
    A função é executada a cada interação do usuário (modelo reativo).
    Streamlit re-executa o script inteiro quando há mudanças de estado.
    
    Note:
        - Não recebe parâmetros (estado gerenciado pelo Streamlit)
        - Não retorna valores (renderiza diretamente na interface)
        - Exceções são capturadas e exibidas como erro na UI
    """
    
    # =========================================================================
    # CABEÇALHO DA PÁGINA
    # =========================================================================
    
    st.markdown(
        "<h1 style='text-align: center;'>🎯 AI Job Matcher Pro</h1>", 
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; color: grey;'>"
        "Analise o 'Fit' do candidato para sua vaga específica"
        "</p>", 
        unsafe_allow_html=True
    )
    st.markdown("---")

    # =========================================================================
    # SIDEBAR - AUTENTICAÇÃO
    # =========================================================================
    # Sistema de proteção por senha para evitar uso não autorizado.
    # A senha é definida via variável de ambiente APP_PASSWORD.
    # =========================================================================
    
    with st.sidebar:
        # Logo/ícone decorativo
        st.sidebar.image(
            "https://cdn-icons-png.flaticon.com/512/3064/3064197.png", 
            width=50
        )
        
        # Campo de senha (tipo password oculta os caracteres)
        app_password = st.text_input(
            "🔒 Senha de Acesso", 
            type="password", 
            help="Peça a senha ao administrador"
        )
        
        # Carrega a senha correta do ambiente
        SENHA_CORRETA = os.getenv("APP_PASSWORD")
        
        # =====================================================================
        # VALIDAÇÕES DE SEGURANÇA
        # =====================================================================
        # Três verificações em sequência:
        # 1. Senha configurada no servidor?
        # 2. Usuário digitou algo?
        # 3. Senha está correta?
        # st.stop() interrompe a execução se qualquer validação falhar
        # =====================================================================
        
        if not SENHA_CORRETA:
            st.error("Erro de Configuração: Senha não definida no servidor.")
            st.stop()

        if not app_password:
            st.info("Digite a senha para liberar o sistema.")
            st.stop()

        if app_password != SENHA_CORRETA:
            st.error("⚠️ Senha incorreta.")
            st.stop()
    
    # =========================================================================
    # SIDEBAR - CONTEXTO DA VAGA
    # =========================================================================
    # Após autenticação bem-sucedida, exibe campos para a vaga
    # =========================================================================
    
    with st.sidebar:
        st.header("🏢 Contexto da Vaga")
        
        # Nome da empresa (usado para contextualizar a análise)
        company_name = st.text_input(
            "Empresa", 
            placeholder="Ex: Google"
        )
        
        # Descrição completa da vaga (textarea maior)
        job_description = st.text_area(
            "Descrição da Vaga", 
            height=300
        )
    
    # =========================================================================
    # ÁREA PRINCIPAL - UPLOAD DO CV
    # =========================================================================
    
    # Cria colunas para centralizar o uploader (truque de layout)
    col_upload, _ = st.columns([1, 0.1]) 
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "📂 Upload do Currículo (PDF)", 
            type="pdf"  # Aceita apenas PDFs
        )

    # =========================================================================
    # PROCESSAMENTO DA ANÁLISE
    # =========================================================================
    # Só processa se:
    # 1. Há um arquivo PDF carregado
    # 2. Há uma descrição de vaga preenchida
    # 3. O usuário clicou no botão de análise
    # =========================================================================
    
    if uploaded_file and job_description:
        # Botão de ação principal
        if st.button(
            "🚀 Analisar Compatibilidade", 
            type="primary",           # Estilo destacado
            use_container_width=True  # Largura total
        ):
            # Spinner mostra feedback visual durante o processamento
            with st.spinner("Analisando candidato, LinkedIn, GitHub e presença Web..."):
                
                # =============================================================
                # ETAPA 1: SALVAR PDF TEMPORARIAMENTE
                # =============================================================
                # Streamlit recebe o arquivo como bytes em memória.
                # Precisamos salvá-lo em disco para o pypdf processar.
                # =============================================================
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    # =========================================================
                    # ETAPA 2: EXTRAIR TEXTO DO PDF
                    # =========================================================
                    text = extract_text_from_pdf(tmp_path)
                    
                    # =========================================================
                    # ETAPA 3: EXECUTAR ANÁLISE VIA AGENT.PY
                    # =========================================================
                    # Esta é a chamada principal que:
                    # - Extrai identidade do candidato
                    # - Busca dados no GitHub
                    # - Faz web search
                    # - Analisa tudo com GPT-4o
                    # =========================================================
                    result = analyze_candidate_with_tools(
                        text, 
                        job_description, 
                        company_name
                    )
                    
                    # Espaçamento visual
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # =========================================================
                    # ETAPA 4: RENDERIZAR CABEÇALHO DO CANDIDATO
                    # =========================================================
                    
                    st.markdown(f"""
                    <div class="css-card">
                        <h2 style="margin:0; color:#2c3e50;">👤 {result.candidate_name}</h2>
                        <p style="color:grey; margin:0;">GitHub: @{result.github_username or 'N/A'}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # =========================================================
                    # ETAPA 5: LAYOUT EM DUAS COLUNAS
                    # =========================================================
                    # Coluna esquerda (1): Métricas e presença online
                    # Coluna direita (2): Detalhes da análise
                    # Proporção 1:2 dá mais espaço para os detalhes
                    # =========================================================
                    
                    col_metrics, col_details = st.columns([1, 2])
                    
                    # ---------------------------------------------------------
                    # COLUNA ESQUERDA: MÉTRICAS
                    # ---------------------------------------------------------
                    
                    with col_metrics:
                        # Define cor do score baseado no valor
                        # Verde >= 80, Laranja >= 60, Vermelho < 60
                        match_color = (
                            "green" if result.match_score >= 80 
                            else "orange" if result.match_score >= 60 
                            else "red"
                        )
                        
                        # Card principal com score e comparativo de senioridade
                        st.markdown(f"""
                        <div class="css-card" style="text-align:center;">
                            <div class="metric-label">Job Match Score</div>
                            <div class="metric-value" style="color:{match_color}; font-size: 42px;">
                                {result.match_score}%
                            </div>
                            <hr>
                            <p style="font-size:12px; color:grey; margin-bottom: 5px;">
                                Comparativo de Nível
                            </p>
                            <div style="margin-bottom: 10px;">
                                <span style="font-size:14px; font-weight:bold; color:#6c757d;">
                                    Vaga Pede:
                                </span><br>
                                <span style="font-size:18px; color:#2c3e50;">
                                    {result.job_required_seniority}
                                </span>
                            </div>
                            <div>
                                <span style="font-size:14px; font-weight:bold; color:#6c757d;">
                                    Seu Nível:
                                </span><br>
                                <span style="font-size:18px; color:#d9534f;">
                                    {result.candidate_seniority_for_job}
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # -------------------------------------------------
                        # PRESENÇA ONLINE COM BOTÕES CLICÁVEIS
                        # -------------------------------------------------
                        # Extrai URLs do texto e cria botões que abrem
                        # os links em nova aba
                        # -------------------------------------------------
                        
                        st.markdown("### 🌐 Presença Online")
                        
                        # Extrai URLs do texto de análise usando regex
                        urls = extract_urls_from_text(result.web_presence_analysis)
                        
                        # Botão GitHub
                        github_url = urls.get("github") or (
                            f"https://github.com/{result.github_username}" 
                            if result.github_username 
                            else None
                        )
                        if github_url:
                            st.link_button(
                                "🐙 GitHub", 
                                github_url, 
                                use_container_width=True
                            )
                        else:
                            st.button(
                                "🐙 GitHub - Não encontrado", 
                                disabled=True, 
                                use_container_width=True
                            )
                        
                        # Botão Website
                        website_url = urls.get("website")
                        if website_url:
                            st.link_button(
                                "🌍 Website Pessoal", 
                                website_url, 
                                use_container_width=True
                            )
                        else:
                            st.button(
                                "🌍 Website - Não encontrado", 
                                disabled=True, 
                                use_container_width=True
                            )
                        
                        # Botão LinkedIn
                        linkedin_url = urls.get("linkedin")
                        if linkedin_url:
                            st.link_button(
                                "💼 LinkedIn", 
                                linkedin_url, 
                                use_container_width=True
                            )
                        else:
                            st.button(
                                "💼 LinkedIn - Não encontrado", 
                                disabled=True, 
                                use_container_width=True
                            )
                        
                        # Exibe o resumo textual da presença online
                        st.info(result.web_presence_analysis)

                    # ---------------------------------------------------------
                    # COLUNA DIREITA: DETALHES DA ANÁLISE
                    # ---------------------------------------------------------
                    
                    with col_details:
                        # Card de análise de compatibilidade
                        st.markdown(f"""
                        <div class="css-card">
                            <h3 style="margin-top:0;">📊 Análise de Compatibilidade</h3>
                            <p style="color:#444;">{result.match_analysis}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # -------------------------------------------------
                        # SKILLS QUE DÃO MATCH (Tags azuis)
                        # -------------------------------------------------
                        
                        st.markdown("### ✅ Stack Match (Requisitos Atendidos)")
                        skills_html = ""
                        # Combina linguagens + frameworks
                        for s in result.skills.languages + result.skills.frameworks:
                            skills_html += f'<span class="skill-tag">{s}</span>'
                        st.markdown(
                            f'<div class="css-card">{skills_html}</div>', 
                            unsafe_allow_html=True
                        )

                        # -------------------------------------------------
                        # GAPS - SKILLS FALTANTES (Tags vermelhas)
                        # -------------------------------------------------
                        # Só exibe se houver gaps identificados
                        
                        if result.missing_skills:
                            st.markdown("### ⚠️ Gaps (Faltantes)")
                            missing_html = ""
                            for gap in result.missing_skills:
                                missing_html += f'<span class="missing-tag">{gap}</span>'
                            st.markdown(
                                f'<div class="css-card">{missing_html}</div>', 
                                unsafe_allow_html=True
                            )

                        # -------------------------------------------------
                        # ARSENAL TÉCNICO COMPLETO (Tags cinzas)
                        # -------------------------------------------------
                        # Mostra todas as skills detectadas, não apenas
                        # as que a vaga pede. Limitado a 20 para não poluir.
                        
                        st.markdown("### 🛠️ Arsenal Técnico Completo (Detectado)")
                        full_stack_html = ""
                        for skill in result.detected_hard_skills[:20]:
                            full_stack_html += f'<span class="skill-tag-gray">{skill}</span>'
                        st.markdown(
                            f'<div class="css-card">{full_stack_html}</div>', 
                            unsafe_allow_html=True
                        )

                    # =========================================================
                    # ETAPA 6: SEÇÃO DE ENTREVISTA
                    # =========================================================
                    # Perguntas geradas pelo LLM baseadas nos gaps e
                    # pontos fortes do candidato
                    # =========================================================
                    
                    st.markdown("---")
                    st.subheader("🎤 Modo Entrevista (Sugestões de Perguntas)")
                    
                    # Cada pergunta em um expander colapsável
                    for i, q in enumerate(result.interview_questions):
                        # Título mostra dificuldade e preview da pergunta
                        with st.expander(
                            f"Pergunta {i+1}: {q.difficulty} ({q.question[:50]}...)"
                        ):
                            st.markdown(f"**Pergunta:** {q.question}")
                            st.markdown(
                                f"**O que esperar na resposta:** {q.expected_answer_topic}"
                            )

                except Exception as e:
                    # =========================================================
                    # TRATAMENTO DE ERROS
                    # =========================================================
                    # Captura qualquer exceção e exibe de forma amigável
                    # O traceback completo ajuda no debugging
                    # =========================================================
                    
                    st.error(f"Erro: {e}")
                    import traceback
                    st.code(traceback.format_exc())
                    
                finally:
                    # =========================================================
                    # LIMPEZA: DELETAR ARQUIVO TEMPORÁRIO
                    # =========================================================
                    # Sempre executa, mesmo se houver erro
                    # Evita acúmulo de arquivos temporários no servidor
                    # =========================================================
                    
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)


# ==============================================================================
# PONTO DE ENTRADA
# ==============================================================================
# Este bloco só executa quando rodamos o arquivo diretamente:
#   streamlit run src/app.py
#
# Não executa quando o módulo é importado por outro arquivo.
# ==============================================================================

if __name__ == "__main__":
    main()
