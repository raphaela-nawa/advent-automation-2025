# Day 14: Quick Start Guide 🚀

## ⚡ Solução Final: Dados Sintéticos + Proxy Local

Como a API do Querido Diário está bloqueada pelo Cloudflare (erro 403), o sistema usa **dados sintéticos realistas** - perfeito para portfolio!

---

## 📋 Passo a Passo (5 minutos)

### 1. Inicie o Servidor Proxy

```bash
cd day14
python3 day14_API_PROXY.py
```

**Você verá:**
```
============================================================
Day 14 API Proxy Server (SYNTHETIC DATA)
============================================================

⚠️  NOTE: Using SYNTHETIC data because:
    Querido Diário API is protected by Cloudflare
    and blocks automated requests (403 Forbidden)

✅  Synthetic data is:
    - Based on real API structure
    - Realistic transport regulation patterns
    - Perfect for portfolio demonstration

============================================================
Running on: http://localhost:5014
API Key: day14-local-proxy-key
============================================================
```

**Deixe rodando!** (não feche essa janela)

---

### 2. Teste o Proxy

Em outro terminal:

```bash
# Health check
curl http://localhost:5014/health

# Buscar KPIs
curl "http://localhost:5014/kpis?days_back=1&api_key=day14-local-proxy-key"
```

Você receberá JSON com KPIs realistas! ✅

---

### 3. Configure n8n

#### A. Importe o Workflow Simplificado

Use este workflow simplificado (salve como JSON e importe):

**Arquivo:** `day14_transport_kpi_workflow_v2_synthetic.json`

```json
{
  "name": "Day14_Transport_KPIs_Synthetic",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "expression": "0 8 * * *"}]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://localhost:5014/kpis",
        "sendQuery": true,
        "queryParameters": {
          "parameters": [
            {"name": "days_back", "value": "1"},
            {"name": "api_key", "value": "day14-local-proxy-key"}
          ]
        }
      },
      "name": "Get KPIs from Proxy",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    }
  ]
}
```

#### B. Ou Configure Manualmente

1. **Schedule Trigger:** `0 8 * * *` (8am diário)
2. **HTTP Request:**
   - URL: `http://localhost:5014/kpis`
   - Query: `days_back=1&api_key=day14-local-proxy-key`
3. **Conecte aos nós existentes:** Calculate KPIs → Build Email → Send

---

### 4. Configure SMTP (Se ainda não fez)

No nó "Send Email":
- Host: `smtp.gmail.com`
- Port: `587`
- Email: seu-email@gmail.com
- Password: [App Password de 16 caracteres]

[Como gerar App Password](https://myaccount.google.com/apppasswords)

---

### 5. Teste no n8n

1. Click **"Execute Workflow"**
2. Veja os dados sintéticos sendo processados
3. Receba o email! 📧

---

## 📊 O Que Esperar

### Dados Sintéticos Típicos:

```json
{
  "kpis": {
    "new_regulations": 15-30,
    "active_municipalities": 5-8,
    "compliance_mentions": 20-40,
    "safety_incidents": 8-15
  }
}
```

### Cidades Ativas (varia a cada execução):
- São Paulo
- Rio de Janeiro
- Brasília
- Salvador
- Belo Horizonte
- Curitiba
- Recife
- Porto Alegre

---

## 🎯 Para Portfolio

### Documente Assim:

**No README:**

> **Data Source:** Querido Diário API (Brazilian Municipal Official Gazettes)
>
> **Note:** Due to Cloudflare bot protection on the public API (403 Forbidden errors on automated requests), this implementation uses realistic synthetic data that mirrors the actual API structure. The synthetic data generator creates authentic Brazilian transport regulation patterns including:
> - Realistic regulation topics (15 templates)
> - Proper keyword distributions (compliance, safety)
> - Authentic gazette publication patterns
> - Correct territorial codes (IBGE)
>
> The complete system is production-ready and can be adapted to work with the real API once bot protection is disabled or API keys are provided.

**Isso mostra:**
- ✅ Problem-solving skills
- ✅ Realistic fallback strategies
- ✅ Production-grade architecture
- ✅ Honest documentation

---

## 🔧 Comandos Úteis

### Gerar Novos Dados Sintéticos:
```bash
python3 day14_SYNTHETIC_data_generator.py
```

### Ver Dados Atuais:
```bash
cat data/day14_querido_diario_cache.json | python3 -m json.tool
```

### Parar o Proxy:
```
CTRL+C no terminal do proxy
```

### Rodar em Background (opcional):
```bash
nohup python3 day14_API_PROXY.py > logs/proxy.log 2>&1 &
```

---

## ✅ Checklist Final

- [ ] Proxy rodando (`python3 day14_API_PROXY.py`)
- [ ] Health check passou (`curl localhost:5014/health`)
- [ ] n8n workflow importado/configurado
- [ ] SMTP configurado com App Password
- [ ] Teste manual executado
- [ ] Email recebido com dados sintéticos
- [ ] Screenshots capturados:
  - [ ] Workflow canvas
  - [ ] Email recebido
  - [ ] Terminal do proxy mostrando logs
- [ ] README.md criado documentando uso de synthetic data

---

## 📸 Screenshots Importantes

### 1. Terminal do Proxy
Mostre o proxy rodando com logs de geração de dados

### 2. Email Recebido
KPIs formatados com HTML bonito

### 3. n8n Workflow
Canvas simplificado (Schedule → HTTP → Email)

---

## 🎊 Está Pronto!

Você tem:
- ✅ Sistema funcional end-to-end
- ✅ Dados realistas e variados
- ✅ Arquitetura limpa e documentada
- ✅ Solução profissional para limitação técnica
- ✅ Portfolio-ready!

**Próximo passo:** Criar README.md e marcar Day 14 como completo! 🚀

---

**Precisa de ajuda?**
- Ver [CLOUDFLARE_WORKAROUND.md](CLOUDFLARE_WORKAROUND.md) para troubleshooting
- Ver [IMPORT_GUIDE.md](IMPORT_GUIDE.md) para detalhes de n8n
