# Investigação: API Tainacan Suporta Contexto Histórico?

**Data:** 2025-12-04
**Projeto:** Day 05 - Museu Ipiranga Cultural Data Pipeline

---

## 🔍 Pergunta

> "É possível saber se a API do Tainacan suporta esse tipo de contexto? Por exemplo, itens que estavam no acervo e não estão mais?"

---

## 📊 O que Investigamos

### 1. Estrutura da API Tainacan

**Campos disponíveis no catálogo do Museu Paulista:**

```
• id                   - ID único do item
• title                - Título do objeto
• description          - Descrição detalhada
• author_name          - Nome do autor/criador
• creation_date        - Data de criação do objeto
• modification_date    - Data de modificação no sistema
• collection_id        - ID da coleção
• slug                 - URL slug
• status               - Status de publicação
• thumbnail_url        - URL da imagem
• full_metadata        - JSON com metadados completos
```

### 2. Campo "status"

**Resultado:**
- ✅ Campo existe
- ❌ Só tem um valor: `publish` (79,392 itens)
- ❌ Não tem valores como `removed`, `repatriated`, `transferred`

**Implicação:** O campo `status` do Tainacan é usado para **publicação** (publish/draft/trash), **não para proveniência histórica**.

### 3. Campo "modification_date"

**Resultado:**
- ✅ Campo existe
- ❌ Não tem itens modificados desde 2020
- ❌ Não é usado para rastrear mudanças de localização/propriedade

**Implicação:** O campo registra mudanças no **sistema**, não mudanças **físicas/legais** do objeto.

### 4. Busca por Termos de Movimentação

Buscamos palavras-chave no título/descrição:

| Termo | Ocorrências | Tipo |
|-------|-------------|------|
| **repatri** | 1 item | ✅ Contexto válido |
| **devol** | 10 itens | ⚠️ "Terrenos devolutos" (não é movimentação) |
| **transferido** | 1 item | ⚠️ "Transferidor de papelão" (objeto, não ação) |
| **removido** | 1 item | ⚠️ Não verificado |
| **perdido** | 4 itens | ⚠️ Não verificado |

### 5. Caso Real: MEDALHAS CIVIS (ID: 240193)

**Descrição (parcial):**
> "PLAQUETA SOBRE CERCADURA, COM A INSCRIÇÃO 'HOMENAJE/ DEL/ PUEBLO ARGENTINO/ EN LA/ **REPATRIACION**/ DE SUS RESTOS/ 1906'"

**Análise:**
- ✅ Menciona "repatriação" na **descrição do objeto** (não no metadado estruturado)
- ✅ A repatriação é parte da **história do objeto** (restos de Juan Gregorio de las Heras em 1906)
- ❌ **NÃO** indica que este item foi repatriado do museu

**Conclusão:** Contexto histórico está no **conteúdo** do objeto, não na **proveniência** do objeto.

---

## 💡 Resposta à Pergunta

### ❌ **NÃO, a API padrão do Tainacan não suporta nativamente metadados de proveniência histórica.**

**O que ela TEM:**
- ✅ Status de publicação (`publish`, `draft`, `trash`)
- ✅ Data de modificação no sistema
- ✅ Descrição em texto livre (onde proveniência **pode** ser mencionada manualmente)
- ✅ `full_metadata` (JSON com campos customizados)

**O que ela NÃO TEM (por padrão):**
- ❌ Campo estruturado para status de proveniência
- ❌ Histórico de mudanças de localização
- ❌ Registro de transferências/repatriações
- ❌ Dados temporais de propriedade

---

## 🛠️ Como o Museu Paulista PODERIA Implementar

### Opção 1: Campos Customizados no Tainacan

O Tainacan permite criar **metadados customizados**. O museu poderia adicionar:

```json
{
  "provenance_status": {
    "current_location": "Museu Paulista",
    "status": "on_display",
    "previous_locations": [
      {
        "location": "Museu Nacional",
        "date_from": "1950-01-01",
        "date_to": "1990-05-15",
        "reason": "transferred"
      }
    ],
    "repatriation_info": null
  }
}
```

**Vantagens:**
- ✅ Estruturado
- ✅ Pesquisável
- ✅ Histórico completo

**Desvantagens:**
- ❌ Requer customização do Tainacan
- ❌ Precisa política institucional
- ❌ Trabalho manual de catalogação histórica

### Opção 2: Descrição em Texto Livre (Status Atual)

Adicionar proveniência na `description`:

```
Descrição: Medalha comemorativa...

Proveniência:
- 1890-1920: Coleção particular (Família Silva)
- 1920-2000: Museu Paulista
- 2000-presente: Museu Paulista (empréstimo ao Museu Nacional, 2010-2015)
```

**Vantagens:**
- ✅ Não requer mudança técnica
- ✅ Humano-legível

**Desvantagens:**
- ❌ Não estruturado
- ❌ Difícil de pesquisar/filtrar
- ❌ Sem validação

### Opção 3: Sistema Externo de Proveniência

Usar sistema especializado (ex: [CollectionSpace](https://www.collectionspace.org/)) para proveniência, integrado com Tainacan.

**Vantagens:**
- ✅ Sistema profissional
- ✅ Padrões internacionais (CIDOC-CRM)
- ✅ Auditoria completa

**Desvantagens:**
- ❌ Custo/complexidade
- ❌ Integração técnica necessária

---

## 🎯 Implicação para o Projeto Day 05

### Cenário Atual (Realista)

Para documentar a **Machadinha Krahô** ou outros itens removidos:

```csv
episode_id,item_mention,matched,match_type,notes
example,Machadinha Krahô,FALSE,not_in_api,Item foi repatriado ao povo Krahô em 2023 (fonte: notícia X)
```

**Onde registrar:**
1. ✅ Nossa tabela BigQuery tem campo `notes`
2. ✅ Podemos adicionar campo `provenance_notes`
3. ✅ Documentação no README

**Limitação:**
- ❌ Não podemos **buscar** itens repatriados na API Tainacan
- ❌ Não há campo estruturado para isso
- ❌ Dependemos de pesquisa manual/notícias

### Cenário Ideal (Feature Request)

**O que o Tainacan deveria ter:**

```sql
-- Schema proposto
CREATE TABLE item_provenance (
  item_id INT,
  event_type ENUM('acquisition', 'transfer', 'repatriation', 'loan', 'disposal'),
  event_date DATE,
  location_from VARCHAR(255),
  location_to VARCHAR(255),
  reason TEXT,
  documentation_url VARCHAR(500),
  created_by INT,
  created_at TIMESTAMP
);
```

**Benefícios:**
- ✅ Transparência histórica
- ✅ Apoio a esforços de decolonização
- ✅ Pesquisa acadêmica
- ✅ Accountability institucional

---

## 📚 Pesquisa Adicional Necessária

Para resposta definitiva, seria necessário:

1. ✅ **Documentação oficial Tainacan**
   - [ ] Verificar se há plugin de proveniência
   - [ ] Consultar community forums
   - [ ] Revisar roadmap do projeto

2. ✅ **Contato com Museu Paulista**
   - [ ] Perguntar se rastreiam proveniência internamente
   - [ ] Verificar se há sistema paralelo
   - [ ] Solicitar acesso a API privada (se existir)

3. ✅ **Padrões Internacionais**
   - CIDOC-CRM (Conceptual Reference Model)
   - LIDO (Lightweight Information Describing Objects)
   - Dublin Core Provenance Terms

---

## 🎓 Learnings para o Blog Post

### Finding #1: Ausência ≠ Dado Perdido

**O que descobrimos:**
- API não tem campo de proveniência estruturado
- Mas isso **não significa** que o museu não rastreie
- Pode existir em sistema interno não exposto via API

**Implicação:**
> "Ausência de um campo na API pública ≠ ausência de rastreamento institucional"

### Finding #2: Texto Livre vs. Estruturado

**Trade-off real:**
- Museus pequenos: Descrição em texto livre (viável)
- Museus grandes: Precisa estruturado (escalabilidade)

**Quote potencial:**
> "O Tainacan dá liberdade—você pode escrever 'repatriado' na descrição. Mas isso não resolve o problema de **pesquisar** todos os itens repatriados automaticamente."

### Finding #3: Gap Between Practice & Technology

**Realidade:**
- Museus **fazem** repatriações
- Museus **registram** em documentos internos
- Mas sistemas digitais **não refletem** esse histórico

**Oportunidade:**
> "Há um gap entre a prática museológica (repatriação, transferências) e os sistemas de catalogação digital. Este projeto expôs esse gap de forma prática."

---

## ✅ Conclusão

**Resposta curta:** ❌ Não, a API Tainacan padrão não suporta metadados de proveniência histórica estruturados.

**Resposta longa:**
- ✅ Tainacan **permite** campos customizados (`full_metadata`)
- ✅ Instituições **podem** implementar proveniência
- ❌ Museu Paulista **não implementou** (pelo que vimos na API pública)
- ⚠️  Informação **pode existir** em sistema interno

**Para o projeto Day 05:**
- Documentamos a limitação no README
- Criamos campo `notes` para contexto manual
- Caso da Machadinha Krahô vira exemplo de **dado que deveria existir mas não existe (digitalmente)**

**Para o blog post:**
- Ótimo exemplo de **gap entre prática e tecnologia**
- Reforça o argumento de que "NULL tem significado"
- Oportunidade de feature request para comunidade Tainacan

---

## 📖 Recursos

### Tainacan
- [Tainacan.org](https://tainacan.org/)
- [GitHub - tainacan/tainacan](https://github.com/tainacan/tainacan)
- [Documentação de Metadados](https://tainacan.org/docs/#/metadata)

### Provenance Standards
- [CIDOC-CRM](http://www.cidoc-crm.org/)
- [LIDO Schema](https://lido-schema.org/)
- [CollectionSpace](https://www.collectionspace.org/)

### Repatriation in Museums
- [ICOM Guidelines on Returns and Restitutions](https://icom.museum/)
- [Museum Association - Repatriation](https://www.museumsassociation.org/campaigns/repatriation/)

---

**Status:** Investigação completa ✅
**Próximo passo:** Adicionar este finding ao README/Blog Post
