import os
import pandas as pd
import glob
from datetime import datetime
import re

def extract_csv_schemas(folder_path, output_file, sample_rows=5):
    """
    Extrai os esquemas (estrutura e amostra de dados) de todos os arquivos CSV
    em uma pasta e salva em formato markdown.
    
    Args:
        folder_path (str): Caminho para a pasta com os arquivos CSV
        output_file (str): Caminho para o arquivo markdown de saída
        sample_rows (int): Número de linhas de amostra a serem incluídas
    """
    # Garantir que o caminho termina com separador
    if not folder_path.endswith(os.sep):
        folder_path += os.sep
    
    # Encontrar todos os arquivos CSV na pasta
    csv_files = glob.glob(folder_path + "*.csv")
    
    if not csv_files:
        print(f"Nenhum arquivo CSV encontrado em {folder_path}")
        return
    
    print(f"Encontrados {len(csv_files)} arquivos CSV para análise.")
    
    # Iniciar o conteúdo markdown
    markdown_content = f"""# Documentação de Esquemas CSV
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Este documento contém a estrutura e amostras de dados de {len(csv_files)} arquivos CSV extraídos.

## Índice

"""
    
    # Criar índice
    for i, file_path in enumerate(sorted(csv_files), 1):
        file_name = os.path.basename(file_path)
        safe_link = re.sub(r'[^a-zA-Z0-9]', '-', file_name.lower())
        markdown_content += f"{i}. [{file_name}](#{safe_link})\n"
    
    markdown_content += "\n---\n\n"
    
    # Processar cada arquivo
    for file_path in sorted(csv_files):
        file_name = os.path.basename(file_path)
        safe_anchor = re.sub(r'[^a-zA-Z0-9]', '-', file_name.lower())
        
        print(f"Processando: {file_name}")
        
        try:
            # Tentar diferentes encodings
            for encoding in ['utf-8', 'latin1', 'cp1252']:
                try:
                    # Ler o cabeçalho primeiro
                    df_header = pd.read_csv(file_path, nrows=0, encoding=encoding)
                    # Se não deu erro, ler algumas linhas para amostra
                    df = pd.read_csv(file_path, nrows=sample_rows, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Erro ao tentar encoding {encoding} para {file_name}: {e}")
            
            # Contar as linhas sem carregar todo o arquivo na memória
            row_count = 0
            with open(file_path, 'r', encoding=encoding) as f:
                for _ in f:
                    row_count += 1
            row_count -= 1  # Descontar o cabeçalho
            
            # Obter informações sobre as colunas
            columns = df.columns.tolist()
            column_types = df.dtypes.tolist()
            
            # Adicionar detalhes do arquivo ao markdown
            markdown_content += f"## <a id='{safe_anchor}'></a>{file_name}\n\n"
            markdown_content += f"**Total de Registros**: {row_count:,}\n\n"
            markdown_content += f"**Total de Colunas**: {len(columns)}\n\n"
            
            # Tabela de esquema
            markdown_content += "### Esquema\n\n"
            markdown_content += "| # | Nome da Coluna | Tipo de Dados | Exemplo |\n"
            markdown_content += "|---|--------------|--------------|---------|\n"
            
            for i, (col, dtype) in enumerate(zip(columns, column_types), 1):
                # Obter um exemplo de valor não nulo se possível
                sample_values = df[col].dropna()
                example = str(sample_values.iloc[0]) if not sample_values.empty else "NULL"
                
                # Limitar o tamanho do exemplo para não quebrar o layout
                if len(example) > 50:
                    example = example[:47] + "..."
                
                # Escapar caracteres especiais do markdown
                example = example.replace("|", "\\|").replace("\n", " ")
                col_name = col.replace("|", "\\|")
                
                markdown_content += f"| {i} | {col_name} | {dtype} | {example} |\n"
            
            # Tabela de amostra de dados
            if not df.empty:
                markdown_content += "\n### Amostra de Dados\n\n"
                
                # Converter DataFrame para markdown
                # Limitar a largura das colunas para tabela legível
                with pd.option_context('display.max_colwidth', 50):
                    df_markdown = df.head(sample_rows).to_markdown(index=False)
                    markdown_content += df_markdown.replace("\n", "  \n")  # Garantir quebras de linha corretas
            
            markdown_content += "\n\n---\n\n"
            
        except Exception as e:
            print(f"Erro ao processar arquivo {file_name}: {e}")
            markdown_content += f"## <a id='{safe_anchor}'></a>{file_name}\n\n"
            markdown_content += f"**ERRO**: {str(e)}\n\n---\n\n"
    
    # Adicionar metadados finais
    markdown_content += f"""## Informações da Extração

- **Data e Hora**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
- **Diretório**: {os.path.abspath(folder_path)}
- **Total de Arquivos**: {len(csv_files)}
"""
    
    # Escrever conteúdo no arquivo de saída
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Documento markdown gerado com sucesso: {output_file}")
    
    # Retornar estatísticas básicas
    return {
        'total_files': len(csv_files),
        'output_file': output_file,
        'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }

def interactive_mode():
    """
    Executa o script em modo interativo
    """
    print("=== Extrator de Esquemas CSV para Markdown ===")
    
    folder_path = input("Digite o caminho para a pasta com os arquivos CSV: ")
    while not os.path.isdir(folder_path):
        print("Pasta não encontrada. Tente novamente.")
        folder_path = input("Digite o caminho para a pasta com os arquivos CSV: ")
    
    output_file = input("Nome do arquivo markdown de saída (padrão: esquemas_csv.md): ")
    output_file = output_file.strip() if output_file.strip() else "esquemas_csv.md"
    
    sample_rows = input("Número de linhas de amostra a incluir (padrão: 5): ")
    sample_rows = int(sample_rows) if sample_rows.strip().isdigit() else 5
    
    stats = extract_csv_schemas(folder_path, output_file, sample_rows)
    
    if stats:
        print("\n=== Extração Concluída ===")
        print(f"- Total de arquivos processados: {stats['total_files']}")
        print(f"- Documento gerado: {stats['output_file']}")
        print(f"- Concluído em: {stats['generated_at']}")
        print("\nO documento markdown contém:")
        print("- Índice completo com links para cada tabela")
        print("- Esquema detalhado de cada arquivo CSV")
        print("- Amostras de dados de cada tabela")
        print("- Contagem de registros e colunas")

if __name__ == "__main__":
    interactive_mode()