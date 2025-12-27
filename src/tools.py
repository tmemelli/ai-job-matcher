import requests
from typing import Dict, Any
# MUDANÇA: Importando a biblioteca oficial diretamente, não via LangChain
from duckduckgo_search import DDGS

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
    Realiza uma busca na web (DuckDuckGo) para encontrar referências do candidato.
    Usa a implementação nativa (DDGS) para evitar erros de versão do LangChain.
    """
    print(f"🌍 TOOL WEB SEARCH: Pesquisando '{query_name}'...")
    try:
        # Usando a lib nativa diretamente (mais estável)
        results = []
        with DDGS() as ddgs:
            # Busca 3 resultados
            raw_results = list(ddgs.text(f"{query_name} developer linkedin portfolio", max_results=3))
            for res in raw_results:
                results.append(f"- Título: {res['title']}\n  Link: {res['href']}\n  Resumo: {res['body']}")
        
        if not results:
            return "Nenhum resultado relevante encontrado online."
            
        return "\n\n".join(results)
        
    except Exception as e:
        return f"Erro na busca web: {e}"

# Teste rápido
if __name__ == "__main__":
    print(search_candidate_online("Thiago Memelli"))