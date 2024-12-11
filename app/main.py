import streamlit as st
from langchain_ollama import ChatOllama
from streamlit_pdf_viewer import pdf_viewer
from langchain_core.prompts import ChatPromptTemplate
from pdf2image import convert_from_path
from pytesseract import image_to_string
import tempfile
import os

# Configuração do modelo
chat = ChatOllama(model="llama3", base_url="http://ollama:11434")

# Prompt de conversão em Markdown
markdown_prompt = ChatPromptTemplate.from_messages([
    # Context
    ("system", "Você é um assistente especializado em transformar documentos escaneados ou digitalizados em Markdown estruturado e organizado. Você deve criar um documento Markdown que seja fiel ao original, seguindo as boas práticas de Markdown e garantindo que tabelas, listas e quaisquer outros elementos estruturais estejam bem representados."),
    
    # Process (com few-shot)
    ("system", """Aqui está um exemplo de como você deve estruturar o Markdown a partir do texto fornecido:

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
"""),

    # Task
    ("human", "Converta o texto abaixo em Markdown estruturado, preservando o layout, tabelas e gráficos:\nTexto: {text}\nMarkdown:")
])

# Função para converter documento em imagens
def convert_to_images(file_path):
    return convert_from_path(file_path)

# Função para aplicar OCR em uma imagem
def extract_text_from_image(image):
    return image_to_string(image)

# Função para converter texto em Markdown
def convert_to_markdown(text):
    response = markdown_prompt | chat
    output = response.invoke({"text": text})
    return output.content

# Pipeline principal
def document_to_markdown(file_path):
    images = convert_to_images(file_path)
    markdowns = []
    for idx, image in enumerate(images):
        st.info(f"Processando página {idx + 1} de {len(images)}...")
        text = extract_text_from_image(image)
        markdown = convert_to_markdown(text)
        markdowns.append(markdown)
    return "\n\n".join(markdowns)

# Interface do Streamlit
st.set_page_config(page_title="Conversor de PDF para Markdown", layout="wide")
st.title("📝 Conversor de PDF para Markdown")
st.markdown("Transforme documentos PDF escaneados em Markdown bem estruturado, preservando tabelas, gráficos e layouts!")

uploaded_file = st.file_uploader("📂 Envie um arquivo PDF", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_file.read())
        temp_pdf_path = temp_pdf.name

    # Dividindo a tela em duas colunas para renderizar lado a lado
    col1, col2 = st.columns(2)

    # Coluna 1: Visualização do PDF Original
    with col1:
        st.subheader("📄 Visualização do PDF Original")
        pdf_viewer(temp_pdf_path)

    # Coluna 2: Markdown gerado
    with col2:
        st.subheader("📜 Markdown Gerado")
        st.info("⏳ Processando...")

        # Processar o PDF
        markdown_output = document_to_markdown(temp_pdf_path)
        st.success("🎉 Conversão concluída!")
        st.markdown(markdown_output, unsafe_allow_html=True)

        # Botão para baixar o Markdown
        st.download_button("⬇️ Baixar Markdown", markdown_output, file_name="documento.md", mime="text/markdown")

    # Limpar o arquivo temporário
    os.unlink(temp_pdf_path)
