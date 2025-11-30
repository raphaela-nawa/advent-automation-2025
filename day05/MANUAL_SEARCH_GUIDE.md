# 🔍 Guia de Busca Manual - Day 05

## 📋 Resumo da Abordagem Melhorada

### Por que Busca Manual?

O fuzzy matching automático não está funcionando bem porque:
- ❌ Descrições dos podcasts são genéricas ("quadro da independência")
- ❌ Nomes oficiais no acervo são diferentes ("Cédulas", IDs técnicos)
- ❌ Score de similaridade fica muito baixo (< 0.6)

**Solução:** Busca manual interativa + seleção assistida

---

## 🚀 Como Usar a Ferramenta de Busca

### 1. Executar a Ferramenta
```bash
cd day05
python day05_TOOL_manual_search.py
```

### 2. Comandos Disponíveis

| Comando | Exemplo | O que faz |
|---------|---------|-----------|
| Termo simples | `independência` | Busca em título E descrição |
| `autor:nome` | `autor:militão` | Busca por autor específico |
| `campo:valor` | `title:fotografia` | Busca em campo específico |
| `stats` | `stats` | Mostra estatísticas do acervo |
| `q` ou `quit` | `q` | Sair |

### 3. Exemplos Práticos

```bash
🔍 Buscar: independência
# Retorna todos os itens com "independência" no título ou descrição

🔍 Buscar: autor:militão
# Retorna TODAS as fotos do Militão (333+ esperadas)

🔍 Buscar: title:pintura
# Busca apenas no campo "title"

🔍 Buscar: stats
# Mostra Top 10 autores, datas, coleções
```

---

## 📊 Formatos de Armazenamento

O script de extração salva em **3 formatos:**

### 1. SQLite (.db) - Para queries SQL
```bash
# Tamanho: ~5-10 MB
# Uso: Queries complexas, joins
```

### 2. Parquet (.parquet) - Para análise rápida
```bash
# Tamanho: ~2-3 MB (comprimido)
# Uso: Pandas, análise de dados (MAIS RÁPIDO)
# 5-10x mais rápido que SQLite
```

### 3. CSV (.csv) - Para Excel/inspeção manual
```bash
# Tamanho: ~8-15 MB
# Uso: Abrir no Excel, Numbers, VS Code
```

---

## 🎯 Workflow Recomendado

### Opção A: Busca Interativa (Recomendado)

1. **Execute a ferramenta:**
   ```bash
   python day05_TOOL_manual_search.py
   ```

2. **Para cada item do podcast:**
   ```bash
   🔍 Buscar: dom pedro retrato
   # Veja resultados
   # Anote o ID do item correto
   ```

3. **Crie um CSV de mapeamento:**
   ```csv
   podcast_mention,tainacan_id,tainacan_title
   "quadro independência",12345,"Independência ou Morte"
   "foto militão",67890,"Retrato de Família - Militão"
   ```

### Opção B: Explorar CSV no Excel

1. **Abra o CSV:**
   ```bash
   open data/processed/museu_paulista_completo.csv
   ```

2. **Use filtros do Excel:**
   - Filtrar por `author_name` contém "Militão"
   - Filtrar por `title` contém "independência"
   - Ordenar por `creation_date`

3. **Copie IDs relevantes**

### Opção C: Pandas Script Customizado

```python
import pandas as pd

# Carregar
df = pd.read_parquet('data/processed/museu_paulista_completo.parquet')

# Buscar fotos do Militão
militao = df[df['author_name'].str.contains('militão', case=False, na=False)]
print(f"Fotos do Militão: {len(militao)}")

# Buscar por período
df_1800s = df[df['creation_date'].str.contains('18', na=False)]

# Exportar subset
militao.to_csv('militao_photos.csv', index=False)
```

---

## 📝 Estrutura do CSV Gerado

```csv
id,title,description,author_name,creation_date,collection_id,...
688027,"Cédulas","Anv/ Nota de 75...","","15 de outubro de 2025","117196",...
```

**Campos principais:**
- `id` - ID único do item
- `title` - Título oficial
- `description` - Descrição completa
- `author_name` - Nome do autor/fotógrafo
- `creation_date` - Data de criação
- `slug` - URL slug
- `thumbnail_url` - Link da miniatura

---

## 🔧 Troubleshooting

### Problema: "Nenhum arquivo encontrado"
**Solução:**
```bash
python day05_DATA_extract_complete_catalog.py
```

### Problema: "Muitos resultados"
**Solução:** Use termos mais específicos
```bash
# ❌ Genérico
🔍 Buscar: foto

# ✅ Específico
🔍 Buscar: autor:militão fotografia 1880
```

### Problema: "Não encontro o item esperado"
**Possíveis causas:**
1. Item não está digitalizado no acervo online
2. Nome no acervo é muito diferente do mencionado
3. Item está em coleção privada/não catalogada

**Solução:** Documente como "não encontrado" no CSV final

---

## 📤 Exportar Resultados da Busca Interativa

Dentro da ferramenta, depois de uma busca:

```python
# Adicione ao código:
tool.export_results(results, "minha_busca.csv")
```

Ou crie um script separado:

```python
from day05_TOOL_manual_search import day05_ManualSearchTool

tool = day05_ManualSearchTool()

# Buscar
results = tool.search_by_author("militão")

# Exportar
tool.export_results(results, "militao_complete.csv")
```

---

## ✅ Checklist de Validação

Após busca manual, verifique:

- [ ] **Total de itens extraídos:** >2000
- [ ] **Fotos do Militão encontradas:** >300
- [ ] **CSV de mapeamento criado:** podcast → tainacan
- [ ] **Matches validados manualmente:** ✓
- [ ] **Itens não encontrados documentados:** ✓

---

## 🎯 Entrega Final

Crie um CSV com este formato:

```csv
episode_id,podcast_mention,timestamp,tainacan_id,tainacan_title,match_method,confidence
01,"quadro independência",00:12:45,12345,"Independência ou Morte",manual,high
01,"foto militão",00:15:20,67890,"Retrato - Militão",manual,high
02,"escultura leão",00:08:10,,"",not_found,none
```

**Colunas:**
- `match_method`: "manual" (você escolheu) ou "fuzzy" (automático)
- `confidence`: "high" (certeza), "medium" (provável), "low" (chute)

---

**Este approach é MUITO mais preciso que fuzzy matching automático!** 🎯
