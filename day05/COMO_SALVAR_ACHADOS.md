# 💾 Como Salvar Achados do Manual Search

## 📋 3 Formas de Salvar Resultados

---

## Opção 1: Script Helper (MAIS FÁCIL) ⭐

```bash
cd day05
python day05_HELPER_save_findings.py
```

**Menu interativo:**
1. **Busca interativa e salvar** - Busca + salvar em um fluxo
2. **Criar template de mapeamento** - Gera CSV para preencher
3. **Exportação rápida** - Exporta buscas comuns (Militão, independência, etc.)

### Exemplo de Uso:

```bash
$ python day05_HELPER_save_findings.py

🎯 Escolha uma opção:
1. Busca interativa e salvar resultados
2. Criar template de mapeamento (podcast → tainacan)
3. Exportação rápida (exemplos comuns)

Opção: 1

🔍 Buscar: autor:militão

📋 Encontrados: 333 resultados

💾 Salvar estes resultados? (s/n): s

📄 Nome do arquivo [search_1_author_militão_20241129_153045.csv]: militao_fotos.csv

✅ Salvo em: data/processed/militao_fotos.csv
```

---

## Opção 2: Durante Manual Search Interativo

Se você já está usando o `day05_TOOL_manual_search.py`, pode exportar resultados programaticamente.

### Passo a Passo:

1. **Rode o manual search:**
```bash
python day05_TOOL_manual_search.py
```

2. **Faça sua busca normalmente:**
```
🔍 Buscar: independência
```

3. **Em outro terminal, rode um script Python:**

```python
# salvar_busca.py
from day05_TOOL_manual_search import day05_ManualSearchTool

tool = day05_ManualSearchTool()

# Buscar
results, total = tool.search_simple("independência")

# Salvar
tool.export_results(results, "independencia_obras.csv")
```

```bash
python salvar_busca.py
```

---

## Opção 3: Criar Mapeamento Podcast → Tainacan (RECOMENDADO PARA PROJETO)

Esta é a forma correta para o projeto final.

### Passo 1: Criar Template

```bash
python day05_HELPER_save_findings.py
# Escolha opção 2
```

Isso cria `mapping_template.csv`:

```csv
episode_id,podcast_mention,timestamp,context,tainacan_id,tainacan_title,match_confidence,notes
01,quadro independência,00:12:45,"...",,,
01,foto militão,00:15:20,"...",,,
02,escultura leão,00:08:10,"...",,,
```

### Passo 2: Buscar Cada Item

Para cada linha do template:

```bash
python day05_TOOL_manual_search.py

🔍 Buscar: independência
# Veja os resultados
# Anote o ID do item correto

🔍 Buscar: autor:militão
# Veja os resultados
# Anote o ID do item correto
```

### Passo 3: Preencher Template

Abra `mapping_template.csv` no Excel/Numbers/VS Code e preencha:

```csv
episode_id,podcast_mention,timestamp,context,tainacan_id,tainacan_title,match_confidence,notes
01,quadro independência,00:12:45,"...",688123,Independência ou Morte,high,Obra principal
01,foto militão,00:15:20,"...",688456,Retrato de Família - Militão,high,
02,escultura leão,00:08:10,"...",,not_found,none,Não encontrado no acervo
```

### Passo 4: Salvar como `matched_items.csv`

```bash
cp mapping_template.csv matched_items.csv
```

---

## 📊 Exportações Rápidas Úteis

### Exportar todas as fotos do Militão (333+)
```python
from day05_TOOL_manual_search import day05_ManualSearchTool

tool = day05_ManualSearchTool()
militao, total = tool.search_by_author("militão")
tool.export_results(militao, "militao_completo.csv")
```

### Exportar obras sobre independência
```python
tool = day05_ManualSearchTool()
indep, total = tool.search_simple("independência")
tool.export_results(indep, "independencia_obras.csv")
```

### Exportar por período (século 19)
```python
tool = day05_ManualSearchTool()
sec19, total = tool.search_all_fields("século 19")
tool.export_results(sec19, "seculo_19.csv")
```

### Exportar por campo específico
```python
tool = day05_ManualSearchTool()
paintings, total = tool.search_by_field("title", "pintura")
tool.export_results(paintings, "pinturas.csv")
```

---

## 🎯 Workflow Recomendado para o Projeto

### Cenário: Mapear menções do podcast para o acervo

1. **Criar template:**
   ```bash
   python day05_HELPER_save_findings.py
   # Opção 2
   ```

2. **Para cada menção, buscar e salvar:**
   ```bash
   python day05_HELPER_save_findings.py
   # Opção 1

   # Buscar cada termo mencionado no podcast
   🔍 Buscar: quadro independência
   💾 Salvar? s
   📄 Nome: independencia_search.csv

   🔍 Buscar: autor:militão
   💾 Salvar? s
   📄 Nome: militao_search.csv
   ```

3. **Revisar CSVs exportados e escolher IDs corretos**

4. **Preencher `matched_items.csv` com os IDs encontrados**

5. **Carregar no BigQuery:**
   ```bash
   python day05_DATA_load_bigquery.py
   ```

---

## 📁 Arquivos Gerados

Todos os arquivos são salvos em:
```
day05/data/processed/
```

**Exemplos:**
- `militao_completo.csv` - Todas as 333+ fotos do Militão
- `independencia_obras.csv` - Obras sobre independência
- `mapping_template.csv` - Template para preencher
- `matched_items.csv` - Mapeamento final (podcast → tainacan)

---

## 💡 Dicas

### Busca Mais Precisa
```bash
# ❌ Muito genérico
🔍 Buscar: foto

# ✅ Mais específico
🔍 Buscar: autor:militão fotografia 1880
```

### Verificar Campos Disponíveis
```bash
python day05_TOOL_manual_search.py

🔍 Buscar: stats
# Mostra top autores, datas, coleções
```

### Buscar em Todos os Campos
```bash
🔍 Buscar: all:dom pedro
# Busca em TODOS os campos de texto
```

### Limitar Resultados
```bash
🔍 Buscar: autor:militão limit=50
# Retorna apenas 50 resultados
```

---

## ✅ Checklist de Validação

Após salvar seus achados, verifique:

- [ ] CSV tem cabeçalho correto
- [ ] IDs do Tainacan estão preenchidos
- [ ] Títulos oficiais estão corretos
- [ ] Match confidence está marcado (high/medium/low)
- [ ] Itens não encontrados marcados como "not_found"
- [ ] Arquivo salvo em `data/processed/`

---

## 🚀 Próximo Passo

Após ter `matched_items.csv` completo:

```bash
python day05_DATA_load_bigquery.py
```

Isso carrega os dados para BigQuery e finaliza o projeto! 🎉
