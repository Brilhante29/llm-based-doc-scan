from pipeline import HUMAN_PROMPT, Settings, document_to_markdown


def test_pages_are_converted_in_order_and_joined():
    pages = ["page-1", "page-2", "page-3"]
    markdown = document_to_markdown(
        "document.pdf",
        render_pages=lambda path: pages,
        extract_text=lambda page: f"text of {page}",
        write_markdown=lambda text: f"# {text}\n",
    )
    assert markdown == "# text of page-1\n\n# text of page-2\n\n# text of page-3"


def test_blank_pages_are_not_sent_to_the_model():
    sent = []

    def write(text):
        sent.append(text)
        return text.upper()

    markdown = document_to_markdown(
        "document.pdf",
        render_pages=lambda path: ["a", "blank", "b"],
        extract_text=lambda page: "  \n" if page == "blank" else page,
        write_markdown=write,
    )
    assert sent == ["a", "b"]
    assert markdown == "A\n\nB"


def test_progress_reports_every_page_with_the_total():
    calls = []
    document_to_markdown(
        "document.pdf",
        render_pages=lambda path: [1, 2],
        extract_text=lambda page: "",
        write_markdown=lambda text: text,
        on_page=lambda index, total: calls.append((index, total)),
    )
    assert calls == [(1, 2), (2, 2)]


def test_renderer_receives_the_document_path():
    received = []
    document_to_markdown(
        "/tmp/scan.pdf",
        render_pages=lambda path: received.append(path) or [],
        extract_text=lambda page: "",
        write_markdown=lambda text: text,
    )
    assert received == ["/tmp/scan.pdf"]


def test_settings_defaults_and_environment_overrides():
    assert Settings.from_env({}) == Settings()
    custom = Settings.from_env(
        {"OLLAMA_BASE_URL": "http://ollama:11434", "OLLAMA_MODEL": "llama3.2", "OCR_LANG": "por"}
    )
    assert custom == Settings("http://ollama:11434", "llama3.2", "por")


def test_human_prompt_carries_the_ocr_text_placeholder():
    assert "{text}" in HUMAN_PROMPT
