"""Scanned PDF to Markdown: rasterize pages, OCR them, and let a local LLM structure the text.

The orchestration in :func:`document_to_markdown` depends only on three callables, so it can be
tested without Tesseract, Poppler, or a running model. Concrete adapters import their heavy
dependencies lazily.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

SYSTEM_PROMPT = (
    "Você é um assistente especializado em transformar documentos escaneados ou digitalizados "
    "em Markdown estruturado e organizado. Crie um documento Markdown fiel ao original, seguindo "
    "boas práticas de Markdown e garantindo que tabelas, listas e outros elementos estruturais "
    "estejam bem representados. Não invente conteúdo que não esteja no texto."
)

FEW_SHOT_EXAMPLE = """Exemplo de como estruturar o Markdown a partir do texto fornecido:

Texto:
Título: Relatório de Vendas 2024
1. **Introdução**
O relatório analisa os dados de vendas de 2024.

2. **Tabelas**
| Mês     | Vendas (R$) | Crescimento (%) |
|---------|-------------|-----------------|
| Janeiro | 50.000      | 10%            |
| Fevereiro | 55.000    | 8%             |

3. **Conclusão**
Os dados indicam crescimento contínuo.

Markdown:
# Relatório de Vendas 2024

## Introdução
O relatório analisa os dados de vendas de 2024.

## Tabelas
| Mês        | Vendas (R$) | Crescimento (%) |
|------------|-------------|-----------------|
| Janeiro    | 50.000      | 10%            |
| Fevereiro  | 55.000      | 8%             |

## Conclusão
Os dados indicam crescimento contínuo.
"""

HUMAN_PROMPT = (
    "Converta o texto abaixo em Markdown estruturado, preservando o layout, tabelas e gráficos:\n"
    "Texto: {text}\nMarkdown:"
)

PageRenderer = Callable[[str], Sequence[Any]]
TextExtractor = Callable[[Any], str]
MarkdownWriter = Callable[[str], str]
ProgressCallback = Callable[[int, int], None]


@dataclass(frozen=True)
class Settings:
    """Runtime configuration, read from environment variables."""

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    ocr_language: str = "por+eng"

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> Settings:
        env = os.environ if environ is None else environ
        return cls(
            ollama_base_url=env.get("OLLAMA_BASE_URL", cls.ollama_base_url),
            ollama_model=env.get("OLLAMA_MODEL", cls.ollama_model),
            ocr_language=env.get("OCR_LANG", cls.ocr_language),
        )


def document_to_markdown(
    path: str,
    render_pages: PageRenderer,
    extract_text: TextExtractor,
    write_markdown: MarkdownWriter,
    on_page: ProgressCallback | None = None,
) -> str:
    """Convert every page of ``path`` to Markdown, in page order.

    Pages whose OCR text is blank are skipped instead of being sent to the model, which avoids
    both wasted inference and invented content for empty pages.
    """
    pages = render_pages(path)
    sections: list[str] = []
    for index, page in enumerate(pages, start=1):
        if on_page is not None:
            on_page(index, len(pages))
        text = extract_text(page)
        if not text.strip():
            continue
        sections.append(write_markdown(text).strip())
    return "\n\n".join(section for section in sections if section)


def render_pdf_pages(path: str) -> list[Any]:
    """Rasterize a PDF with Poppler (via pdf2image)."""
    from pdf2image import convert_from_path

    return convert_from_path(path)


def tesseract_extractor(language: str) -> TextExtractor:
    """OCR one page image with Tesseract in the given language set (for example ``por+eng``)."""
    from pytesseract import image_to_string

    def extract(image: Any) -> str:
        return image_to_string(image, lang=language)

    return extract


def ollama_markdown_writer(model: str, base_url: str) -> MarkdownWriter:
    """Turn OCR text into Markdown with a local model served by Ollama."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_ollama import ChatOllama

    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("system", FEW_SHOT_EXAMPLE), ("human", HUMAN_PROMPT)]
    )
    chain = prompt | ChatOllama(model=model, base_url=base_url)

    def write(text: str) -> str:
        return str(chain.invoke({"text": text}).content)

    return write
