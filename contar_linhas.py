import os
from pathlib import Path

def contar_linhas_codigo(pasta, extensoes=None, ignorar_diretorios=None):
    """
    Conta linhas de código em uma pasta específica.
    
    Args:
        pasta (str): Caminho da pasta a ser analisada
        extensoes (list): Lista de extensões de arquivo para contar
        ignorar_diretorios (list): Lista de diretórios para ignorar
    """
    if extensoes is None:
        extensoes = ['.py']  # para backend
    
    if ignorar_diretorios is None:
        ignorar_diretorios = [
            'venv', 
            'env', 
            '__pycache__', 
            'node_modules',
            '.git',
            'migrations'
        ]

    total_linhas = 0
    arquivos_analisados = 0
    
    for raiz, dirs, arquivos in os.walk(pasta):
        # Remove diretórios que devem ser ignorados
        dirs[:] = [d for d in dirs if d not in ignorar_diretorios]
        
        for arquivo in arquivos:
            if any(arquivo.endswith(ext) for ext in extensoes):
                caminho_completo = os.path.join(raiz, arquivo)
                try:
                    with open(caminho_completo, 'r', encoding='utf-8') as f:
                        # Conta apenas linhas não vazias e não comentários
                        linhas = [linha.strip() for linha in f if linha.strip() and not linha.strip().startswith('#')]
                        num_linhas = len(linhas)
                        total_linhas += num_linhas
                        arquivos_analisados += 1
                        print(f"Arquivo: {caminho_completo} - {num_linhas} linhas")
                except Exception as e:
                    print(f"Erro ao ler arquivo {caminho_completo}: {e}")
    
    return total_linhas, arquivos_analisados

# Função para contar código do backend (Python)
def contar_backend():
    pasta_backend = './backend'  # ajuste o caminho conforme necessário
    extensoes = ['.py']
    total_linhas, total_arquivos = contar_linhas_codigo(pasta_backend, extensoes)
    print(f"\nBackend:")
    print(f"Total de arquivos Python: {total_arquivos}")
    print(f"Total de linhas de código: {total_linhas}")
    return total_linhas

# Função para contar código do frontend
def contar_frontend():
    pasta_frontend = './frontend'  # ajuste o caminho conforme necessário
    extensoes = ['.js', '.jsx', '.ts', '.tsx', '.vue', '.css', '.scss']
    total_linhas, total_arquivos = contar_linhas_codigo(pasta_frontend, extensoes)
    print(f"\nFrontend:")
    print(f"Total de arquivos: {total_arquivos}")
    print(f"Total de linhas de código: {total_linhas}")
    return total_linhas

if __name__ == "__main__":
    print("Analisando código...")
    backend_linhas = contar_backend()
    frontend_linhas = contar_frontend()
    
    print(f"\nResumo Total:")
    print(f"Total geral de linhas: {backend_linhas + frontend_linhas}")