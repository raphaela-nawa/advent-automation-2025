# Day 14: Python Solution - Setup em 3 Minutos ⚡

## Por Que Python em Vez de n8n?

- ✅ **Mais simples**: Sem configuração de nós complexos
- ✅ **Mais robusto**: Sem erros de contexto/loop
- ✅ **Mais rápido**: Setup em 3 minutos
- ✅ **Mais fácil debug**: Logs claros no terminal
- ✅ **Agendamento**: Use cron (Linux/Mac) ou Task Scheduler (Windows)

---

## 🚀 Setup Rápido

### 1. Configure SMTP (1 minuto)

```bash
cd day14
cp .env.example .env
nano .env  # ou use VSCode
```

Preencha:
```
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-app-password-de-16-caracteres
SMTP_TO=seu-email@gmail.com
```

**Como gerar Gmail App Password:**
1. Acesse: https://myaccount.google.com/apppasswords
2. Crie senha para "Mail"
3. Copie os 16 caracteres (sem espaços)

### 2. Execute o Script (30 segundos)

```bash
python3 day14_MAIN_automation.py
```

**Output esperado:**
```
============================================================
DAY 14: Transport KPI Automation
============================================================

📊 Fetching KPIs (last 30 days)...
Fetching transport data from 2025-11-15 to 2025-12-15...
Querying Sao_Paulo for 'transporte OR mobilidade'...
Querying Rio_de_Janeiro for 'transporte OR mobilidade'...
[...]

✅ KPI Summary:
   - New Regulations: 95
   - Active Municipalities: 5
   - Compliance Mentions: 159
   - Safety Incidents: 15

📧 Building HTML email...

📤 Sending email to seu-email@gmail.com...

✅ Email sent successfully to seu-email@gmail.com

============================================================
✅ AUTOMATION COMPLETE!
============================================================
```

### 3. Verifique Seu Email! 📧

Você receberá um email profissional com:
- 4 KPIs calculados
- Municípios ativos
- Insights automáticos
- Design HTML responsivo

---

## 📅 Agendar Execução Diária

### Linux/Mac (cron):

```bash
# Editar crontab
crontab -e

# Adicionar (executa todo dia às 8am):
0 8 * * * cd /caminho/para/day14 && /usr/bin/python3 day14_MAIN_automation.py >> logs/cron.log 2>&1
```

### Windows (Task Scheduler):

1. Abra "Task Scheduler"
2. Create Basic Task
3. Trigger: Daily, 8:00 AM
4. Action: Start a program
   - Program: `python`
   - Arguments: `day14_MAIN_automation.py`
   - Start in: `C:\caminho\para\day14`

---

## 🔧 Mudar Período de Busca

Edite `day14_MAIN_automation.py`, linha 220:

```python
DAYS_BACK = 30  # Mude para 7, 15, 60, etc
```

---

## 📊 O Que o Script Faz

```
1. Fetch KPIs (day14_HELPER_querido_diario.py)
   ├─ Query 10 cidades × 3 keywords
   ├─ Respeita rate limit (60 req/min)
   └─ Retorna KPIs calculados

2. Build HTML Email
   ├─ KPI cards profissionais
   ├─ City badges dinâmicos
   └─ Insights baseados em dados reais

3. Send via Gmail SMTP
   ├─ Port 587 + TLS
   └─ HTML formatado
```

---

## ✅ Vantagens vs n8n

| Aspecto | n8n | Python |
|---------|-----|--------|
| **Setup** | 15+ minutos | 3 minutos |
| **Erros** | Contexto, loops, merge | Nenhum |
| **Debug** | Difícil | Fácil (print logs) |
| **Manutenção** | Requer UI | Editar código |
| **Portabilidade** | Precisa n8n instalado | Python anywhere |
| **Agendamento** | Interno | Cron/Task Scheduler |

---

## 🧪 Testar Sem Enviar Email

Comente a linha de envio em `day14_MAIN_automation.py`:

```python
# Step 3: Send email
print(f"\n📤 Sending email to {TO_EMAIL}...")
# success = send_email(subject, html_body, FROM_EMAIL, TO_EMAIL, SMTP_PASSWORD)  # COMENTAR ESTA LINHA

# Debug: Ver HTML
print("\n" + "=" * 60)
print("HTML Preview:")
print("=" * 60)
print(html_body[:500])  # Primeiros 500 chars
```

---

## 📝 Arquivos Importantes

```
day14/
├── day14_MAIN_automation.py          ← Script principal (execute este!)
├── day14_HELPER_querido_diario.py    ← Funções de API
├── day14_CONFIG_settings.py          ← Configurações
├── .env                              ← Suas credenciais SMTP
└── logs/                             ← Logs de execução
```

---

## 🔍 Troubleshooting

### Erro: "SMTP_PASSWORD not found"

**Solução:** Copie `.env.example` para `.env` e preencha as credenciais.

### Erro: "SMTPAuthenticationError"

**Solução:**
1. Verifique App Password (16 chars, sem espaços)
2. Habilite "Less secure app access" (se necessário)
3. Use port 587 (não 465)

### KPIs = 0

**Normal!** Alguns períodos têm poucas publicações.

**Solução:** Aumente `DAYS_BACK` para 60 ou 90.

### ImportError: No module named 'dotenv'

**Solução:**
```bash
pip3 install python-dotenv
```

---

## 🎯 Pronto!

Você tem agora:
- ✅ Script Python funcional
- ✅ Setup em 3 minutos
- ✅ Zero problemas de n8n
- ✅ Fácil de agendar e manter
- ✅ Logs claros no terminal

**Execute agora:**
```bash
python3 day14_MAIN_automation.py
```

E receba seu primeiro email de KPIs! 🚀
