# 🔄 Pipeline Atualizado - Day 05

## ⚠️ CORREÇÃO CRÍTICA APLICADA

O pipeline foi corrigido para fazer **extração completa do catálogo** ao invés de busca limitada.

---

## 📋 Novo Fluxo de Execução

### Passo 1: Transcrever Áudios (30 min)
```bash
python day05_DATA_transcribe_whisper.py
```
**Output:** Transcripts em `data/raw/transcripts/`

---

### Passo 2: Extrair Menções com GPT-4 (25 min)
```bash
python day05_PIPELINE_extract_items.py
```
**Output:** `data/processed/items_to_validate.csv`

---

### Passo 3: **[NOVO]** Extrair Catálogo Completo (45 min)
```bash
python day05_DATA_extract_complete_catalog.py
```

**O que faz:**
- ✅ Descobre total de itens no acervo (estimado: 2000+)
- ✅ Extrai **TODOS** os itens com paginação
- ✅ Salva em database SQLite local
- ✅ Valida completude (>95%)

**Output:** `data/processed/museu_paulista_completo.db`

**Estimativa:**
- Total esperado: **2000-5000+ itens**
- Fotos do Militão: **333+ itens**
- Tempo de extração: **30-45 min**

---

### Passo 4: Validação Manual (15 min)
```bash
# Abrir CSV manualmente
open data/processed/items_to_validate.csv
```

**Ações:**
1. Revisar cada `item_mention`
2. Marcar `validated` como `yes` ou `no`
3. Salvar arquivo

---

### Passo 5: **[ATUALIZADO]** Busca Local (10 min)
```bash
python day05_DATA_search_local_db.py
```

**Mudanças:**
- ❌ ~~Busca via API limitada~~
- ✅ Busca no database SQLite completo
- ✅ Fuzzy matching com **TODOS** os itens
- ✅ Melhor precisão de matching

**Output:** `data/processed/matched_items.csv`

---

### Passo 6: Load para BigQuery (5 min)
```bash
python day05_DATA_load_bigquery.py
```
**Output:** BigQuery table `podcast_museum_mentions`

---

## 📊 Validação de Sucesso

### Após Passo 3 (Extração Completa):
```bash
python -c "
import sqlite3
conn = sqlite3.connect('data/processed/museu_paulista_completo.db')
total = conn.execute('SELECT COUNT(*) FROM items').fetchone()[0]
print(f'✅ Total de itens no DB: {total:,}')
print(f'Esperado: >2000 itens')
conn.close()
"
```

### Após Passo 5 (Busca Local):
```bash
python -c "
import pandas as pd
df = pd.read_csv('data/processed/matched_items.csv')
matched = df['matched'].sum()
total = len(df)
print(f'✅ Matched: {matched}/{total}')
print(f'Taxa de match: {matched/total*100:.1f}%')
"
```

---

## 🎯 Critérios de Sucesso Final

- ✅ Database SQLite com **2000+ itens**
- ✅ **>80%** de completude vs total da API
- ✅ Fuzzy matching com confiança **>0.6**
- ✅ Dados carregados no BigQuery

---

## 📁 Arquivos Gerados

```
day05/data/processed/
├── items_to_validate.csv           # GPT extractions
├── museu_paulista_completo.db      # NOVO: Full catalog
├── extraction_stats.json           # NOVO: Stats
├── matched_items.csv               # Search results
└── final_bigquery_data.csv         # Final output
```

---

## ⏱️ Tempo Total Atualizado

| Passo | Tempo | Total |
|-------|-------|-------|
| Transcrição | 30 min | 30 min |
| Extração GPT | 25 min | 55 min |
| **Extração Completa** | **45 min** | **100 min** |
| Validação Manual | 15 min | 115 min |
| Busca Local | 10 min | 125 min |
| BigQuery Load | 5 min | 130 min |
| **Total** | **~2h 10min** | |

---

## 🚀 Comando Rápido (Tudo em Sequência)

```bash
cd day05

# Passo 1
python day05_DATA_transcribe_whisper.py

# Passo 2
python day05_PIPELINE_extract_items.py

# Passo 3 - NOVO!
python day05_DATA_extract_complete_catalog.py

# Passo 4 - MANUAL
echo "⚠️  Valide items_to_validate.csv manualmente!"
open data/processed/items_to_validate.csv

# Passo 5 - ATUALIZADO!
python day05_DATA_search_local_db.py

# Passo 6
python day05_DATA_load_bigquery.py
```

---

**Melhorias Implementadas:**
- ✅ Extração completa do acervo (2000+ itens)
- ✅ Database SQLite local para busca rápida
- ✅ Fuzzy matching mais preciso
- ✅ Melhor taxa de correspondência
- ✅ Pipeline mais robusto
