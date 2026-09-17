# Imagem base oficial leve com Python 3.11
FROM python:3.11-slim AS base

# Definir variáveis de ambiente para Python em containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Criar usuário sem privilégios de root (Boa prática de segurança auditada pelo SonarQube)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código-fonte da aplicação e especificações
COPY app/ ./app/
COPY docs/ ./docs/

# Ajustar permissões para o usuário não-root
RUN chown -R appuser:appuser /app
USER appuser

# Expor a porta da aplicação
EXPOSE 8000

# Healthcheck do container Docker
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando de inicialização com Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
