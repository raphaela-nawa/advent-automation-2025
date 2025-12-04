"""
Day 05: Prepare Data for BigQuery
Valida e prepara os dados para carregar no BigQuery (sem fazer o upload)

Uso:
    python day05_PREPARE_for_bigquery.py
"""

import pandas as pd
from pathlib import Path
from day05_CONFIG_settings import day05_PROCESSED_DIR


def day05_prepare_bigquery_data():
    """
    Prepara dados finais para BigQuery
    """
    print("=" * 100)
    print("📦 Day 05: Preparação dos Dados para BigQuery")
    print("=" * 100)

    # Load matched_items.csv
    matched_file = day05_PROCESSED_DIR / "matched_items.csv"

    if not matched_file.exists():
        print(f"\n❌ Arquivo não encontrado: {matched_file}")
        print("   Execute primeiro: python day05_FINALIZE_militao_only.py")
        return

    df = pd.read_csv(matched_file)
    print(f"\n📊 Dados carregados: {len(df)} registros")

    # Validate columns
    required_cols = [
        'episode_id',
        'item_mention',
        'timestamp',
        'matched',
        'match_confidence',
        'tainacan_item_id',
        'tainacan_title'
    ]

    print("\n✅ Validando estrutura...")
    for col in required_cols:
        if col in df.columns:
            print(f"   ✓ {col}")
        else:
            print(f"   ✗ {col} (FALTANDO)")

    # Show statistics
    print("\n" + "=" * 100)
    print("📈 Estatísticas dos Dados")
    print("=" * 100)

    print(f"\n📸 Total de menções: {len(df)}")
    print(f"✅ Matches encontrados: {df['matched'].sum()}")
    print(f"❌ Não encontrados: {(~df['matched']).sum()}")

    if 'match_confidence' in df.columns:
        matched_only = df[df['matched'] == True]
        if len(matched_only) > 0:
            print(f"📊 Confidence médio: {matched_only['match_confidence'].mean():.2f}")
            print(f"📊 Confidence min: {matched_only['match_confidence'].min():.2f}")
            print(f"📊 Confidence max: {matched_only['match_confidence'].max():.2f}")

    # Episodes
    if 'episode_id' in df.columns:
        episodes = df['episode_id'].unique()
        print(f"\n🎙️ Episódios cobertos: {len(episodes)}")
        for ep in sorted(episodes):
            count = len(df[df['episode_id'] == ep])
            print(f"   • Episódio {ep}: {count} menções")

    # Sample data
    print("\n" + "=" * 100)
    print("📋 Amostra dos Dados (primeiras 3 linhas)")
    print("=" * 100)

    for idx, row in df.head(3).iterrows():
        print(f"\n{idx + 1}. Episódio {row.get('episode_id', 'N/A')} [{row.get('timestamp', 'N/A')}]")
        print(f"   Menção: {row.get('item_mention', 'N/A')}")
        print(f"   Match: {row.get('matched', False)}")
        if row.get('matched', False):
            print(f"   Tainacan ID: {row.get('tainacan_item_id', 'N/A')}")
            print(f"   Título: {row.get('tainacan_title', 'N/A')[:80]}...")
            print(f"   Confidence: {row.get('match_confidence', 0):.2f}")

    # Export for BigQuery
    output_file = day05_PROCESSED_DIR / "bigquery_ready.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')

    print("\n" + "=" * 100)
    print("✅ DADOS PRONTOS PARA BIGQUERY!")
    print("=" * 100)
    print(f"\n📁 Arquivo: {output_file}")
    print(f"📊 Registros: {len(df)}")
    print(f"💾 Tamanho: {output_file.stat().st_size / 1024:.2f} KB")

    print("\n🚀 Próximos passos:")
    print("\n1. Autenticar no GCP:")
    print("   gcloud auth application-default login")
    print("   gcloud config set project advent2025-day05")

    print("\n2. Carregar no BigQuery:")
    print("   python day05_DATA_load_bigquery.py")

    print("\n   OU manualmente via CLI:")
    print("   bq load --source_format=CSV --autodetect \\")
    print("       cultural_data.podcast_museum_mentions \\")
    print(f"       {output_file}")

    print("\n3. Query de teste:")
    print("   bq query --use_legacy_sql=false \\")
    print("       'SELECT episode_id, COUNT(*) as mentions \\")
    print("        FROM `advent2025-day05.cultural_data.podcast_museum_mentions` \\")
    print("        GROUP BY episode_id'")

    return df, output_file


if __name__ == "__main__":
    day05_prepare_bigquery_data()
