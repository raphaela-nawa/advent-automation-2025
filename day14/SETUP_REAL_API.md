# Day 14: Setup com API Real ✅

## 🎉 Descoberta: API Funciona!

A API do Querido Diário está funcionando perfeitamente no endpoint correto:
- ✅ URL: `https://api.queridodiario.ok.org.br`
- ✅ Status: HTTP 200 OK
- ✅ Sem autenticação necessária
- ✅ Parâmetros corrigidos

---

## 🚀 Passo a Passo (5 minutos)

### 1. Inicie o Proxy com API Real

```bash
cd day14
python3 day14_API_PROXY.py
```

**Você verá:**
```
============================================================
Day 14 API Proxy Server (REAL DATA)
============================================================

✅  Using REAL data from:
    Querido Diário API (Brazilian Government)
    https://api.queridodiario.ok.org.br

📊  Monitoring:
    - 10 major Brazilian cities
    - Transport & mobility regulations
    - Compliance mentions
    - Safety incidents

============================================================
Running on: http://localhost:5014
API Key: day14-local-proxy-key

Endpoints:
  GET /health
  GET /kpis?days_back=15&api_key=YOUR_KEY

Note: Using days_back=15 for better results
      (municipalities don't publish daily)
============================================================
```

**IMPORTANTE:** Deixe rodando! Não feche essa janela.

---

### 2. Teste o Proxy (Verificar que funciona)

Em outro terminal:

```bash
# Health check
curl http://localhost:5014/health

# Buscar KPIs (15 dias para primeira execução)
curl "http://localhost:5014/kpis?days_back=15&api_key=day14-local-proxy-key"
```

**O que esperar:**
- Demora ~30-60 segundos (consulta 10 cidades × 3 tipos de keywords)
- Retorna JSON com KPIs reais
- Logs no terminal do proxy mostram progresso

---

### 3. Configurar n8n Workflow

#### ⚠️ MUDANÇAS NECESSÁRIAS NO N8N

**Se você já importou o workflow, precisa mudar APENAS 1 parâmetro:**

### No Nó "Query Local Proxy" (HTTP Request):

**Antes:**
```
URL: http://localhost:5014/kpis
Query Parameters:
  - days_back: 1
  - api_key: day14-local-proxy-key
```

**Depois (MUDAR PARA 15):**
```
URL: http://localhost:5014/kpis
Query Parameters:
  - days_back: 15  ← MUDAR DE 1 PARA 15
  - api_key: day14-local-proxy-key
```

**Como mudar:**
1. Abra o workflow no n8n
2. Clique no nó "HTTP Request" ou "Query Local Proxy"
3. Em "Query Parameters", mude `days_back` de `1` para `15`
4. Click "Execute Node" para testar
5. Salve o workflow

---

### 4. Por Que 15 Dias?

**Razão:**
- Municípios não publicam diários oficiais TODOS os dias
- Alguns publicam 1-2x por semana
- 15 dias garante encontrar publicações

**Depois da primeira execução:**
- Você pode reduzir para 7 dias (semanal)
- Ou manter 15 dias para relatório quinzenal

---

### 5. Teste Manual no n8n

1. **No n8n, clique "Execute Workflow"**
2. **Aguarde ~1 minuto** (API está consultando 10 cidades)
3. **Verifique o nó "Calculate KPIs":**
   - Deve ter `new_regulations > 0`
   - Deve ter `active_municipalities > 0`
4. **Verifique seu email!** 📧

---

## 📊 O Que Esperar (Dados Reais)

### KPIs Típicos (15 dias):

```json
{
  "new_regulations": 5-20,
  "active_municipalities": 3-7,
  "compliance_mentions": 10-40,
  "safety_incidents": 5-25
}
```

**Nota:** Varia muito! Alguns períodos têm mais publicações que outros.

---

## 🔧 Troubleshooting

### Problema: "KPIs todos em 0"

**Causa:** Período sem publicações sobre transporte

**Solução:**
1. Aumente `days_back` para 30
2. Ou use keywords mais genéricos
3. Normal em alguns períodos

### Problema: "Proxy lento (>2 minutos)"

**Causa:** Consultando muitas cidades/keywords

**Solução:** Normal na primeira execução. API faz 30 requisições (10 cidades × 3 keywords).

### Problema: "Connection refused"

**Causa:** Proxy não está rodando

**Solução:**
```bash
cd day14
python3 day14_API_PROXY.py
```

---

## 📋 Checklist de Setup

- [ ] Proxy rodando (`python3 day14_API_PROXY.py`)
- [ ] Health check passou (`curl localhost:5014/health`)
- [ ] n8n workflow importado
- [ ] Parâmetro `days_back` mudado para `15`
- [ ] SMTP configurado (Gmail App Password)
- [ ] Teste manual executado no n8n
- [ ] Email recebido com dados reais! 🎉

---

## 🎯 Para Produção

### Agendamento Recomendado:

**Opção A: Quinzenal (recomendado)**
- Cron: `0 8 1,15 * *` (dia 1 e 15 de cada mês, 8am)
- `days_back: 15`

**Opção B: Semanal**
- Cron: `0 8 * * 1` (segundas 8am)
- `days_back: 7`

**Opção C: Diário (pode ter 0 resultados)**
- Cron: `0 8 * * *` (diário 8am)
- `days_back: 1`

### No Nó "Schedule Trigger" do n8n:

Mude a cron expression conforme preferência acima.

---

## 📸 Screenshots para Portfolio

Depois de executar com sucesso:

1. **Terminal do Proxy** mostrando logs de API real
2. **Email recebido** com KPIs de dados reais
3. **n8n Workflow** executado com sucesso

**Destaque no README:**
> Uses **real government data** from Querido Diário API (Brazilian Official Gazettes)

---

## ✅ Está Pronto!

Sistema funcionando com:
- ✅ **Dados reais** do governo brasileiro
- ✅ **10 municípios** monitorados
- ✅ **4 KPIs** calculados
- ✅ **Email HTML** profissional
- ✅ **Automação completa**

**Próximo passo:** Execute manualmente no n8n e veja os dados reais chegarem! 🚀

---

**Precisa de ajuda?** Qualquer dúvida, só perguntar!
