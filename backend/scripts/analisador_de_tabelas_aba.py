import os
import pandas as pd
import re
import glob
from tabulate import tabulate

def analyze_csv_folder(folder_path, search_term=None, search_in_data=False, max_rows_to_check=1000):
    """
    Analisa todos os arquivos CSV em uma pasta e busca por termos específicos
    nos nomes das colunas ou nos dados (opcional).
    
    Args:
        folder_path (str): Caminho para a pasta com os arquivos CSV
        search_term (str, optional): Termo a ser buscado (pode ser uma expressão regular)
        search_in_data (bool): Se True, também busca no conteúdo dos arquivos
        max_rows_to_check (int): Número máximo de linhas a verificar quando search_in_data=True
    
    Returns:
        dict: Resultados da análise
    """
    # Garantir que o caminho termina com separador
    if not folder_path.endswith(os.sep):
        folder_path += os.sep
    
    # Encontrar todos os arquivos CSV na pasta
    csv_files = glob.glob(folder_path + "*.csv")
    
    if not csv_files:
        print(f"Nenhum arquivo CSV encontrado em {folder_path}")
        return {}
    
    print(f"Encontrados {len(csv_files)} arquivos CSV para análise.")
    
    results = {}
    
    # Compilar o padrão regex se um termo de busca foi fornecido
    pattern = re.compile(search_term, re.IGNORECASE) if search_term else None
    
    # Analisar cada arquivo
    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        try:
            # Tentar diferentes delimitadores e encodings comuns
            for encoding in ['utf-8', 'latin1', 'cp1252']:
                try:
                    # Primeiro tentar ler apenas o cabeçalho para economizar memória
                    df = pd.read_csv(file_path, nrows=0, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Erro ao tentar encoding {encoding} para {file_name}: {e}")
            
            columns = list(df.columns)
            num_rows = 0
            
            # Contar as linhas sem carregar todo o arquivo na memória
            with open(file_path, 'r', encoding=encoding) as f:
                for _ in f:
                    num_rows += 1
            num_rows -= 1  # Desconsiderar linha de cabeçalho
            
            # Verificar se o termo de busca está nas colunas
            if search_term:
                matching_columns = [col for col in columns if pattern.search(col)]
            else:
                matching_columns = columns
            
            # Buscar nos dados, se solicitado
            matching_data = {}
            if search_term and search_in_data:
                try:
                    # Carregar parte do CSV para verificar os dados
                    df_sample = pd.read_csv(file_path, nrows=min(max_rows_to_check, num_rows), encoding=encoding)
                    
                    # Verificar cada coluna
                    for col in columns:
                        try:
                            # Converter para string para garantir que podemos buscar
                            # Ignorar NaN/None values
                            col_data = df_sample[col].astype(str).replace('nan', '')
                            matches = col_data.str.contains(search_term, case=False, regex=True, na=False)
                            match_count = matches.sum()
                            
                            if match_count > 0:
                                matching_data[col] = match_count
                        except Exception as e:
                            print(f"Erro ao analisar coluna {col} em {file_name}: {e}")
                except Exception as e:
                    print(f"Erro ao buscar nos dados de {file_name}: {e}")
            
            # Salvar resultados
            results[file_name] = {
                'total_columns': len(columns),
                'total_rows': num_rows,
                'columns': columns,
                'matching_columns': matching_columns,
                'matching_data': matching_data
            }
            
        except Exception as e:
            print(f"Erro ao analisar o arquivo {file_name}: {e}")
            results[file_name] = {'error': str(e)}
    
    return results

def print_summary(results, search_term=None):
    """
    Imprime um resumo da análise em formato tabular
    """
    if not results:
        print("Nenhum resultado para exibir.")
        return
    
    # Preparar dados para tabela de resumo
    summary_data = []
    
    for file_name, data in results.items():
        if 'error' in data:
            summary_data.append([
                file_name, 
                "ERRO", 
                "ERRO", 
                data['error'],
                ""
            ])
        else:
            matching_cols = ", ".join(data['matching_columns']) if len(data['matching_columns']) <= 3 else \
                            f"{', '.join(data['matching_columns'][:3])} + {len(data['matching_columns']) - 3} mais"
            
            matching_data_info = ""
            if search_term and data['matching_data']:
                matching_data_items = [f"{col} ({count})" for col, count in data['matching_data'].items()]
                matching_data_info = ", ".join(matching_data_items) if len(matching_data_items) <= 3 else \
                                    f"{', '.join(matching_data_items[:3])} + {len(matching_data_items) - 3} mais"
            
            summary_data.append([
                file_name,
                data['total_rows'],
                data['total_columns'],
                matching_cols,
                matching_data_info
            ])
    
    # Definir cabeçalho da tabela
    headers = ["Arquivo", "Linhas", "Colunas", "Colunas Encontradas", "Matches nos Dados"]
    
    # Imprimir tabela
    print(tabulate(summary_data, headers=headers, tablefmt="grid"))

def export_results(results, output_file):
    """
    Exporta os resultados detalhados para um arquivo CSV
    """
    output_data = []
    
    for file_name, data in results.items():
        if 'error' in data:
            row = {
                'arquivo': file_name,
                'total_linhas': 'ERRO',
                'total_colunas': 'ERRO',
                'coluna': 'ERRO',
                'encontrado_em': 'coluna',
                'contagem_matches': 0,
                'erro': data['error']
            }
            output_data.append(row)
        else:
            # Adicionar entrada para cada coluna
            for col in data['columns']:
                found_in_col = col in data['matching_columns']
                found_in_data = col in data.get('matching_data', {})
                match_count = data.get('matching_data', {}).get(col, 0)
                
                row = {
                    'arquivo': file_name,
                    'total_linhas': data['total_rows'],
                    'total_colunas': data['total_columns'],
                    'coluna': col,
                    'encontrado_em': 'coluna e dados' if found_in_col and found_in_data else 
                                     'coluna' if found_in_col else 
                                     'dados' if found_in_data else 
                                     'não encontrado',
                    'contagem_matches': match_count,
                    'erro': ''
                }
                output_data.append(row)
    
    # Criar DataFrame e exportar
    df = pd.DataFrame(output_data)
    df.to_csv(output_file, index=False)
    print(f"Resultados exportados para {output_file}")

def interactive_mode():
    """
    Executa o script em modo interativo
    """
    print("=== Analisador de Arquivos CSV ===")
    
    folder_path = input("Digite o caminho para a pasta com os arquivos CSV: ")
    while not os.path.isdir(folder_path):
        print("Pasta não encontrada. Tente novamente.")
        folder_path = input("Digite o caminho para a pasta com os arquivos CSV: ")
    
    search_term = input("Digite o termo a ser buscado (deixe em branco para listar todas as colunas): ")
    search_term = search_term if search_term.strip() else None
    
    search_in_data = input("Buscar também nos dados? (s/n, padrão: n): ").lower() == 's'
    
    if search_in_data:
        max_rows = input("Número máximo de linhas a verificar (padrão: 1000): ")
        max_rows = int(max_rows) if max_rows.strip().isdigit() else 1000
    else:
        max_rows = 1000
    
    results = analyze_csv_folder(folder_path, search_term, search_in_data, max_rows)
    print_summary(results, search_term)
    
    export_option = input("Exportar resultados detalhados para CSV? (s/n): ").lower()
    if export_option == 's':
        output_file = input("Nome do arquivo de saída (padrão: resultados_analise.csv): ")
        output_file = output_file if output_file.strip() else "resultados_analise.csv"
        export_results(results, output_file)

if __name__ == "__main__":
    interactive_mode()