# 🎨 n8n Workflow - Guia de Importação

## 📥 Como Importar o Workflow

### Passo 1: Acessar n8n
1. Acesse sua conta n8n (cloud ou self-hosted)
2. Vá para **Workflows**

### Passo 2: Importar
1. Clique em **Add Workflow** (botão superior direito)
2. Clique nos 3 pontinhos ⋮ no canto superior direito
3. Selecione **Import from File**
4. Escolha o arquivo: `day11_n8n_workflow_IMPORTABLE.json`

### Passo 3: Configurar Credenciais

Você precisará configurar:

#### 1. **Slack Webhook** (obrigatório)
   - Node: "Send to Slack"
   - Adicione seu webhook URL do Slack
   - O mesmo que você colocou em `config/.env`

#### 2. **Google Sheets** (opcional - para logging)
   - Node: "Log Execution"
   - Conecte sua conta Google
   - Crie uma planilha chamada "day11_execution_log"

### Passo 4: Configurar Variáveis de Ambiente

No n8n, vá em **Settings → Environment Variables** e adicione:

```bash
DAY11_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DAY11_RUN_ON_WEEKENDS=false
```

### Passo 5: Ativar o Workflow

1. Clique em **Save** para salvar o workflow
2. Toggle **Active** (switch no topo) para ativar
3. O workflow agora rodará diariamente às 8am UTC

---

## 🎯 Estrutura Visual do Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW VISUAL (n8n)                            │
└─────────────────────────────────────────────────────────────────────┘

[Schedule Trigger]
   Daily 8am UTC
        │
        ▼
   [Check Weekend]
   Code: Skip weekends?
        │
        ▼
    [IF Node]
   Should run?
        │
        ├──► YES ────────────────────────────────┐
        │                                        │
        ▼                                        ▼
[Fetch GA4 Data]                      [Fetch Ads Data]
 HTTP Request                          HTTP Request
        │                                        │
        └────────────┬───────────────────────────┘
                     │
                     ▼
            [Fallback: Load CSV]
            Code: Read local files
                     │
                     ▼
            [Calculate Metrics]
            Code: 18 KPIs
                     │
                     ▼
         [Format Slack Message]
         Code: Block Kit builder
                     │
                     ▼
            [Send to Slack]
            HTTP POST webhook
                     │
                     ▼
            [Log Execution]
            Google Sheets append
                     │
                     ▼
                  [Done]

         ERROR PATH (from any node):
                     │
                     ▼
         [Format Error Message]
         Code: Error formatter
                     │
                     ▼
         [Send Error to Slack]
         HTTP POST webhook
```

---

## 🔧 Nodes Explicados

### 1️⃣ **Schedule Trigger**
- **Tipo:** Cron Trigger
- **Configuração:** `0 8 * * *` (8am UTC diário)
- **Função:** Inicia o workflow automaticamente

### 2️⃣ **Check Weekend**
- **Tipo:** Code (JavaScript)
- **Função:** Verifica se é final de semana
- **Output:** `{ skip: true/false, date, dayOfWeek }`

### 3️⃣ **Should Run?**
- **Tipo:** IF Node
- **Condição:** `skip === false`
- **True Path:** Continua para fetch
- **False Path:** Para execução

### 4️⃣ **Fetch GA4 Data**
- **Tipo:** HTTP Request
- **URL:** `http://localhost:5000/api/day01/ga4`
- **Função:** Busca dados do GA4
- **Error Handling:** Continue on error

### 5️⃣ **Fetch Google Ads Data**
- **Tipo:** HTTP Request
- **URL:** `http://localhost:5000/api/day01/ads`
- **Função:** Busca dados de Google Ads
- **Executa em paralelo** com Fetch GA4

### 6️⃣ **Fallback: Load CSV**
- **Tipo:** Code (JavaScript)
- **Função:** Se APIs falharem, lê CSVs locais
- **Caminho:** `day01/data/processed/*.csv`

### 7️⃣ **Calculate Metrics**
- **Tipo:** Code (JavaScript)
- **Função:** Calcula 18 KPIs
- **Output:** Objeto com todas métricas

### 8️⃣ **Format Slack Message**
- **Tipo:** Code (JavaScript)
- **Função:** Cria Slack Block Kit JSON
- **Output:** Array de 13 blocks

### 9️⃣ **Send to Slack**
- **Tipo:** HTTP Request
- **Method:** POST
- **URL:** Slack webhook
- **Retry:** 3 tentativas, 10s entre cada

### 🔟 **Log Execution**
- **Tipo:** Google Sheets
- **Função:** Registra execução em planilha
- **Colunas:** timestamp, status, sessions, spend, source

### ❌ **Error Handlers**
- **Format Error Message:** Formata erro em Slack blocks
- **Send Error to Slack:** Envia notificação de erro

---

## 🎨 Visual no n8n (Como vai aparecer)

Quando você importar, verá algo assim:

```
         ⏰
    [Schedule]
         │
         ▼
      📅 ┌──────────┐
         │ Weekend? │
         └──────────┘
         │
         ▼
      ❓ ┌─────────┐
         │ Should? │
         └─────────┘
         │
    ┌────┴────┐
    ▼         ▼
  🌐 GA4    💰 Ads
    │         │
    └────┬────┘
         ▼
    📁 Fallback
         ▼
    🧮 Calculate
         ▼
    🎨 Format
         ▼
    📤 Slack
         ▼
    📊 Log
```

---

## 🧪 Testar o Workflow

### Teste Manual (sem esperar cron)

1. No n8n, abra o workflow
2. Clique em **Test Workflow** (botão superior)
3. Clique em **Execute Workflow**
4. Veja a execução em tempo real!

### Ver Execuções Passadas

1. Clique na aba **Executions** (lado esquerdo)
2. Veja histórico de todas execuções
3. Clique em qualquer execução para debug

---

## ⚠️ Troubleshooting

### Problema: "Workflow not executing"
**Solução:**
- Verifique se está **Active** (toggle ligado)
- Verifique timezone do cron
- Veja logs em Executions

### Problema: "Slack webhook 404"
**Solução:**
- Verifique `DAY11_SLACK_WEBHOOK_URL` nas env vars
- Teste webhook manualmente com curl

### Problema: "CSV fallback failing"
**Solução:**
- Ajuste caminho dos CSVs no node "Fallback: Load CSV"
- Ou remova o node e use sempre API

### Problema: "Google Sheets connection"
**Solução:**
- Reconecte conta Google em Credentials
- Ou remova o node "Log Execution" (é opcional)

---

## 🎯 Próximos Passos

Depois de importar:

1. ✅ Configure webhook do Slack
2. ✅ Teste manualmente uma vez
3. ✅ Ative o workflow
4. ✅ Aguarde próximo 8am UTC ou force execução
5. ✅ Verifique Slack para o relatório!

---

## 🔄 Comparação: n8n vs Python

| Aspecto | n8n Workflow | Python (atual) |
|---------|-------------|----------------|
| **Visual** | ✅ Sim - arrastar e soltar | ❌ Código apenas |
| **Teste** | ✅ Interface gráfica | 🟡 Linha de comando |
| **Debug** | ✅ Ver dados em cada node | 🟡 Logs em arquivo |
| **Versionamento** | 🟡 Export JSON | ✅ Git nativo |
| **Portabilidade** | 🟡 Precisa n8n rodando | ✅ Roda em qualquer lugar |
| **Rápido Setup** | 🟡 Import + config | ✅ Imediato |
| **Clientes Low-Code** | ✅ Perfeito | ❌ Técnico demais |

**Recomendação:** Use ambos!
- **Python** para produção/CI/CD
- **n8n** para demos com clientes e prototipagem rápida

---

## 📸 Screenshots para Portfolio

Tire screenshots de:

1. **Workflow Canvas** (visão geral dos nodes)
2. **Execution Success** (mostrando dados fluindo)
3. **Slack Message** (o relatório formatado)
4. **Error Handling** (mostrando que erros são tratados)

Essas imagens são GOLD para Upwork! 🏆

---

**Criado para Day 11 - Retail Daily Performance Report Automation**
**Orchestration Week - Christmas Data Advent 2025** 🎄
