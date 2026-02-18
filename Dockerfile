FROM python:3.9-slim

WORKDIR /app

# Instalando dependências do sistema para o PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Variável de ambiente que o Google Cloud Run exige
ENV PORT=8080

# Comando ajustado para forçar a porta e o endereço corretos
CMD streamlit run app_web.py --server.port=${PORT} --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false