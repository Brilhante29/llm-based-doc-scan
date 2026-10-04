"""Streamlit UI: upload a scanned PDF, preview it, and download the generated Markdown."""

from __future__ import annotations

import hashlib
import os
import tempfile

import streamlit as st
from pipeline import (
    MarkdownWriter,
    Settings,
    document_to_markdown,
    ollama_markdown_writer,
    render_pdf_pages,
    tesseract_extractor,
)
from streamlit_pdf_viewer import pdf_viewer

settings = Settings.from_env()


@st.cache_resource
def markdown_writer(model: str, base_url: str) -> MarkdownWriter:
    return ollama_markdown_writer(model, base_url)


st.set_page_config(page_title="PDF para Markdown", layout="wide")
st.title("📝 Conversor de PDF escaneado para Markdown")
st.caption(
    f"OCR: Tesseract ({settings.ocr_language}) · Modelo local: {settings.ollama_model} via Ollama"
)

uploaded_file = st.file_uploader("📂 Envie um arquivo PDF", type=["pdf"])

if uploaded_file is not None:
    content = uploaded_file.getvalue()
    digest = hashlib.sha256(content).hexdigest()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(content)
        temp_pdf_path = temp_pdf.name

    try:
        original, generated = st.columns(2)
        with original:
            st.subheader("📄 PDF original")
            pdf_viewer(temp_pdf_path)

        with generated:
            st.subheader("📜 Markdown gerado")
            # Streamlit reruns the script on every interaction; keep the result per file so that
            # clicking "download" does not convert the document again.
            if st.session_state.get("digest") != digest:
                st.session_state.pop("markdown", None)

            if st.button("Converter", type="primary"):
                progress = st.progress(0.0, text="Processando...")

                def on_page(index: int, total: int) -> None:
                    progress.progress(index / total, text=f"Página {index} de {total}")

                st.session_state["markdown"] = document_to_markdown(
                    temp_pdf_path,
                    render_pages=render_pdf_pages,
                    extract_text=tesseract_extractor(settings.ocr_language),
                    write_markdown=markdown_writer(settings.ollama_model, settings.ollama_base_url),
                    on_page=on_page,
                )
                st.session_state["digest"] = digest
                progress.empty()

            markdown_output = st.session_state.get("markdown")
            if markdown_output is not None:
                st.success("🎉 Conversão concluída!")
                # Model output derived from an untrusted document is rendered as Markdown only,
                # never as raw HTML.
                st.markdown(markdown_output)
                st.download_button(
                    "⬇️ Baixar Markdown",
                    markdown_output,
                    file_name="documento.md",
                    mime="text/markdown",
                )
    finally:
        os.unlink(temp_pdf_path)
