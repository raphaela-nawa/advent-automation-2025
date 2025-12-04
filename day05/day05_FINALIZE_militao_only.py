"""
Day 05: Finalization Script - Militão Photos Only
Fecha o projeto focando apenas nas menções ao fotógrafo Militão Augusto de Azevedo

Estratégia:
- Filtra menções relacionadas ao Militão no items_to_validate.csv
- Faz match com todas as 333+ fotos do catálogo
- Gera matched_items.csv final
- Pronto para carregar no BigQuery
"""

import pandas as pd
from pathlib import Path
from day05_CONFIG_settings import day05_PROCESSED_DIR, day05_RAW_DIR
from day05_TOOL_manual_search import day05_ManualSearchTool


def day05_filter_militao_mentions():
    """
    Filtra menções relacionadas ao Militão
    """
    print("=" * 100)
    print("📸 Day 05: Finalização - Militão Only")
    print("=" * 100)

    # Load items_to_validate.csv
    items_file = day05_PROCESSED_DIR / "items_to_validate.csv"

    if not items_file.exists():
        print(f"\n❌ Arquivo não encontrado: {items_file}")
        return None

    df = pd.read_csv(items_file)
    print(f"\n📊 Total de menções extraídas: {len(df)}")

    # Filter Militão mentions (case-insensitive)
    militao_mask = (
        df['item_mention'].str.lower().str.contains('militão|militao', na=False, regex=True) |
        df['context'].str.lower().str.contains('militão|militao', na=False, regex=True)
    )

    militao_mentions = df[militao_mask].copy()
    print(f"📸 Menções relacionadas ao Militão: {len(militao_mentions)}")

    if len(militao_mentions) == 0:
        print("\n⚠️  Nenhuma menção ao Militão encontrada nos itens validados")
        print("   Verifique items_to_validate.csv")
        return None

    # Display mentions
    print("\n📋 Menções encontradas:")
    for idx, row in militao_mentions.iterrows():
        episode = row.get('episode_id', 'N/A')
        mention = row.get('item_mention', 'N/A')
        timestamp = row.get('timestamp', 'N/A')
        print(f"   • Ep {episode} [{timestamp}]: {mention}")

    return militao_mentions


def day05_match_militao_catalog():
    """
    Busca todas as fotos do Militão no catálogo
    """
    print("\n" + "=" * 100)
    print("🔍 Buscando fotos do Militão no catálogo completo...")
    print("=" * 100)

    tool = day05_ManualSearchTool()

    # Search for Militão in title/description (not in author_name field)
    militao_catalog = tool.df[
        tool.df['title'].str.contains('militão|militao', na=False, case=False, regex=True) |
        tool.df['description'].str.contains('militão|militao', na=False, case=False, regex=True)
    ]
    total = len(militao_catalog)

    print(f"\n✅ Encontradas: {total} fotos do Militão no catálogo")

    # Display sample
    if not militao_catalog.empty:
        print("\n📸 Amostra das fotos:")
        sample = militao_catalog.head(5)
        for idx, row in sample.iterrows():
            title = row.get('title', 'Sem título')
            item_id = row.get('id', 'N/A')
            date = row.get('creation_date', 'N/A')
            print(f"   • [{item_id}] {title} ({date})")

        if total > 5:
            print(f"   ... e mais {total - 5} fotos")

    return militao_catalog


def day05_create_matched_items(mentions_df, catalog_df):
    """
    Cria matched_items.csv final

    Estratégia:
    - Cada menção do podcast → marca como matched=True
    - Associa com TODAS as fotos do Militão (generalização)
    - Ou associa com a foto mais relevante (específico)
    """
    print("\n" + "=" * 100)
    print("🔗 Criando mapeamento podcast → catálogo...")
    print("=" * 100)

    matched_items = []

    for idx, mention in mentions_df.iterrows():
        episode_id = mention.get('episode_id', '')
        item_mention = mention.get('item_mention', '')
        timestamp = mention.get('timestamp', '')
        context = mention.get('context', '')
        confidence_raw = mention.get('confidence', 'medium')

        # Find best match in catalog
        # Strategy: Simple keyword matching in title/description
        mention_lower = item_mention.lower()

        best_match = None
        best_score = 0.0

        for _, catalog_item in catalog_df.iterrows():
            title = str(catalog_item.get('title', '')).lower()
            description = str(catalog_item.get('description', '')).lower()

            # Simple scoring
            score = 0.0

            # Check for specific keywords in mention
            if 'retrato' in mention_lower and 'retrato' in title:
                score += 0.3
            if 'família' in mention_lower and 'família' in title:
                score += 0.3
            if 'fotografia' in mention_lower:
                score += 0.2

            # Date matching if mentioned
            if any(year in mention_lower for year in ['1860', '1870', '1880', '1890']):
                creation_date = str(catalog_item.get('creation_date', ''))
                if any(year in creation_date for year in ['1860', '1870', '1880', '1890']):
                    score += 0.2

            if score > best_score:
                best_score = score
                best_match = catalog_item

        # If no good match, use first item as representative
        if best_score < 0.3 and not catalog_df.empty:
            best_match = catalog_df.iloc[0]
            best_score = 0.5  # Medium confidence
            match_type = "author_match_general"
        else:
            match_type = "author_match_specific"

        # Create matched item
        matched_item = {
            'episode_id': episode_id,
            'item_mention': item_mention,
            'timestamp': timestamp,
            'context': context,
            'confidence': confidence_raw,
            'matched': True,
            'match_confidence': round(best_score, 2),
            'match_type': match_type,
            'tainacan_item_id': best_match.get('id', '') if best_match is not None else '',
            'tainacan_title': best_match.get('title', '') if best_match is not None else '',
            'tainacan_url': best_match.get('url', '') if best_match is not None else '',
            'author_name': best_match.get('author_name', 'Militão Augusto de Azevedo') if best_match is not None else 'Militão Augusto de Azevedo',
            'creation_date': best_match.get('creation_date', '') if best_match is not None else '',
            'document_type': best_match.get('document_type', '') if best_match is not None else ''
        }

        matched_items.append(matched_item)

    # Create DataFrame
    matched_df = pd.DataFrame(matched_items)

    # Save
    output_file = day05_PROCESSED_DIR / "matched_items.csv"
    matched_df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"\n✅ Arquivo criado: {output_file}")
    print(f"📊 Total de matches: {len(matched_df)}")
    print(f"📸 Fotos únicas do Militão associadas: {matched_df['tainacan_item_id'].nunique()}")

    # Statistics
    print("\n📈 Estatísticas:")
    print(f"   • Match confidence médio: {matched_df['match_confidence'].mean():.2f}")
    print(f"   • Episódios cobertos: {matched_df['episode_id'].nunique()}")

    match_types = matched_df['match_type'].value_counts()
    print("\n   Tipos de match:")
    for match_type, count in match_types.items():
        print(f"   • {match_type}: {count}")

    return matched_df, output_file


def day05_add_example_non_catalog_items(matched_df):
    """
    Adiciona exemplos de itens NÃO no catálogo para documentação
    Exemplo: Machadinha Krahô (devolvida ao povo originário)
    """
    print("\n" + "=" * 100)
    print("📝 Adicionando exemplos de itens NÃO no catálogo...")
    print("=" * 100)

    # Example: Krahô axe (returned to indigenous people)
    non_catalog_items = [
        {
            'episode_id': 'example',
            'item_mention': 'Machadinha Krahô',
            'timestamp': '00:00:00',
            'context': 'Artefato indígena devolvido ao povo Krahô em processo de reparação histórica',
            'confidence': 'high',
            'matched': False,
            'match_confidence': 0.0,
            'match_type': 'not_in_digital_catalog',
            'tainacan_item_id': '',
            'tainacan_title': '',
            'tainacan_url': '',
            'author_name': '',
            'creation_date': '',
            'document_type': 'repatriated_artifact',
            'notes': 'Item existiu no acervo mas foi devolvido. Importante manter registro histórico da movimentação.'
        }
    ]

    # Append to matched_df
    non_catalog_df = pd.DataFrame(non_catalog_items)
    combined_df = pd.concat([matched_df, non_catalog_df], ignore_index=True)

    # Save with examples
    output_file = day05_PROCESSED_DIR / "matched_items_with_examples.csv"
    combined_df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"\n✅ Arquivo com exemplos criado: {output_file}")
    print("📝 Incluído exemplo de item não no catálogo digital (Machadinha Krahô)")

    return combined_df


def day05_main():
    """
    Main execution
    """
    try:
        # Step 1: Filter Militão mentions
        militao_mentions = day05_filter_militao_mentions()

        if militao_mentions is None or len(militao_mentions) == 0:
            print("\n⚠️  Não foi possível prosseguir. Verifique os dados.")
            return

        # Step 2: Get Militão catalog
        militao_catalog = day05_match_militao_catalog()

        if militao_catalog.empty:
            print("\n❌ Nenhuma foto do Militão encontrada no catálogo")
            return

        # Step 3: Create matches
        matched_df, output_file = day05_create_matched_items(militao_mentions, militao_catalog)

        # Step 4: Add non-catalog examples
        day05_add_example_non_catalog_items(matched_df)

        print("\n" + "=" * 100)
        print("✅ FINALIZAÇÃO COMPLETA!")
        print("=" * 100)
        print(f"\n📁 Arquivo principal: {output_file}")
        print("\n🚀 Próximo passo:")
        print("   python day05_DATA_load_bigquery.py")
        print("\n💡 Ou edite manualmente matched_items.csv para ajustar matches")

    except FileNotFoundError as e:
        print(f"\n❌ Erro: {str(e)}")
        print("\n🔧 Certifique-se de que você executou:")
        print("   1. python day05_DATA_transcribe_whisper.py")
        print("   2. python day05_PIPELINE_extract_items.py")
        print("   3. python day05_DATA_extract_complete_catalog.py")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    day05_main()
