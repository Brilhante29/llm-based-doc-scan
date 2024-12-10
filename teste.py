# from langchain_ollama import ChatOllama
# from langchain_core.prompts import ChatPromptTemplate
# from pdf2image import convert_from_path
# from pytesseract import image_to_string
# import pytesseract

# # Configuração do modelo
# chat = ChatOllama(model="llama3")

# pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
# poppler_path = "C:/poppler-24.08.0/Library/bin"

# # Prompt Zero-Shot para texto simples
# zero_shot_prompt = ChatPromptTemplate.from_messages([
#     ("system", "Você é um assistente que transforma documentos escaneados em Markdown bem estruturado."),
#     ("human", "Converta o texto abaixo em Markdown estruturado:\nTexto: {text}\nMarkdown:")
# ])

# # Prompt Few-Shot para tabelas e layouts complexos
# few_shot_prompt = ChatPromptTemplate.from_messages([
#     ("system", "Você é um assistente que transforma documentos escaneados em Markdown. Aqui estão exemplos:"),
#     ("human", "Exemplo 1:\nTexto: 'Tabela de vendas: Nome | Produto | Valor'\nMarkdown: '| Nome | Produto | Valor |\n|------|---------|-------|'"),
#     ("human", "Exemplo 2:\nTexto: 'Lista de tarefas: Comprar leite, Ir ao mercado'\nMarkdown: '- Comprar leite\n- Ir ao mercado'"),
#     ("human", "Agora, converta o texto abaixo em Markdown:\nTexto: {text}\nMarkdown:")
# ])

# # Prompt Chain-of-Thought para raciocínio em partes complexas
# cot_prompt = ChatPromptTemplate.from_messages([
#     ("system", "Você é um assistente que explica e transforma documentos escaneados em Markdown."),
#     ("human", "O texto descreve um gráfico. Primeiro, analise o eixo X, depois o eixo Y, e explique antes de criar o Markdown.\nTexto: {text}\nExplicação e Markdown:")
# ])

# # Função para converter documentos em imagens
# def convert_to_images(file_path):
#     return convert_from_path(file_path, poppler_path=poppler_path)

# # Função para aplicar OCR em uma imagem
# def extract_text_from_image(image):
#     return image_to_string(image)

# # Função para selecionar o tipo de prompt com base no texto
# def convert_to_markdown(text):
#     if "gráfico" in text.lower():
#         prompt = cot_prompt
#     elif "tabela" in text.lower() or "|" in text:
#         prompt = few_shot_prompt
#     else:
#         prompt = zero_shot_prompt

#     response = prompt | chat
#     output = response.invoke({"text": text})
#     return output.content

# # Pipeline principal
# def document_to_markdown(file_path):
#     # Passo 1: Converter documento em imagens
#     images = convert_to_images(file_path)

#     markdowns = []
#     for image in images:
#         # Passo 2: Extração de texto com OCR
#         text = extract_text_from_image(image)

#         # Passo 3: Selecionar prompt e passar o texto pelo modelo
#         markdown = convert_to_markdown(text)
#         markdowns.append(markdown)

#     # Passo 4: Agregar os markdowns e retornar
#     return "\n\n".join(markdowns)

# # Teste do pipeline
# file_path = "documento.pdf"
# markdown_output = document_to_markdown(file_path)

# with open("documento.md", "w") as f:
#     f.write(markdown_output)

# print("Markdown gerado com sucesso!")

import streamlit as st
from langchain_ollama import ChatOllama
from streamlit_pdf_viewer import pdf_viewer
from langchain_core.prompts import ChatPromptTemplate
from pdf2image import convert_from_path
from pytesseract import image_to_string
import pytesseract
import tempfile
import os

# Configuração do Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
poppler_path = 'C:/poppler-24.08.0/Library/bin'

# Configuração do modelo
chat = ChatOllama(model="llama3")

# Prompt de conversão em Markdown
markdown_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente que transforma documentos escaneados em Markdown bem estruturado."),
    ("human", "Converta o texto abaixo em Markdown estruturado, preservando o layout, tabelas e gráficos:\nTexto: {text}\nMarkdown:")
])

# Função para converter documento em imagens
def convert_to_images(file_path):
    return convert_from_path(file_path, poppler_path=poppler_path)

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
