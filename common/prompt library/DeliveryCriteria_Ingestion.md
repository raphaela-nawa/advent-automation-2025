# Delivery Criteria - Ingestion Projects (Days 1A to 1E)

## 📋 MATRIZ DE MICRO-DECISÕES

### ✅ OUTPUT OBRIGATÓRIO (Você DEVE entregar isso)

| Item | Descrição | Localização |
|------|-----------|-------------|
| **Dados estruturados** | CSV/JSON/Parquet com schema documentado | `/dayXX/data/processed/` ou BigQuery |
| **Script de extração** | `dayXX_DATA_extract.py` executável sem erros | `/dayXX/dayXX_DATA_extract.py` |
| **Script de loading** | `dayXX_DATA_load.py` salva dados no destino | `/dayXX/dayXX_DATA_load.py` |
| **Configuração reproduzível** | `.env.example` com variáveis DAY específicas | `/dayXX/.env.example` |
| **Dependências** | Day-specific requirements (se necessário) | `/dayXX/dayXX_requirements.txt` |
| **Documentação mínima** | README com Quick Start copy-paste | `/dayXX/README.md` |

### ❌ OUTPUT PROIBIDO (NÃO faça isso - vai estourar 3h)

| Item | Por que NÃO |
|------|-------------|
| **Dashboards/visualizações** | Isso é Pilar D (Dashboard) |
| **Orquestração/scheduling** | Isso é Pilar C (Orchestration) |
| **Análises/insights sobre os dados** | Isso é Pilar E (AI Insights) |
| **Modelagem de dados** | Isso é Pilar B (Modeling) |
| **Testes end-to-end complexos** | Só testes unitários básicos (< 30 min) |
| **Otimizações prematuras** | Performance vem depois, funcionalidade primeiro |
| **UI/Frontend** | É CLI ou script Python, ponto final |

---

## ✅ CHECKLIST DE "PROJETO COMPLETO"

### **ANTES de considerar o projeto pronto, verifique:**

#### **1. Funcionalidade Core**
- [ ] `python dayXX_DATA_extract.py` executa sem erros
- [ ] Dados aparecem em `/dayXX/data/processed/` (ou BigQuery) com estrutura esperada
- [ ] Schema está documentado (README ou comments no código)

#### **2. Reprodutibilidade** (respeitando regras do PROMPT_project_setup.md)
- [ ] `.env.example` lista TODAS as variáveis necessárias (formato: `KEY_OPENAI_DAYXX`, `DAYXX_SPECIFIC_VAR`)
- [ ] Variáveis adicionadas ao root `config/.env` seguindo convenção existente
- [ ] `dayXX_requirements.txt` tem dependências específicas (se necessário)
- [ ] README tem seção "Quick Start" que funciona copy-paste

#### **3. Qualidade Mínima**
- [ ] Código tem docstrings nas funções principais
- [ ] Há tratamento de erros básico (try/except em chamadas de API)
- [ ] Logs informativos (print ou logging mostrando progresso)

#### **4. Nomenclatura (CRÍTICO)**
- [ ] Todos os arquivos têm prefixo `dayXX_`
- [ ] Variáveis globais têm prefixo `dayXX_` ou `DAYXX_`
- [ ] Classes têm prefixo `dayXX_`
- [ ] Funções principais têm prefixo `dayXX_`

#### **5. Entrega**
- [ ] Git commit com mensagem descritiva
- [ ] Push para GitHub

#### **6. Teste Final (5 minutos)**
- [ ] Clone o repo em outra pasta
- [ ] Rode os comandos do README
- [ ] Funciona? ✅ Projeto completo. Não funciona? ❌ Debug e fix.

---

## ⏱️ GESTÃO DE TEMPO (3 horas)

### **Distribuição ideal:**

| Fase | Tempo | O que fazer |
|------|-------|-------------|
| **Setup** | 20 min | Criar pasta dayXX/, copiar estrutura base, configurar .env |
| **Extract** | 90 min | Implementar `dayXX_DATA_extract.py`, testar API, tratar erros |
| **Load** | 40 min | Implementar `dayXX_DATA_load.py`, salvar dados |
| **Docs** | 20 min | README Quick Start + docstrings |
| **Buffer** | 10 min | Imprevistos, ajustes finais |

### **🚨 SINAIS DE QUE VOCÊ ESTÁ DESVIANDO DO ESCOPO:**

- Você está escrevendo CSS
- Você está criando um dashboard
- Você está fazendo análise exploratória dos dados
- Você está otimizando performance antes de funcionar
- Você está adicionando "features legais" não solicitadas

**Se isso acontecer:** PARE. Volte aos requisitos. Entregue o mínimo prometido primeiro.

---

## 🎯 CRITÉRIOS ESPECÍFICOS POR PROJETO

### **Day 1A (Daud - GA4 + Google Ads)**

**Fontes de dados:**
- GA4 Demo Account (Google Merchandise Store) OU dados sintéticos (backup após 1h)
- Google Ads dados sintéticos (no free sandbox available)

**Output obrigatório:**
- [ ] Tabela `ga4_sessions` em BigQuery: `date, sessions, conversions, bounce_rate, source`
- [ ] Tabela `google_ads_campaigns` em BigQuery: `date, campaign_name, spend, clicks, impressions, conversions`
- [ ] Join preparado (mesmo date field) para análise futura
- [ ] Schema documentado no README

**Quando parar:**
- ✅ Dados de GA4 (real ou sintético) em BigQuery
- ✅ Dados de Google Ads (sintético) em BigQuery
- ✅ README explica como conectar GA4 real vs. sintético
- ❌ NÃO faça: Dashboard de ROAS, análise de campanhas, alertas

**Arquivos esperados:**
```
dayXX/
├── data/
│   ├── raw/
│   │   ├── ga4_sample.json (se Demo Account)
│   │   └── ads_synthetic.csv
│   └── processed/
│       ├── ga4_sessions.csv
│       └── ads_campaigns.csv
├── dayXX_DATA_extract_ga4.py
├── dayXX_DATA_extract_ads.py (synthetic generator)
├── dayXX_DATA_load_bigquery.py
├── dayXX_CONFIG_settings.py
├── dayXX_requirements.txt (se necessário)
├── .env.example
└── README.md
```

**Validação final:**
```sql
-- Rode no BigQuery para validar
SELECT COUNT(*) FROM `project.dataset.ga4_sessions`;
SELECT COUNT(*) FROM `project.dataset.google_ads_campaigns`;
-- Deve retornar > 0 rows
```

**Nomenclatura de variáveis:**
```python
# ✅ CORRETO
DAYXX_GA4_PROPERTY_ID = "12345"
DAYXX_ADS_CUSTOMER_ID = "678-901-2345"

class dayXX_GA4Extractor:
    pass

def dayXX_process_ga4_sessions():
    pass

# ❌ ERRADO (causa conflitos)
GA4_PROPERTY_ID = "12345"
class GA4Extractor:
    pass
```

---

### **Day 1B (Samira - Instagram Creator)**

**Fonte de dados:**
- Instagram dados sintéticos (CSV gerado manualmente)

**Output obrigatório:**
- [ ] CSV sintético: `instagram_posts.csv` com: `post_id, date, likes, comments, reach, post_type, caption_preview`
- [ ] Tabela `instagram_engagement` em BigQuery
- [ ] Engagement rate calculado: `(likes + comments) / reach`
- [ ] Schema documentado

**Quando parar:**
- ✅ CSV sintético com 30-50 posts (mix de imagens/reels/carousels)
- ✅ Dados em BigQuery com engagement_rate calculado
- ✅ README explica estrutura de dados e como adicionar mais posts
- ❌ NÃO faça: Análise de "qual post performa melhor", gráficos, predictions

**Arquivos esperados:**
```
dayXX/
├── data/
│   ├── raw/
│   │   └── instagram_synthetic.csv
│   └── processed/
│       └── instagram_engagement.csv
├── dayXX_DATA_generate_synthetic.py (cria o CSV)
├── dayXX_DATA_load_bigquery.py
├── dayXX_CONFIG_settings.py
├── .env.example
└── README.md
```

---

### **Day 1C (Maru - GDPR Lead Ingestion)**

**Fonte de dados:**
- Webhook local (Flask) + leads sintéticos (JSON payloads)

**Output obrigatório:**
- [ ] Webhook Flask rodando em `localhost:5000/leads`
- [ ] Tabela `gdpr_leads` em BigQuery: `lead_id, name, email, consent_timestamp, consent_purpose, ip_address, data_retention_date`
- [ ] Exemplo de payload JSON no README
- [ ] Lógica de retention: `data_retention_date = consent_timestamp + 30 days` se não consentido

**Quando parar:**
- ✅ Webhook recebe POST request com JSON
- ✅ Valida campos obrigatórios (consent_timestamp, purpose)
- ✅ Salva no BigQuery com metadata GDPR
- ✅ README tem exemplo curl para testar
- ❌ NÃO faça: UI do formulário, validação complexa de email, automação de deletion

**Arquivos esperados:**
```
dayXX/
├── data/
│   └── sample_payloads/
│       ├── lead_with_consent.json
│       └── lead_without_consent.json
├── dayXX_APP_webhook_server.py (Flask app)
├── dayXX_PIPELINE_gdpr_validator.py
├── dayXX_DATA_load_bigquery.py
├── dayXX_CONFIG_settings.py
├── .env.example
└── README.md
```

**Exemplo payload (README):**
```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "consent_given": true,
  "consent_purpose": "marketing_communications",
  "ip_address": "192.168.1.1",
  "timestamp": "2024-11-26T10:30:00Z"
}
```

**Teste:**
```bash
curl -X POST http://localhost:5000/leads \
  -H "Content-Type: application/json" \
  -d @data/sample_payloads/lead_with_consent.json
```

**Nomenclatura:**
```python
# ✅ CORRETO
DAYXX_WEBHOOK_PORT = 5000
DAYXX_GDPR_RETENTION_DAYS = 30

class dayXX_GDPRValidator:
    pass

def dayXX_calculate_retention_date():
    pass
```

---

### **Day 1D (Pedro - Crypto Price Tracker)**

**Fonte de dados:**
- CoinGecko API (free, no auth required)

**Output obrigatório:**
- [ ] Dockerfile funcional
- [ ] `docker-compose.yml` para rodar tudo
- [ ] Tabela `cardano_prices` em BigQuery: `timestamp, price_usd, market_cap, volume_24h, price_change_24h`
- [ ] Container executa, extrai dados, salva em BigQuery, e para

**Quando parar:**
- ✅ `docker-compose up` funciona sem erros
- ✅ Dados de Cardano (ADA) aparecem no BigQuery
- ✅ README explica: build, run, environment variables
- ❌ NÃO faça: CI/CD complexo, múltiplas cryptos, análise de tendências, scheduling

**Arquivos esperados:**
```
dayXX/
├── data/
│   └── processed/
│       └── cardano_prices.csv (local backup)
├── dayXX_DATA_extract_coingecko.py
├── dayXX_DATA_load_bigquery.py
├── dayXX_CONFIG_settings.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

**Dockerfile (estrutura esperada):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY dayXX_requirements.txt .
RUN pip install --no-cache-dir -r dayXX_requirements.txt
COPY dayXX_*.py ./
CMD ["python", "dayXX_DATA_extract_coingecko.py"]
```

**Teste:**
```bash
docker-compose up --build
# Deve ver logs: "Extracting Cardano prices... Done. Loaded to BigQuery."
```

**Nomenclatura:**
```python
# ✅ CORRETO
DAYXX_COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
DAYXX_CRYPTO_SYMBOL = "cardano"

class dayXX_CryptoExtractor:
    pass

def dayXX_fetch_cardano_price():
    pass
```

---

### **Day 1E (Paula - Museu Ipiranga Cultural Data)**

**Fonte de dados:**
- Tainacan REST API (Museu Paulista): `https://acervoonline.mp.usp.br/wp-json/tainacan/v2/`
- Spotify for Podcasters dados sintéticos (no real credentials)

**Output obrigatório:**
- [ ] Tabela `museum_artifacts` em BigQuery: `item_id, title, category, period, author, image_url, description`
- [ ] Tabela `podcast_episodes` (sintético): `episode_id, title, publish_date, downloads, retention_rate, theme_category`
- [ ] Join logic preparado (theme_category comum entre tabelas)
- [ ] README explica estrutura de dados culturais

**Quando parar:**
- ✅ 100-200 itens do acervo Ipiranga em BigQuery (via Tainacan API)
- ✅ 10-15 episódios sintéticos do podcast
- ✅ Categorias mapeadas (ex: "colonial_artifacts", "photography", "paintings")
- ✅ README tem link para acervo online
- ❌ NÃO faça: Análise de correlação tema-engagement, gráficos, RAG sobre descrições

**Arquivos esperados:**
```
dayXX/
├── data/
│   ├── raw/
│   │   ├── tainacan_items.json
│   │   └── podcast_episodes_synthetic.csv
│   └── processed/
│       ├── museum_artifacts.csv
│       └── podcast_episodes.csv
├── dayXX_DATA_extract_tainacan.py
├── dayXX_DATA_generate_podcast.py (synthetic)
├── dayXX_DATA_load_bigquery.py
├── dayXX_CONFIG_settings.py
├── .env.example
└── README.md
```

**Tainacan API exemplo:**
```python
import requests

# ✅ CORRETO - com nomenclatura day-scoped
DAYXX_TAINACAN_API_URL = "https://acervoonline.mp.usp.br/wp-json/tainacan/v2/"

def dayXX_fetch_museum_items():
    response = requests.get(
        f"{DAYXX_TAINACAN_API_URL}/items",
        params={"perpage": 100}
    )
    return response.json()
```

---

## 🔄 REGRA DE PIVOT (1 hora)

**Para Day 1A especificamente:**

Se após **1 hora** você ainda não conseguiu:
- Configurar GA4 Demo Account OU
- Extrair dados reais da API

➡️ **PIVOT IMEDIATO para dados sintéticos:**

1. Crie `data/raw/ga4_synthetic.csv`:
```csv
date,sessions,conversions,bounce_rate,source
2024-11-01,1250,45,0.42,google
2024-11-02,1180,38,0.45,facebook
2024-11-03,1320,52,0.39,direct
...
```

2. Crie `data/raw/ads_synthetic.csv`:
```csv
date,campaign_name,spend,clicks,impressions,conversions
2024-11-01,Brand Campaign,450.00,320,12500,18
2024-11-02,Product Launch,680.00,510,18200,25
...
```

3. Ajuste `dayXX_DATA_extract.py` para ler CSVs locais
4. Continue normalmente (load → BigQuery → README)

**NÃO gaste mais de 1h tentando fazer APIs reais funcionarem. O objetivo é entregar, não é perfeccionismo.**

---

## 📊 VALIDAÇÃO FINAL (Todos os Projetos)

Antes de dar push:
```bash
# 1. Teste em ambiente limpo
cd /tmp
git clone seu-repo
cd advent-automation-2025/dayXX

# 2. Configure .env (adicione variáveis do projeto ao root config/.env)
# Certifique-se de seguir convenção: KEY_OPENAI_DAYXX, DAYXX_SPECIFIC_VAR

# 3. Execute
python dayXX_DATA_extract.py
python dayXX_DATA_load.py

# 4. Valide
# - Dados apareceram em BigQuery? ✅
# - Logs fazem sentido? ✅
# - Erros são informativos? ✅
# - Nomenclatura está correta (dayXX_ prefix)? ✅
```

Se TUDO acima funciona → ✅ **Projeto completo**

---

## 🔧 CHECKLIST DE INTEGRAÇÃO COM ESTRUTURA EXISTENTE

Antes de finalizar qualquer projeto de Ingestion, verifique:

- [ ] Variáveis de ambiente adicionadas a `config/.env` seguindo convenção existente
- [ ] Dependências específicas documentadas em `dayXX_requirements.txt` (se necessário)
- [ ] Dependências comuns adicionadas ao root `requirements.txt` (apenas se globalmente relevantes)
- [ ] TODOS os arquivos têm prefixo `dayXX_`
- [ ] TODAS as variáveis/classes/funções seguem nomenclatura isolada
- [ ] README explica claramente como configurar variáveis de ambiente
- [ ] Projeto funciona de forma INDEPENDENTE (não depende de outros days)

---

## 💡 LEMBRETE FINAL

**Você está construindo um PORTFOLIO, não um produto de produção.**

O objetivo é demonstrar:
- ✅ Você sabe usar APIs
- ✅ Você sabe estruturar dados
- ✅ Você sabe documentar
- ✅ Você consegue entregar em 3h
- ✅ Você sabe trabalhar com isolamento de código

**NÃO é demonstrar:**
- ❌ Sistema perfeito e bug-free
- ❌ Performance otimizada
- ❌ Todos os edge cases tratados

**Foco: Funcional > Perfeito. Documentado > Complexo. Entregue > Ideal. Isolado > Compartilhado.**
