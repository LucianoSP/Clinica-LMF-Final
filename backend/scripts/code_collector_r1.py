import os
from pathlib import Path

def read_files_to_single_output(root_dir, output_file='codigo_completo.txt'):
    # Configurações
    target_dirs = ['backend', 'frontend/src', 'sql']
    exclude_dirs = ['node_modules', '.next', 'venv', '__pycache__', '.git']
    exclude_ext = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.env', '.lock', '.gitignore']
    root_files_include = ['app.py', 'database_supabase.py', 'config.py']
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("=== Estrutura do Arquivo ===\n")
        outfile.write(f"Projeto: {os.path.basename(Path(root_dir).resolve())}\n\n")
        
        # Coletar arquivos relevantes
        all_files = []
        
        # Processar arquivos específicos na raiz
        for file in root_files_include:
            if os.path.isfile(os.path.join(root_dir, file)):
                all_files.append(file)
        
        # Processar pastas alvo
        for folder in target_dirs:
            folder_path = os.path.join(root_dir, folder)
            if not os.path.exists(folder_path):
                continue
                
            for root, dirs, files in os.walk(folder_path):
                # Filtrar diretórios
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_dir)
                    
                    # Pular arquivos excluídos
                    if any(file.endswith(ext) for ext in exclude_ext):
                        continue
                        
                    all_files.append(rel_path)

        # Escrever lista de arquivos
        outfile.write("Arquivos incluídos:\n")
        for file in sorted(all_files):
            outfile.write(f"- {file}\n")
        
        # Escrever conteúdo dos arquivos
        outfile.write("\n\n=== Conteúdo dos Arquivos ===\n\n")
        
        # Escrever arquivos específicos da raiz primeiro
        for file in root_files_include:
            file_path = os.path.join(root_dir, file)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(f"\n=== {file} ===\n")
                        outfile.write(content + "\n")
                except Exception as e:
                    print(f"Erro ao ler {file}: {str(e)}")
        
        # Escrever conteúdo das pastas
        for folder in target_dirs:
            folder_path = os.path.join(root_dir, folder)
            if not os.path.exists(folder_path):
                continue
                
            for root, dirs, files in os.walk(folder_path):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_dir)
                    
                    if any(file.endswith(ext) for ext in exclude_ext):
                        continue
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(f"\n=== {rel_path} ===\n")
                            outfile.write(content + "\n")
                    except UnicodeDecodeError:
                        print(f"Ignorando arquivo binário: {rel_path}")
                    except Exception as e:
                        print(f"Erro ao ler {rel_path}: {str(e)}")

if __name__ == "__main__":
    project_root = os.getcwd()
    read_files_to_single_output(project_root)
    print("Arquivo de código completo gerado com sucesso!")