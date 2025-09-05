# PDF Tools — Automação de PDFs em Python

Coleção de scripts em Python para automatizar tarefas comuns com arquivos PDF. O foco é manter utilitários de linha de comando simples e reutilizáveis.

Atualmente, o repositório contém um utilitário de extração de texto para Markdown com detecção heurística de títulos e seções.

## Requisitos
- Python 3.9+ (recomendado 3.10+)
- Dependências:
  - PyMuPDF (`pymupdf`)

Instalação rápida:
- Windows (PowerShell):
  - `python -m venv .venv`
  - `.venv\\Scripts\\Activate.ps1`
  - `pip install pymupdf`
- macOS/Linux:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install pymupdf`

## Roadmap
- Mesclar/dividir PDFs, extrair imagens, reorganizar páginas, metadados, OCR (Tesseract), conversões para TXT/HTML e extrações com regex.

## Licença
Este projeto está disponível sob a Licença MIT. Consulte os termos em https://opensource.org/licenses/MIT.

![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white) [![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
