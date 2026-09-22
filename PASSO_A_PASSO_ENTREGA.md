# Passo a passo — executar e entregar a atividade SSDLC

Guia direto do que fazer, na ordem. Divisão sugerida: **Misael** cuida da AWS/EC2 e
dos secrets; **Vinicius** cuida do SonarCloud e do código/SDD. Os dois acompanham a pipeline.

> As 5 correções já estão aplicadas neste pacote. Antes do push, só falta preencher
> valores que dependem das contas de vocês (SonarCloud, Docker Hub, IP da EC2).

---

## Etapa 0 — Subir o código no repositório que vocês já têm

Na pasta do projeto:
```bash
git add .
git commit -m "fix: quality gate bloqueante, sonar org, action atualizada e nomes"
git push origin main
```

---

## Etapa 1 — SonarCloud (scanner de segurança)

1. Acesse <https://sonarcloud.io> e entre com o GitHub.
2. `+` → **Analyze new project** → selecione o repositório de vocês.
3. Em **Administration → Analysis Method**, **desligue** o *Automatic Analysis*
   (a análise vai vir pela pipeline).
4. Anote a **Organization** e a **Project Key** que o SonarCloud mostrar.
5. Abra `sonar-project.properties` e troque:
   - `sonar.organization=SUA_ORGANIZACAO_SONARCLOUD` → a organização real
   - `sonar.projectKey=SUA_PROJECT_KEY_SONARCLOUD` → a project key real
6. Gere um token: **My Account → Security → Generate Token**. Guarde — vira o secret `SONAR_TOKEN`.

Commit da mudança do properties:
```bash
git add sonar-project.properties && git commit -m "chore: configurar org e key do SonarCloud" && git push
```

---

## Etapa 2 — Docker Hub

1. Em <https://hub.docker.com>, crie conta (se não tiver).
2. **Account Settings → Security → New Access Token**. Guarde — vira `DOCKERHUB_TOKEN`.
3. O usuário do Docker Hub vira `DOCKERHUB_USERNAME`.

---

## Etapa 3 — AWS EC2 (a máquina na nuvem)

1. Console AWS → **EC2 → Launch Instance**.
2. Nome: `servidor-sdd-app` · AMI: **Ubuntu Server 24.04 LTS** · Tipo: **t2.micro** (Free Tier).
3. **Key pair:** crie um novo (RSA, `.pem`) e baixe. Esse arquivo vira o secret `EC2_SSH_KEY`.
4. **Security group (firewall):** libere **SSH (22)** e **HTTP (80)**.
5. Launch. Anote o **Public IPv4** → vira `EC2_HOST`.

Instalar Docker na EC2 (conecte via SSH):
```bash
ssh -i "ec2-key.pem" ubuntu@SEU_IP_PUBLICO

sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
exit   # sair e reconectar para o grupo docker valer
```

---

## Etapa 4 — Cadastrar os 6 secrets no GitHub

Repositório → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Valor |
|--------|-------|
| `SONAR_TOKEN` | token do SonarCloud (Etapa 1) |
| `DOCKERHUB_USERNAME` | usuário do Docker Hub |
| `DOCKERHUB_TOKEN` | token do Docker Hub (Etapa 2) |
| `EC2_HOST` | IP público da EC2 (Etapa 3) |
| `EC2_USERNAME` | `ubuntu` |
| `EC2_SSH_KEY` | conteúdo INTEIRO do arquivo `.pem` (com as linhas BEGIN/END) |

> ⚠️ A chave `.pem` e os tokens vivem só aqui, nunca no código. O `.gitignore` já
> bloqueia `*.pem`.

---

## Etapa 5 — Rodar a pipeline

```bash
git commit --allow-empty -m "ci: disparar pipeline completa"
git push origin main
```
Vá na aba **Actions** e acompanhe:
1. **Testes** (pytest, 8 testes, cobertura ~99%)
2. **SonarCloud** — agora **espera o Quality Gate**; se reprovar, a pipeline para aqui e o deploy NÃO acontece
3. **Build & Push** da imagem no Docker Hub
4. **Deploy SSH** na EC2 + health check

---

## Etapa 6 — Validar que está publicado na internet

No navegador (troque pelo IP da EC2):
- `http://SEU_IP/health` → `{"status":"healthy",...}`
- `http://SEU_IP/docs` → Swagger interativo (prova visual forte do SDD/OpenAPI)
- `http://SEU_IP/api/v1/tasks` → `[]`

Criar uma tarefa pelo terminal:
```bash
curl -X POST http://SEU_IP/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Primeira tarefa","priority":"HIGH"}'
```

---

## O que entregar (evidências)

Juntem num documento/PDF:
1. **Link do repositório** no GitHub.
2. **Print da aba Actions** com a pipeline verde (as 4 etapas).
3. **Print do SonarCloud** mostrando o relatório (Bugs / Vulnerabilities / Coverage / Quality Gate: Passed).
4. **Print do Swagger** em `http://SEU_IP/docs` — prova de que está público e que o contrato SDD está no ar.
5. **Print do `/health`** respondendo pela internet.

### Como explicar cada requisito da atividade
| Requisito | Resposta |
|-----------|----------|
| Repositório no GitHub | link do repo |
| Sistema com SDD | `docs/openapi.yaml` (contrato) + `docs/SDD.md`, código Pydantic seguindo o schema; Swagger em `/docs` |
| Ambiente na AWS | EC2 Ubuntu rodando o container (porta 80) |
| Pipeline | GitHub Actions (`.github/workflows/deploy.yml`), 4 estágios |
| Scanner de segurança no deploy | SonarCloud com `sonar.qualitygate.wait=true` — reprovou, não faz deploy |
| Publicado na internet | `http://SEU_IP/docs` acessível |

---

## Dica para a defesa oral
Se perguntarem "por que o scanner protege o deploy?": o job `test-and-security` roda
**antes** do `build-and-deploy` (via `needs:`), e o Sonar espera o Quality Gate
(`sonar.qualitygate.wait=true`). Se o gate reprovar, o passo falha, o job falha, e o
deploy — que depende dele — nem começa. É o "portão de qualidade" do SSDLC na prática.
