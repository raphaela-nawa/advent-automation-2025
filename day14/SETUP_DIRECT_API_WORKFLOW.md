# Day 14: Direct API Workflow Setup Guide 🚀

## ✅ Novo Workflow (v3) - Conexão Direta com API

Este workflow elimina o proxy e conecta o n8n **diretamente** à API do Querido Diário.

---

## 📥 Importar Workflow no n8n

### 1. Abra o n8n

```bash
# Se ainda não está rodando:
npx n8n
```

### 2. Importe o Workflow

1. Click no menu **"Workflows"** (canto superior esquerdo)
2. Click **"Import"**
3. Selecione o arquivo: `day14/workflows/day14_transport_kpi_workflow_v3_direct_api.json`
4. Click **"Import"**

---

## ⚙️ Configuração Necessária (3 minutos)

### 1. Configurar SMTP no Nó "Send Email"

1. Click no nó **"Send Email"**
2. Em **"Credential for SMTP"**, click **"Create New Credential"**
3. Preencha:
   - **User**: seu-email@gmail.com
   - **Password**: [App Password de 16 caracteres]
   - **Host**: smtp.gmail.com
   - **Port**: 587
   - **SSL/TLS**: DESLIGADO (use TLS)

**Como gerar Gmail App Password:**
- Acesse: https://myaccount.google.com/apppasswords
- Crie senha para "Mail"
- Copie a senha de 16 caracteres

### 2. Atualizar Email de Destino

No nó **"Send Email"**:
- **From Email**: seu-email@gmail.com
- **To Email**: seu-email@gmail.com (ou outro destinatário)

---

## 🎯 Como Funciona

### Fluxo do Workflow:

```
Schedule Trigger (8am daily)
    ↓
Prepare City Queries (10 cidades, 15 dias)
    ↓
Split in Batches (grupos de 3 para respeitar rate limit)
    ↓
Query API (https://api.queridodiario.ok.org.br/gazettes)
    ↓
Wait 1 second (rate limiting: 60 req/min)
    ↓
Attach City Name (adicionar nome da cidade à resposta)
    ↓
[Loop até processar todas as cidades]
    ↓
Aggregate Results (combinar respostas)
    ↓
Calculate KPIs (4 métricas)
    ↓
Build HTML Email (template profissional)
    ↓
Send Email (SMTP)
```

### Rate Limiting:
- **API Limit**: 60 requests/minute
- **Workflow**: 10 cidades × 1 request = 10 total requests
- **Batches**: 3 cidades por vez, 1 segundo de espera
- **Tempo total**: ~10-15 segundos ✅

---

## 🔍 Parâmetros da API

O workflow usa os parâmetros corretos:

```
GET https://api.queridodiario.ok.org.br/gazettes
?territory_ids=3550308              # IBGE code
&querystring=transporte OR mobilidade OR trânsito...
&published_since=2025-11-30         # 15 dias atrás
&published_until=2025-12-15         # hoje
&excerpt_size=500                   # caracteres por excerpt
&number_of_excerpts=3               # excerpts por gazette
&size=10                            # max gazettes por cidade
```

---

## 🧪 Teste Manual

### 1. Ative o Workflow

Click no switch **"Active"** no canto superior direito.

### 2. Execute Manualmente

Click no botão **"Execute Workflow"** (▶️).

### 3. Acompanhe a Execução

Você verá cada nó sendo executado:
- ✅ Schedule Trigger
- ✅ Prepare City Queries (10 items)
- ✅ Query API (10× com 1s delay)
- ✅ Aggregate Results
- ✅ Calculate KPIs
- ✅ Send Email

**Tempo esperado:** 10-20 segundos

### 4. Verifique seu Email! 📧

Você receberá um email com:
- 4 KPIs calculados
- Lista de municípios ativos
- Insights automáticos
- Design HTML responsivo

---

## 📊 KPIs Esperados (15 dias)

Valores típicos com dados reais:

```json
{
  "new_regulations": 8-25,
  "active_municipalities": 3-7,
  "compliance_mentions": 5-30,
  "safety_incidents": 3-15
}
```

**Nota:** Varia conforme período! Alguns períodos têm mais publicações.

---

## 🔧 Troubleshooting

### Problema: "0 regulations found"

**Causa:** Período sem publicações sobre transporte

**Solução:**
1. Normal para alguns períodos
2. Keywords muito específicos
3. Tente aumentar `periodDays` de 15 para 30 dias

**Como mudar:**
- No nó "Prepare City Queries"
- Linha: `startDate.setDate(startDate.getDate() - 15);`
- Mude `15` para `30`

### Problema: "Error 403 Forbidden"

**Causa:** API bloqueou requisição

**Solução:**
1. Verifique se URL está correta: `api.queridodiario.ok.org.br` (não `queridodiario.ok.org.br/api`)
2. Adicione 2 segundos de wait (mudar de 1 para 2)
3. Reduza batch size de 3 para 1

### Problema: "SMTP Error"

**Causa:** Configuração de email

**Solução:**
1. Use port 587 (não 465)
2. Desative opção "SSL/TLS" (use TLS simples)
3. Verifique App Password (16 caracteres, sem espaços)

### Problema: "Timeout"

**Causa:** API lenta ou sem resposta

**Solução:**
- No nó "Query API"
- Em "Options" → "Timeout"
- Aumente para 60000ms (60 segundos)

---

## 🗓️ Agendamento Recomendado

No nó **"Schedule Trigger"**, configure o cron:

### Opção A: Diário (8am) ⭐
```
0 8 * * *
```
- Bom para monitoramento contínuo
- Pode ter dias com 0 resultados

### Opção B: Semanal (Segundas 8am)
```
0 8 * * 1
```
- Mais resultados por relatório
- Menos emails

### Opção C: Quinzenal (dia 1 e 15, 8am)
```
0 8 1,15 * *
```
- Período ideal (15 dias de lookback)
- 2 relatórios/mês

---

## ✅ Checklist de Setup

- [ ] Workflow importado no n8n
- [ ] SMTP configurado com App Password
- [ ] Emails (from/to) atualizados
- [ ] Teste manual executado com sucesso
- [ ] Email recebido com KPIs reais
- [ ] Workflow ativado (switch "Active")
- [ ] Cron agendado conforme preferência

---

## 🎯 Diferenças da Versão Anterior

| Aspecto | v2 (Proxy) | v3 (Direct API) ✅ |
|---------|------------|-------------------|
| **Conexão** | n8n → Proxy → API | n8n → API |
| **Dependências** | Flask server rodando | Nenhuma |
| **Complexidade** | 2 componentes | 1 componente |
| **Manutenção** | Proxy + n8n | Só n8n |
| **Performance** | +1 hop de rede | Direto |
| **Falhas** | Proxy ou API | Só API |

---

## 📸 Screenshots para Portfolio

Capture:

1. **n8n Canvas**: Workflow completo ativo
2. **Execution Log**: Mostrando 10 cidades processadas
3. **Email Recebido**: KPIs com dados reais
4. **KPI Card Details**: Valores específicos

---

## 🚀 Está Pronto!

Sistema completo:
- ✅ Conexão direta com API real
- ✅ 10 municípios brasileiros
- ✅ 4 KPIs calculados
- ✅ Email HTML profissional
- ✅ Rate limiting respeitado (60 req/min)
- ✅ Agendamento automático
- ✅ Zero dependências externas (proxy removido)

**Próximo passo:** Execute manualmente e veja os dados reais chegarem! 🎉

---

## 🔗 Links Úteis

- **API Docs**: https://api.queridodiario.ok.org.br/docs
- **Querido Diário**: https://queridodiario.ok.org.br
- **n8n Docs**: https://docs.n8n.io
- **Gmail App Passwords**: https://myaccount.google.com/apppasswords

---

**Precisa de ajuda?** Qualquer dúvida, só perguntar! 🤝
