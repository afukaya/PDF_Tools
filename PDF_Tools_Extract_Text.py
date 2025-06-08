#
# Extracts text from a PDF File.
# By ChatGPT.

import PyPDF2

def extrair_texto_pdf(caminho_arquivo):
    # Abrindo o arquivo PDF em modo binário
    with open(caminho_arquivo, 'rb') as arquivo:
        leitor_pdf = PyPDF2.PdfReader(arquivo)
        
        # Inicializando uma string para armazenar todo o texto
        texto_completo = ''
        
        # Iterando sobre cada página do PDF
        for numero_pagina in range(len(leitor_pdf.pages)):
            pagina = leitor_pdf.pages[numero_pagina]
            print('Pagina: ')
            print(pagina.extract_text())
            print('\n--------------------------------\n')

# Exemplo de uso
caminho_do_pdf = 'file.pdf'  # Substitua pelo caminho do seu arquivo PDF
extrair_texto_pdf(caminho_do_pdf)
