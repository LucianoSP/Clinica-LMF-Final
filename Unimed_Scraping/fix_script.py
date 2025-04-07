with open('captura_guias_via_pdf.py', 'r') as file:
    content = file.read()

# Corrigir parênteses problemáticos
fixed_content = content.replace('           ))\n', '           )\n')
fixed_content = fixed_content.replace('                ))\n', '                )\n')
fixed_content = fixed_content.replace('            ))\n', '            )\n')
fixed_content = fixed_content.replace('\n                ))', '\n                )')
fixed_content = fixed_content.replace('\n            ))', '\n            )')

with open('captura_guias_via_pdf_fixed.py', 'w') as file:
    file.write(fixed_content)

print("Arquivo corrigido salvo como captura_guias_via_pdf_fixed.py") 