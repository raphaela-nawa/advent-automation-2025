# 🏠 n8n Self-Host Guide - Guia Completo

## Por que Self-Host?

**Vantagens:**
- ✅ Environment variables completas
- ✅ Controle total dos dados
- ✅ Sem limites de execuções
- ✅ Grátis (só paga infraestrutura)

**Desvantagens:**
- ❌ Precisa manter servidor rodando
- ❌ Responsável por backups
- ❌ Precisa gerenciar updates

---

## 🚀 Método 1: Docker (Mais Fácil)

### Pré-requisitos

```bash
# Instale Docker Desktop
# Mac: https://docs.docker.com/desktop/install/mac-install/
# Ou via Homebrew:
brew install --cask docker
```

### Passo a Passo

**1. Crie uma pasta para n8n:**

```bash
cd ~/Desktop
mkdir n8n-selfhost
cd n8n-selfhost
```

**2. Crie o arquivo docker-compose.yml:**

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      # n8n Configuration
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeThisPassword123
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http

      # Timezone
      - GENERIC_TIMEZONE=America/Sao_Paulo
      - TZ=America/Sao_Paulo

      # Day 11 Environment Variables
      - DAY11_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
      - DAY11_RUN_ON_WEEKENDS=false

    volumes:
      - n8n_data:/home/node/.n8n
      - ./workflows:/home/node/.n8n/workflows
      - ./credentials:/home/node/.n8n/credentials

volumes:
  n8n_data:
```

**3. Inicie o n8n:**

```bash
docker-compose up -d
```

**4. Acesse:**

```
http://localhost:5678
```

**Credenciais:**
- User: `admin`
- Password: `changeThisPassword123` (mude isso no docker-compose.yml!)

**5. Importe o workflow:**

- No n8n local, importe `day11_n8n_workflow_IMPORTABLE.json`
- As variáveis de ambiente já estarão disponíveis!

**6. Parar/Reiniciar:**

```bash
# Parar
docker-compose down

# Reiniciar
docker-compose restart

# Ver logs
docker-compose logs -f n8n
```

---

## 🌐 Método 2: Deploy na Nuvem (Railway)

Railway é **grátis** para começar e muito fácil:

### Passo a Passo

**1. Acesse:**
```
https://railway.app
```

**2. Faça login com GitHub**

**3. New Project → Deploy n8n**
   - Railway tem template pronto de n8n!

**4. Configure Environment Variables:**

No Railway dashboard:
```
DAY11_SLACK_WEBHOOK_URL=seu_webhook
DAY11_RUN_ON_WEEKENDS=false
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=suaSenha123
```

**5. Acesse seu n8n:**
   - Railway gera um URL automático tipo: `https://n8n-production-xxxx.up.railway.app`

**6. Importe o workflow normalmente**

**Custo:**
- $5/mês de crédito grátis (suficiente para n8n)
- Depois ~$10-15/mês

---

## ☁️ Método 3: DigitalOcean Droplet

Para quem quer mais controle:

### Criar Droplet

```bash
# 1. Crie droplet no DigitalOcean
# - Ubuntu 22.04
# - Droplet $6/mês (1GB RAM)

# 2. SSH no servidor
ssh root@seu-ip

# 3. Instale Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Instale Docker Compose
apt install docker-compose -y

# 5. Clone seu setup
mkdir /opt/n8n
cd /opt/n8n

# 6. Crie docker-compose.yml (mesmo do Método 1)

# 7. Inicie
docker-compose up -d

# 8. Configure firewall
ufw allow 5678/tcp
```

**Acesse:**
```
http://seu-ip:5678
```

**Custo:** $6/mês

---

## 🔒 Método 4: Com HTTPS (Produção)

Se quiser domínio próprio com SSL:

### docker-compose.yml com Traefik

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.email=seu@email.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.myresolver.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./letsencrypt:/letsencrypt

  n8n:
    image: n8nio/n8n:latest
    restart: always
    environment:
      - N8N_HOST=n8n.seudominio.com
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://n8n.seudominio.com
      - DAY11_SLACK_WEBHOOK_URL=${DAY11_SLACK_WEBHOOK_URL}
    volumes:
      - n8n_data:/home/node/.n8n
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.n8n.rule=Host(`n8n.seudominio.com`)"
      - "traefik.http.routers.n8n.entrypoints=websecure"
      - "traefik.http.routers.n8n.tls.certresolver=myresolver"

volumes:
  n8n_data:
```

---

## 🎯 Qual Método Escolher?

### Para Testar/Aprender:
→ **Docker Local** (Método 1) - Grátis, roda no seu Mac

### Para Portfolio:
→ **Railway** (Método 2) - $5 grátis, fácil, URL bonito

### Para Produção Leve:
→ **DigitalOcean** (Método 3) - $6/mês, controle total

### Para Cliente Empresarial:
→ **HTTPS com domínio** (Método 4) - Profissional, seguro

---

## 🆚 Comparação: Cloud vs Self-Host

| Aspecto | n8n Cloud | Self-Host Docker |
|---------|-----------|------------------|
| **Setup** | 5 minutos | 15 minutos |
| **Custo** | $20/mês | $0-6/mês |
| **Env Vars** | Limitado | Total |
| **Manutenção** | Zero | Você |
| **Backups** | Automático | Manual |
| **Updates** | Automático | Manual |
| **Customização** | Limitada | Total |

---

## 📝 Recomendação para Você

**Para Day 11 Portfolio:**

1. **Use n8n Cloud** (mais rápido)
   - Cole webhook direto no node
   - Não precisa de env vars
   - Tire screenshots bonitos

2. **OU Docker Local** (se quiser aprender)
   - Grátis
   - Roda no seu Mac
   - Bom para entender infraestrutura

**Não precisa de produção completa para portfolio!**

---

## 🚀 Quick Start Recomendado

```bash
# 1. Clone o setup
cd ~/Desktop
mkdir n8n-local
cd n8n-local

# 2. Crie docker-compose.yml (copie do Método 1)

# 3. Edite as env vars:
nano docker-compose.yml
# Mude DAY11_SLACK_WEBHOOK_URL=seu_webhook_real

# 4. Inicie
docker-compose up -d

# 5. Acesse
open http://localhost:5678

# 6. Login com admin/changeThisPassword123

# 7. Importe day11_n8n_workflow_IMPORTABLE.json

# 8. Teste!
```

---

## ❓ FAQ

**P: Preciso manter meu Mac ligado?**
R: Se usar Docker local, sim. Use Railway se quiser 24/7.

**P: Como faço backup?**
R: `docker-compose down && cp -r n8n_data backup_$(date +%Y%m%d)`

**P: Posso migrar de self-host para cloud depois?**
R: Sim! Export workflows → Import na cloud.

**P: E se quiser parar?**
R: `docker-compose down && docker-compose rm`

---

**Pronto! Escolha o método que preferir e me avise se precisar de ajuda!** 🚀
