"""
================================================================================
                        🔧 TOOLS.PY - AS FERRAMENTAS DO AGENTE
================================================================================

Este módulo contém as FERRAMENTAS (tools) que o agente utiliza para coletar
dados externos sobre candidatos. Pense nelas como os "sentidos" do agente —
são elas que permitem ao sistema "ver" além do PDF do currículo.

CONCEITO DE TOOLS EM AGENTES DE IA:
    Em arquiteturas de agentes autônomos, "tools" são funções que o LLM pode
    invocar para interagir com o mundo externo. O LLM decide QUANDO e COMO
    usar cada ferramenta baseado no contexto da tarefa.
    
    Neste projeto, as tools são chamadas diretamente pelo código (não via
    function calling), mas a arquitetura permite fácil migração para
    frameworks como LangChain ou OpenAI Assistants API.

FERRAMENTAS DISPONÍVEIS:
    1. fetch_github_profile() - Coleta dados da API do GitHub
    2. search_candidate_online() - Busca presença web via Tavily API

FLUXO DE DADOS:
    ┌─────────────┐
    │  agent.py   │
    │  (cérebro)  │
    └──────┬──────┘
           │ Chama as tools
           ▼
    ┌─────────────────────────────────────────────────────┐
    │                    tools.py                         │
    │  ┌─────────────────┐    ┌─────────────────────────┐ │
    │  │ GitHub API      │    │ Tavily API              │ │
    │  │                 │    │                         │ │
    │  │ • Perfil        │    │ • LinkedIn              │ │
    │  │ • Bio           │    │ • Artigos               │ │
    │  │ • Repos         │    │ • Portfolio             │ │
    │  │ • Website       │    │ • Menções               │ │
    │  └────────┬────────┘    └────────────┬────────────┘ │
    │           │                          │              │
    └───────────┼──────────────────────────┼──────────────┘
                │                          │
                ▼                          ▼
         ┌─────────────┐           ┌─────────────┐
         │ GitHub.com  │           │ Web (Google)│
         │    API      │           │ via Tavily  │
         └─────────────┘           └─────────────┘

ESCALABILIDADE - ARQUITETURA DE PLUGINS:
    Este módulo foi projetado para ser EXTENSÍVEL. Para adicionar suporte
    a outros setores além de TI, basta criar novas funções seguindo o
    mesmo padrão:
    
    # Exemplo: Setor de Saúde
    def fetch_crm_profile(crm_number: str) -> Dict[str, Any]:
        '''Valida registro no Conselho Regional de Medicina'''
        ...
    
    # Exemplo: Setor Acadêmico
    def fetch_lattes_profile(lattes_id: str) -> Dict[str, Any]:
        '''Busca currículo na Plataforma Lattes'''
        ...

DEPENDÊNCIAS:
    - requests: Para chamadas HTTP à API do GitHub
    - tavily: Cliente oficial da API de busca Tavily
    - python-dotenv: Para carregar variáveis de ambiente

VARIÁVEIS DE AMBIENTE:
    - TAVILY_API_KEY: Chave da API Tavily (obrigatório para busca web)
    - GITHUB_TOKEN: Token do GitHub (opcional, aumenta rate limit)

AUTOR: Thiago Memelli
VERSÃO: 1.0.0
================================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import os                          # Acesso a variáveis de ambiente
import requests                    # Cliente HTTP para APIs REST
from typing import Dict, Any       # Type hints para melhor legibilidade

# Cliente oficial da Tavily - API de busca otimizada para agentes de IA
# Tavily é superior ao Google Search para agentes porque:
# 1. Retorna conteúdo limpo (sem HTML)
# 2. Otimizado para extração de informações
# 3. Pricing amigável para desenvolvedores
from tavily import TavilyClient


# ==============================================================================
# TOOL 1: GITHUB API
# ==============================================================================
# 
# Esta ferramenta acessa a API pública do GitHub para coletar informações
# sobre o perfil de um desenvolvedor. É especialmente útil para validar
# claims técnicos do currículo.
#
# ENDPOINTS UTILIZADOS:
#   - GET /users/{username} - Dados do perfil
#   - GET /users/{username}/repos - Lista de repositórios
#
# RATE LIMITS:
#   - Sem autenticação: 60 requests/hora
#   - Com token: 5.000 requests/hora
#
# DOCUMENTAÇÃO: https://docs.github.com/en/rest
# ==============================================================================


def fetch_github_profile(username: str) -> Dict[str, Any]:
    """
    Busca dados do perfil público e repositórios de um usuário no GitHub.
    
    Esta é uma das principais ferramentas de validação do agente. Ela permite
    verificar se o candidato realmente tem atividade no GitHub e quais
    tecnologias ele utiliza em seus projetos.
    
    Args:
        username: Username do GitHub (sem @).
                  Ex: "tmemelli", "torvalds", "gvanrossum"
    
    Returns:
        Dict contendo:
            - username (str): Username confirmado
            - bio (str | None): Biografia do perfil
            - company (str | None): Empresa atual
            - blog (str | None): Website pessoal (CAMPO IMPORTANTE!)
            - public_repos (int): Número total de repos públicos
            - followers (int): Número de seguidores
            - recent_projects (list): Lista dos 5 repos mais recentes
            
        Em caso de erro:
            - {"error": "Usuário GitHub não encontrado"}
    
    Example:
        >>> profile = fetch_github_profile("tmemelli")
        >>> print(profile["bio"])
        "Backend Developer | Python | AI Engineering"
        >>> print(profile["blog"])
        "https://thiagomemelli.com.br"
    
    Note:
        - O campo "blog" é onde usuários configuram seu website pessoal
        - Este campo é crucial para encontrar portfolios e sites pessoais
        - Sem autenticação, há limite de 60 requests/hora por IP
        
    API Reference:
        https://docs.github.com/en/rest/users/users#get-a-user
    """
    print(f"🔧 TOOL GITHUB: Buscando dados para '{username}'...")
    
    # ==========================================================================
    # ETAPA 1: BUSCAR DADOS DO PERFIL
    # ==========================================================================
    # Endpoint: GET /users/{username}
    # Retorna: bio, company, blog, location, followers, public_repos, etc.
    # ==========================================================================
    
    user_url = f"https://api.github.com/users/{username}"
    user_response = requests.get(user_url)
    
    # Verifica se o usuário existe
    # Status 200 = sucesso, 404 = não encontrado
    if user_response.status_code != 200:
        return {"error": "Usuário GitHub não encontrado"}
    
    # Parseia a resposta JSON
    user_data = user_response.json()
    
    # ==========================================================================
    # ETAPA 2: BUSCAR REPOSITÓRIOS RECENTES
    # ==========================================================================
    # Endpoint: GET /users/{username}/repos
    # Parâmetros:
    #   - sort=updated: Ordena por última atualização
    #   - per_page=5: Limita a 5 resultados (economiza bandwidth)
    # ==========================================================================
    
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
    repos_response = requests.get(repos_url)
    repos_data = repos_response.json()
    
    # ==========================================================================
    # ETAPA 3: PROCESSAR E RESUMIR REPOSITÓRIOS
    # ==========================================================================
    # Extraímos apenas os campos relevantes de cada repo:
    #   - name: Nome do projeto
    #   - language: Linguagem principal
    #   - stars: Indicador de popularidade
    #   - description: O que o projeto faz
    # ==========================================================================
    
    repo_summaries = []
    
    # Verifica se repos_data é uma lista (pode ser dict de erro em alguns casos)
    if isinstance(repos_data, list):
        for repo in repos_data:
            repo_summaries.append({
                "name": repo.get("name"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "description": repo.get("description")
            })
    
    # ==========================================================================
    # ETAPA 4: MONTAR E RETORNAR RESULTADO
    # ==========================================================================
    # Estruturamos os dados de forma que o LLM possa interpretar facilmente
    # ==========================================================================
    
    return {
        "username": user_data.get("login"),             # Username confirmado
        "bio": user_data.get("bio"),                    # Biografia/headline
        "company": user_data.get("company"),            # Empresa atual
        "blog": user_data.get("blog"),                  # ⭐ WEBSITE PESSOAL!
        "public_repos": user_data.get("public_repos"),  # Total de repos
        "followers": user_data.get("followers"),        # Seguidores
        "recent_projects": repo_summaries               # Top 5 projetos recentes
    }


# ==============================================================================
# TOOL 2: WEB SEARCH (TAVILY API)
# ==============================================================================
#
# Esta ferramenta realiza buscas na web para encontrar a presença online
# do candidato: LinkedIn, artigos publicados, menções em blogs, portfolios,
# participações em eventos, etc.
#
# POR QUE TAVILY E NÃO GOOGLE?
#   1. Tavily foi criado especificamente para agentes de IA
#   2. Retorna conteúdo limpo e estruturado (não HTML bruto)
#   3. Tem modo "advanced" que faz deep search
#   4. Pricing amigável: 1000 buscas/mês grátis
#   5. Não precisa parsear HTML ou lidar com CAPTCHAs
#
# FALLBACK:
#   Se TAVILY_API_KEY não estiver configurada, o sistema pode usar
#   DuckDuckGo como alternativa (implementado em versões anteriores).
#
# DOCUMENTAÇÃO: https://docs.tavily.com/
# ==============================================================================


def search_candidate_online(query_name: str) -> str:
    """
    Realiza busca profissional na web para encontrar presença online do candidato.
    
    Esta ferramenta é GENÉRICA e funciona para qualquer profissão, não apenas
    desenvolvedores. Ela busca por perfis profissionais, artigos, menções
    e qualquer rastro digital público do candidato.
    
    Args:
        query_name: Nome completo do candidato para busca.
                    Ex: "Thiago Memelli", "João Silva Developer"
    
    Returns:
        String formatada contendo os resultados da busca:
        - Título de cada resultado
        - URL do link
        - Snippet do conteúdo
        
        Em caso de erro:
        - Mensagem descritiva do erro
        
        Se não encontrar nada:
        - "Nenhum resultado relevante encontrado online."
    
    Example:
        >>> results = search_candidate_online("Thiago Memelli")
        >>> print(results)
        "- Título: Thiago Memelli | LinkedIn
           Link: https://linkedin.com/in/thiagomemelli
           Conteúdo: Backend Developer com experiência em Python..."
    
    Note:
        - Requer TAVILY_API_KEY configurada no ambiente
        - Usa search_depth="advanced" para resultados mais completos
        - Busca por: LinkedIn, GitHub, portfolio, website pessoal
        - Limite de 10 resultados por busca
        
    Search Strategy:
        A query é expandida com termos profissionais para melhorar relevância:
        "{nome} linkedin personal website professional profile github portfolio"
        
    API Reference:
        https://docs.tavily.com/docs/tavily-api/rest-api
    """
    print(f"🌍 TOOL WEB SEARCH (TAVILY): Pesquisando '{query_name}'...")
    
    try:
        # ======================================================================
        # ETAPA 1: OBTER E VALIDAR API KEY
        # ======================================================================
        # A chave da Tavily é necessária para autenticar as requisições
        # Sem ela, a busca web não funciona (mas o sistema continua
        # funcionando com os dados do GitHub e CV)
        # ======================================================================
        
        api_key = os.getenv("TAVILY_API_KEY")
        
        if not api_key:
            return "Erro: TAVILY_API_KEY não encontrada."
        
        # Inicializa o cliente Tavily com a API key
        client = TavilyClient(api_key=api_key)
        
        # ======================================================================
        # ETAPA 2: CONSTRUIR QUERY DE BUSCA
        # ======================================================================
        # Expandimos o nome do candidato com termos profissionais para
        # aumentar a chance de encontrar perfis relevantes.
        #
        # Termos adicionados:
        #   - linkedin: Perfil profissional
        #   - personal website: Site pessoal/portfolio
        #   - professional profile: Perfis em outras plataformas
        #   - github: Perfil de código (redundante mas útil)
        #   - portfolio: Trabalhos anteriores
        #   - homepage: Página pessoal
        # ======================================================================
        
        search_query = (
            f"{query_name} linkedin personal website "
            f"professional profile github portfolio homepage"
        )
        
        # ======================================================================
        # ETAPA 3: EXECUTAR BUSCA
        # ======================================================================
        # Parâmetros da busca:
        #   - query: A string de busca construída
        #   - search_depth: "advanced" = busca mais profunda (mais lenta)
        #   - max_results: Limita a 10 resultados
        # ======================================================================
        
        response = client.search(
            query=search_query,
            search_depth="advanced",  # Busca mais profunda
            max_results=10            # Top 10 resultados
        )
        
        # ======================================================================
        # ETAPA 4: PROCESSAR E FORMATAR RESULTADOS
        # ======================================================================
        # Transformamos a resposta da API em texto formatado que o LLM
        # pode facilmente interpretar e usar na análise.
        # ======================================================================
        
        results = []
        
        # Verifica se há resultados na resposta
        if 'results' in response and response['results']:
            for res in response['results']:
                # Formata cada resultado em um bloco de texto estruturado
                formatted_result = (
                    f"- Título: {res.get('title')}\n"
                    f"  Link: {res.get('url')}\n"
                    f"  Conteúdo: {res.get('content')}"
                )
                results.append(formatted_result)
            
            # Junta todos os resultados com linhas em branco entre eles
            return "\n\n".join(results)
        
        # Se não encontrou nenhum resultado
        return "Nenhum resultado relevante encontrado online."

    except Exception as e:
        # ======================================================================
        # TRATAMENTO DE ERROS
        # ======================================================================
        # Capturamos qualquer exceção para evitar que o sistema quebre.
        # O agente continua funcionando mesmo se a busca web falhar,
        # usando apenas os dados do CV e GitHub.
        # ======================================================================
        return f"Erro na busca web (Tavily): {str(e)}"


# ==============================================================================
# BLOCO DE TESTE LOCAL
# ==============================================================================
#
# Este bloco só é executado quando rodamos o arquivo diretamente:
#   python src/tools.py
#
# Útil para testar as ferramentas isoladamente durante o desenvolvimento.
# Não é executado quando o módulo é importado por agent.py.
# ==============================================================================

if __name__ == "__main__":
    # Carrega variáveis de ambiente do arquivo .env
    # Necessário apenas quando rodando o arquivo diretamente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Teste da função de busca web
    print("=" * 60)
    print("TESTE: search_candidate_online()")
    print("=" * 60)
    print(search_candidate_online("Thiago Memelli"))
    
    print("\n" + "=" * 60)
    print("TESTE: fetch_github_profile()")
    print("=" * 60)
    profile = fetch_github_profile("tmemelli")
    
    # Exibe os resultados de forma legível
    for key, value in profile.items():
        print(f"{key}: {value}")
