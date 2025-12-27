import os
import requests
from typing import Dict, Any
from tavily import TavilyClient

def fetch_github_profile(username: str) -> Dict[str, Any]:
    """
    Busca dados do perfil público e estatísticas de repositórios de um usuário no GitHub.
    """
    print(f"🔧 TOOL GITHUB: Buscando dados para '{username}'...")
    
    # 1. Buscar Perfil do Usuário
    user_url = f"https://api.github.com/users/{username}"
    user_response = requests.get(user_url)
    
    if user_response.status_code != 200:
        return {"error": "Usuário GitHub não encontrado"}
        
    user_data = user_response.json()
    
    # 2. Buscar Repositórios (Top 5)
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
    repos_response = requests.get(repos_url)
    repos_data = repos_response.json()
    
    # 3. Resumir Repositórios
    repo_summaries = []
    if isinstance(repos_data, list):
        for repo in repos_data:
            repo_summaries.append({
                "name": repo.get("name"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "description": repo.get("description")
            })
            
    return {
        "username": user_data.get("login"),
        "bio": user_data.get("bio"),
        "company": user_data.get("company"),
        "blog": user_data.get("blog"),
        "public_repos": user_data.get("public_repos"),
        "followers": user_data.get("followers"),
        "recent_projects": repo_summaries
    }

def search_candidate_online(query_name: str) -> str:
    """
    Realiza uma busca profissional na web usando Tavily API.
    Totalmente genérica: Funciona para qualquer cargo ou área.
    """
    print(f"🌍 TOOL WEB SEARCH (TAVILY): Pesquisando '{query_name}'...")
    
    try:
        # Pega a chave do ambiente
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Erro: TAVILY_API_KEY não encontrada."

        client = TavilyClient(api_key=api_key)
        
        search_query = f"{query_name} linkedin personal website professional profile github portfolio homepage"
        
        response = client.search(
            query=search_query,
            search_depth="advanced",
            max_results=10
        )
        
        results = []
        if 'results' in response and response['results']:
            for res in response['results']:
                results.append(f"- Título: {res.get('title')}\n  Link: {res.get('url')}\n  Conteúdo: {res.get('content')}")
            
            return "\n\n".join(results)
            
        return "Nenhum resultado relevante encontrado online."

    except Exception as e:
        return f"Erro na busca web (Tavily): {str(e)}"

# Teste rápido
if __name__ == "__main__":
    # Carrega env vars se estiver rodando localmente apenas o arquivo tools.py
    from dotenv import load_dotenv
    load_dotenv()
    print(search_candidate_online("Thiago Memelli"))