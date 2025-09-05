import fitz  # PyMuPDF
import re
import argparse
import os
import sys

def score_title(line_text, size, base_size, bold, underline):
    """Calcula a pontuação heurística de uma linha como título.

    Parâmetros:
    - line_text: texto da linha já concatenado.
    - size: maior tamanho de fonte encontrado na linha.
    - base_size: tamanho de fonte base (mais frequente no documento).
    - bold: se há indicação de fonte em negrito na linha.
    - underline: se há indicação de sublinhado na linha.

    Retorna:
    - int com a pontuação (quanto maior, mais provável ser título).
    """
    score = 0
    if size >= base_size + 4:
        score += 3
    elif size >= base_size + 2:
        score += 2
    elif size > base_size:
        score += 1
    if bold:
        score += 1
    if underline:
        score += 1
    upper_ratio = sum(1 for c in line_text if c.isupper()) / (len(line_text) + 0.1)
    if upper_ratio > 0.8 and len(line_text) > 4:
        score += 1
    if re.match(r"^(\d+(\.\d+)*(\s|-|—)+)", line_text) or re.match(r"^\d+\s+[A-Z]", line_text):
        score += 1
    if 3 < len(line_text.split()) < 10:
        score += 1
    return score

def score_to_md_level(score):
    """Converte a pontuação em um prefixo de título Markdown.

    Retorna um dos valores: "# ", "## ", "### ", "#### " ou string vazia.
    """
    if score >= 5:
        return "# "
    elif score >= 4:
        return "## "
    elif score >= 3:
        return "### "
    elif score >= 2:
        return "#### "
    else:
        return ""

def _collect_font_sizes(doc):
    """Percorre o documento e coleta os tamanhos de fonte de todos os spans.

    Parâmetros:
    - doc: objeto PyMuPDF (fitz.Document) já aberto.

    Retorna:
    - list[float] contendo os tamanhos de fonte encontrados.
    """
    sizes = []
    for page in doc:
        blocks = page.get_text("dict").get("blocks", [])
        for b in blocks:
            if b.get('type') != 0:
                continue
            for l in b.get("lines", []):
                for s in l.get("spans", []):
                    sizes.append(s.get("size", 0))
    return sizes

def _parse_line(line):
    """Extrai informações relevantes de uma linha (spans) do PyMuPDF.

    Parâmetros:
    - line: dicionário de linha retornado por page.get_text("dict").

    Retorna:
    - tuple(clean_text, max_size, bold, underline).
    """
    line_text = ""
    bold = False
    underline = False
    max_size = 0
    for s in line.get("spans", []):
        text = s.get('text', '')
        if text.strip() == '':
            continue
        if "Bold" in s.get('font', ''):
            bold = True
        if s.get('flags', 0) & 4:
            underline = True
        size = s.get('size', 0)
        if size > max_size:
            max_size = size
        line_text += text
    clean_text = re.sub(r'\s+', ' ', line_text).strip()
    return clean_text, max_size, bold, underline

def _md_from_line(clean_text, max_size, base_font_size, bold, underline, space_above):
    """Gera a linha final (Markdown ou texto simples) a partir da heurística.

    Retorna:
    - string com prefixo Markdown quando aplicável, texto simples caso contrário,
      ou None quando a linha não deve ser incluída (texto vazio).
    """
    if not clean_text:
        return None
    score = score_title(clean_text, max_size, base_font_size, bold, underline)
    if len(clean_text.split()) > 18:
        score = 0
    if space_above > 12:
        score += 1
    md_prefix = score_to_md_level(score)
    if md_prefix:
        return '\n' + md_prefix + clean_text + '\n'
    return clean_text

def extract_pdf_structure_advanced(pdf_path):
    """Extrai texto estruturado de um PDF e retorna em formato Markdown.

    Abre o PDF, estima o tamanho de fonte base, avalia cada linha com
    heurísticas de título e monta a saída com prefixos Markdown quando cabível.

    Parâmetros:
    - pdf_path: caminho para o arquivo PDF de entrada.

    Retorna:
    - string com o conteúdo em Markdown.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"[ERRO] Não foi possível abrir o PDF: {pdf_path}\nDetalhes: {e}")
        sys.exit(1)

    all_text = []
    font_sizes = _collect_font_sizes(doc)
    if not font_sizes:
        print("[ERRO] Não foi possível identificar o texto ou as fontes do PDF.")
        sys.exit(1)
    base_font_size = max(set(font_sizes), key=font_sizes.count)
    last_block_bottom = 0

    for page in doc:
        blocks = page.get_text("dict").get("blocks", [])
        for b in blocks:
            if b.get('type') != 0:
                continue
            space_above = b['bbox'][1] - last_block_bottom
            last_block_bottom = b['bbox'][3]
            for l in b.get("lines", []):
                clean_text, max_size, bold, underline = _parse_line(l)
                md_line = _md_from_line(clean_text, max_size, base_font_size, bold, underline, space_above)
                if md_line is None:
                    continue
                all_text.append(md_line)
    return "\n".join(all_text)

def save_markdown(md_text, md_path):
    """Salva o texto Markdown no caminho indicado, criando diretórios se preciso.

    Em caso de erro de escrita, imprime mensagem de erro e encerra o processo
    com código 1.

    Parâmetros:
    - md_text: conteúdo Markdown a ser salvo.
    - md_path: caminho do arquivo de saída (.md).
    """
    try:
        output_dir = os.path.dirname(os.path.abspath(md_path))
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_text)
    except Exception as e:
        print(f"[ERRO] Não foi possível salvar o arquivo Markdown em '{md_path}'.\nDetalhes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extrai texto estruturado de um PDF para Markdown')
    parser.add_argument('pdf', help='Arquivo PDF de entrada')
    parser.add_argument('md', nargs='?', default=None, help='Arquivo Markdown de saída (opcional)')
    args = parser.parse_args()

    # Manipulação multiplataforma do caminho
    pdf_path = os.path.abspath(os.path.expanduser(args.pdf))
    if not os.path.isfile(pdf_path):
        print(f"[ERRO] Arquivo PDF '{pdf_path}' não encontrado.")
        sys.exit(1)

    if args.md:
        md_path = os.path.abspath(os.path.expanduser(args.md))
    else:
        base, _ = os.path.splitext(pdf_path)
        md_path = base + '.md'

    print(f"Processando PDF: {pdf_path}")
    print(f"Arquivo Markdown de saída: {md_path}")

    md_text = extract_pdf_structure_advanced(pdf_path)
    save_markdown(md_text, md_path)
    print(f"\n[SUCESSO] Arquivo convertido para Markdown salvo como: {md_path}")
