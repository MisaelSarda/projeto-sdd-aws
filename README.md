# Task & Service Health API (SDD + AWS + CI/CD + SonarQube)

[![CI/CD Pipeline](https://github.com/SEU_USUARIO/projeto-sdd-aws/actions/workflows/deploy.yml/badge.svg)](https://github.com/SEU_USUARIO/projeto-sdd-aws/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SEU_PROJETO_SONAR&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=SEU_PROJETO_SONAR)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=SEU_PROJETO_SONAR&metric=coverage)](https://sonarcloud.io/summary/new_code?id=SEU_PROJETO_SONAR)

> **Trabalho Prático de Engenharia de Software e DevOps em Nuvem**  
> **Integrantes da Dupla:**  
> - Estudante 1: Misael Pablo Sardá - DevOps & Cloud Lead  
> - Estudante 2: Vinicius Policarpo Macedo - Software Engineer & SDD Lead  

---

## 📌 1. Visão Geral do Projeto

Este projeto consiste em uma API RESTful de alta disponibilidade para gerenciamento de tarefas e monitoramento de serviços, desenvolvida estritamente através da abordagem de engenharia **Spec-Driven Development (SDD)** / **Schema-Driven Development**.

O ecossistema conta com:
- **Contrato Formal OpenAPI 3.0** (`docs/openapi.yaml`) e **Software Design Document** (`docs/SDD.md`).
- **Backend Moderno em FastAPI (Python)** com validação de tipos e dados estrita via **Pydantic**.
- **Testes Automatizados com Pytest** com cobertura de código superior a 90%.
- **Scanner de Segurança de Código Estático (SAST)** com **SonarQube / SonarCloud** integrado na esteira.
- **Pipeline de Integração e Entrega Contínua (CI/CD)** implementada no **GitHub Actions**.
- **Publicação Automática na Nuvem AWS (EC2)** empacotada em container **Docker**.

---

## 📐 2. Engenharia Orientada a Especificação (SDD)

Na abordagem SDD empregada:
1. **Especificação Prévia:** O contrato da API foi integralmente modelado em `docs/openapi.yaml` e documentado em `docs/SDD.md` antes da escrita do código.
2. **Conformidade de Esquema:** A aplicação e os modelos Pydantic implementam estritamente as regras de tipos, limites de comprimento e formatos descritos na especificação.
3. **Documentação Viva:** A documentação interativa OpenAPI/Swagger é servida automaticamente na rota pública `/docs`.

---

## 🚀 3. Guia Passo a Passo para a Dupla

### Passo 1: Criar o Repositório no GitHub
1. Um dos estudantes cria um repositório no GitHub (público para uso gratuito do SonarCloud), por exemplo: `projeto-sdd-aws`.
2. O criador adiciona a dupla como colaboradora (`Settings > Collaborators`).
3. Clone ou copie todos os arquivos desta pasta para o repositório local e faça o primeiro push:
   ```bash
   git init
   git add .
   git commit -m "feat: initial commit with SDD specs, API, tests and CI/CD"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/projeto-sdd-aws.git
   git push -u origin main
   ```

---

### Passo 2: Configurar o Scanner de Segurança (SonarCloud)
1. Acesse [sonarcloud.io](https://sonarcloud.io) e faça login com a conta do GitHub.
2. Clique no ícone `+` no canto superior direito > **Analyze new project**.
3. Selecione o repositório `projeto-sdd-aws`.
4. Em **Administration > Analysis Method**, desative o *Automatic Analysis* para permitir o scanner via GitHub Actions.
5. Em **Account > Security**, gere um token com o nome `GITHUB_ACTIONS_TOKEN`.
6. Atualize o arquivo `sonar-project.properties` do seu repositório com sua `organization` e `projectKey` fornecidos pelo SonarCloud.

---

### Passo 3: Provisionar a Máquina na AWS (EC2 Free Tier)
1. Acesse o console da **AWS** > serviço **EC2** > **Launch Instance** (Executar Instância).
2. **Nome:** `servidor-sdd-app`
3. **Sistema Operacional (AMI):** `Ubuntu Server 24.04 LTS (HVM), SSD Volume Type` (64-bit x86).
4. **Tipo de Instância:** `t2.micro` ou `t3.micro` (Elegível para o Free Tier gratuito).
5. **Key Pair (Par de chaves):** Crie um novo par de chaves (tipo RSA, formato `.pem`) e faça o download (ex: `ec2-key.pem`).
6. **Network Settings (Security Group / Firewall):**
   - Marcar: **Allow SSH traffic from anywhere** (Porta 22).
   - Marcar: **Allow HTTP traffic from the internet** (Porta 80).
7. Clique em **Launch Instance**.
8. Quando a instância estiver em status *Running*, anote o **Public IPv4 address** (ex: `54.232.xxx.xxx`).

#### Instalação Inicial do Docker na EC2:
Conecte-se na EC2 via terminal SSH e execute:
```bash
# Conectar na instância
ssh -i "ec2-key.pem" ubuntu@SEU_IP_PUBLICO

# Instalar Docker e Docker Compose
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Permitir executar Docker sem sudo
sudo usermod -aG docker ubuntu
exit
```

---

### Passo 4: Cadastrar os Secrets no GitHub
No seu repositório do GitHub, vá em:  
`Settings > Secrets and variables > Actions > New repository secret`

Cadastre os seguintes 6 segredos:

| Nome do Secret | Descrição / Valor |
| :--- | :--- |
| `SONAR_TOKEN` | Token gerado no SonarCloud |
| `DOCKERHUB_USERNAME` | Seu nome de usuário no [Docker Hub](https://hub.docker.com) |
| `DOCKERHUB_TOKEN` | Access Token gerado no Docker Hub (*Account Settings > Security*) |
| `EC2_HOST` | O endereço IPv4 Público da instância EC2 (ex: `54.232.xxx.xxx`) |
| `EC2_USERNAME` | Nome do usuário do Ubuntu na AWS: `ubuntu` |
| `EC2_SSH_KEY` | Todo o conteúdo textual do arquivo de chave `.pem` baixado da AWS |

---

### Passo 5: Disparar a Pipeline de CI/CD
1. Faça qualquer commit na branch `main`:
   ```bash
   git commit --allow-empty -m "ci: trigger full pipeline"
   git push origin main
   ```
2. Acesse a aba **Actions** no repositório.
3. Observe as etapas:
   - **Testes Unitários:** Pytest executará 100% dos testes e gerará o arquivo `coverage.xml`.
   - **Scanner SonarCloud:** Analisará vulnerabilidades e verificará o Quality Gate.
   - **Docker Build & Push:** Construirá a imagem e fará upload no Docker Hub.
   - **Deploy SSH na EC2:** Conectará à AWS, atualizará o container e iniciará a aplicação.

---

## 🌐 4. Acesso e Validação da Aplicação Pública

Após a conclusão com sucesso do pipeline, a aplicação estará instantaneamente disponível na internet para avaliação:

- **Swagger UI Interativo (OpenAPI):**  
  `http://<IP_PUBLICO_EC2>/docs`
- **Documentação ReDoc:**  
  `http://<IP_PUBLICO_EC2>/redoc`
- **Endpoint de Health Check:**  
  `http://<IP_PUBLICO_EC2>/health`
- **Endpoint de Informações da Aplicação:**  
  `http://<IP_PUBLICO_EC2>/api/v1/info`

---

## 🧪 5. Executando os Testes Localmente

Caso queira testar na máquina local antes de subir para a nuvem:

```bash
# 1. Criar e ativar ambiente virtual
python -m venv .venv
# No Linux/macOS:
source .venv/bin/activate
# No Windows PowerShell:
.venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar suíte de testes com cobertura
pytest --cov=app --cov-report=term-missing

# 4. Executar a aplicação localmente
uvicorn app.main:app --reload --port 8000
```
