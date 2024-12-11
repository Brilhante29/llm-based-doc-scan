
# LLM-Based Doc Scan

Este projeto utiliza **Docker Compose** para configurar dois serviços: um aplicativo Streamlit para escanear documentos com modelos LLM e um container **Ollama** configurado para rodar o modelo `llama3`.

## **Estrutura do Projeto**

```
.
├── app/
│   ├── main.py          # Código principal do Streamlit
├── docker/
│   ├── docker-compose.yml  # Arquivo Docker Compose
│   ├── ollama_data/     # Pasta de dados persistentes do Ollama
├── requirements.txt     # Dependências do Python
├── README.md            # Este arquivo
```

---

## **Pré-requisitos**

Certifique-se de ter as seguintes ferramentas instaladas no seu ambiente:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## **Configuração Inicial**

1. **Clone o repositório**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DO_REPOSITORIO>
   ```

2. **Verifique o arquivo `docker-compose.yml`**
   Certifique-se de que o arquivo `docker-compose.yml` está configurado corretamente.

3. **Verifique as dependências**
   Certifique-se de que o arquivo `requirements.txt` contém todas as bibliotecas necessárias para rodar o aplicativo Streamlit.

---

## **Passo a Passo para Rodar o Projeto**

1. **Subir os containers**
   Execute o seguinte comando na raiz do projeto para construir e subir os serviços:
   ```bash
   docker-compose up --build
   ```

2. **Verifique se os containers estão rodando**
   Depois de subir os serviços, use o comando abaixo para listar os containers ativos:
   ```bash
   docker ps
   ```

   Você deverá ver dois containers: 
   - **streamlit-app**
   - **ollama**

3. **Iniciar o modelo `llama3`**
   Após os containers estarem em execução, você precisa rodar o comando abaixo para iniciar o modelo `llama3` no serviço **Ollama**:

   ```bash
   container_id=$(docker ps | grep ollama | awk '{print $1}')
   docker exec -it $container_id ollama run llama3
   ```

   Esse comando:
   - Localiza o ID do container do serviço **Ollama**.
   - Executa o comando `ollama run llama3` dentro do container para iniciar o modelo.

4. **Acessar o aplicativo Streamlit**
   Após iniciar o modelo `llama3`, acesse o aplicativo Streamlit no seu navegador em:
   ```
   http://localhost:8501
   ```

---

## **Configuração Persistente**

Os dados do serviço **Ollama** (como o modelo baixado) são salvos na pasta:
```
docker/ollama_data/
```

Essa pasta é mapeada para o container e permite que os dados sejam mantidos mesmo após o container ser reiniciado.

---

## **Comandos Úteis**

1. **Reiniciar os serviços**
   Para reiniciar os serviços:
   ```bash
   docker-compose restart
   ```

2. **Parar os serviços**
   Para parar os containers:
   ```bash
   docker-compose down
   ```

3. **Verificar os logs**
   Para monitorar os logs dos containers:
   ```bash
   docker-compose logs -f
   ```

---

## **Problemas Comuns**

### 1. O modelo `llama3` não está rodando
   - Certifique-se de que executou o comando:
     ```bash
     container_id=$(docker ps | grep ollama | awk '{print $1}')
     docker exec -it $container_id ollama run llama3
     ```

### 2. Erros de dependência no Streamlit
   - Verifique se todas as dependências estão no `requirements.txt` e reconstrua a imagem:
     ```bash
     docker-compose build
     docker-compose up
     ```

---

## **Contribuição**

Sinta-se à vontade para abrir issues ou enviar pull requests para melhorias no projeto.
