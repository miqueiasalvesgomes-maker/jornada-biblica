# Imagem oficial Python leve
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Inicializa plano e banco se necessário
RUN python generate_plan.py

# Variável de ambiente de porta
ENV PORT=5000

# Expõe a porta
EXPOSE 5000

# Executa o servidor
CMD ["python", "server.py"]
