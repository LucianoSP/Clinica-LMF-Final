#!/usr/bin/env python3
"""
Script para aplicar as adaptações ao script original todas_as_fases_windows_final_com_execucoes.py
"""
import os
import re
import shutil
from datetime import datetime

# Caminhos dos arquivos
SCRIPT_ORIGINAL = "todas_as_fases_windows_final_com_execucoes.py"
ADAPTACOES = "adaptacoes_unimed_sessoes.py"
SCRIPT_ADAPTADO = "todas_as_fases_adaptado.py"

def backup_original():
    """Cria um backup do script original"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{SCRIPT_ORIGINAL}.bak_{timestamp}"
    shutil.copy2(SCRIPT_ORIGINAL, backup_file)
    print(f"Backup do script original criado em: {backup_file}")
    return backup_file

def ler_adaptacoes():
    """Lê as adaptações a serem aplicadas"""
    with open(ADAPTACOES, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrair os diferentes blocos de adaptação
    save_unimed_execution = re.search(
        r'def save_unimed_execution\(self.*?return False\n\n',
        content, re.DOTALL
    ).group(0)
    
    verificar_processamento = re.search(
        r'def verificar_processamento_sessoes\(self.*?print\(f"Erro ao verificar processamento: \{str\(e\)\}"\)\n\n',
        content, re.DOTALL
    ).group(0)
    
    save_to_supabase = re.search(
        r'def save_to_supabase\(self.*?self\.verificar_processamento_sessoes\(\)\n\n',
        content, re.DOTALL
    ).group(0)
    
    return {
        'save_unimed_execution': save_unimed_execution,
        'verificar_processamento': verificar_processamento,
        'save_to_supabase': save_to_supabase,
    }

def ler_script_original():
    """Lê o conteúdo do script original"""
    with open(SCRIPT_ORIGINAL, 'r', encoding='utf-8') as f:
        return f.read()

def aplicar_adaptacoes(original_content, adaptacoes):
    """Aplica as adaptações ao conteúdo original"""
    # Substitui o método save_unimed_execution
    modified_content = re.sub(
        r'def save_unimed_execution\(self.*?return False(\n\s*)',
        adaptacoes['save_unimed_execution'],
        original_content, 
        flags=re.DOTALL
    )
    
    # Adiciona o novo método verificar_processamento_sessoes antes do método close
    modified_content = re.sub(
        r'(\s*)def close\(self\):',
        f"\n{adaptacoes['verificar_processamento']}\n\\1def close(self):",
        modified_content
    )
    
    # Modifica o método save_to_supabase
    # Primeiro, encontramos o fim do método para adicionar a chamada ao novo método
    save_to_supabase_pattern = r'def save_to_supabase\(self, guide_details_list\):.*?(?=\n\s*def |\n\s*$)'
    save_to_supabase_match = re.search(save_to_supabase_pattern, modified_content, re.DOTALL)
    
    if save_to_supabase_match:
        original_method = save_to_supabase_match.group(0)
        # Adiciona a linha para chamar o método verificar_processamento_sessoes no final
        if "verificar_processamento_sessoes" not in original_method:
            modified_method = original_method + "\n        # Após processar todas as guias, verificar o status das sessões\n        self.verificar_processamento_sessoes()"
            modified_content = modified_content.replace(original_method, modified_method)
    
    # Adiciona import datetime se necessário
    if "from datetime import datetime" not in modified_content and "import datetime" not in modified_content:
        modified_content = re.sub(
            r'import time\n',
            'import time\nfrom datetime import datetime\n',
            modified_content
        )
    
    return modified_content

def salvar_script_adaptado(content):
    """Salva o script adaptado"""
    with open(SCRIPT_ADAPTADO, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Script adaptado salvo em: {SCRIPT_ADAPTADO}")

def main():
    """Função principal"""
    print("Iniciando processo de adaptação do script...")
    
    # Verifica se os arquivos existem
    if not os.path.exists(SCRIPT_ORIGINAL):
        print(f"Erro: Arquivo original {SCRIPT_ORIGINAL} não encontrado.")
        return
    
    if not os.path.exists(ADAPTACOES):
        print(f"Erro: Arquivo de adaptações {ADAPTACOES} não encontrado.")
        return
    
    # Faz backup do script original
    backup_file = backup_original()
    
    try:
        # Lê adaptações
        adaptacoes = ler_adaptacoes()
        
        # Lê script original
        original_content = ler_script_original()
        
        # Aplica adaptações
        modified_content = aplicar_adaptacoes(original_content, adaptacoes)
        
        # Salva script adaptado
        salvar_script_adaptado(modified_content)
        
        print(f"""
Adaptações aplicadas com sucesso!

As seguintes alterações foram realizadas:
1. Substituído o método save_unimed_execution para usar a tabela intermediária
2. Adicionado o método verificar_processamento_sessoes para gerar estatísticas
3. Modificado o método save_to_supabase para chamar a verificação no final

Para testar o script adaptado:
python {SCRIPT_ADAPTADO}

Se precisar restaurar o original:
copy {backup_file} {SCRIPT_ORIGINAL}
""")
    
    except Exception as e:
        print(f"Erro ao aplicar adaptações: {str(e)}")
        print(f"O script original não foi modificado. Você pode usar o backup em: {backup_file}")

if __name__ == "__main__":
    main() 