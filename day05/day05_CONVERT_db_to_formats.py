"""
Day 05: Convert SQLite to Parquet and CSV
Converts existing SQLite database to multiple formats

Usage:
    python day05_CONVERT_db_to_formats.py
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Import day05 configuration
from day05_CONFIG_settings import day05_PROCESSED_DIR


def day05_convert_database():
    """Convert SQLite database to Parquet and CSV"""

    print("=" * 80)
    print("Day 05: Database Format Converter")
    print("SQLite → Parquet + CSV")
    print("=" * 80)

    # Paths
    db_path = day05_PROCESSED_DIR / "museu_paulista_completo.db"
    parquet_path = day05_PROCESSED_DIR / "museu_paulista_completo.parquet"
    csv_path = day05_PROCESSED_DIR / "museu_paulista_completo.csv"

    # Check if database exists
    if not db_path.exists():
        print(f"\n❌ Database não encontrado: {db_path}")
        print("   Execute: python day05_DATA_extract_complete_catalog.py")
        return

    print(f"\n📂 Database encontrado: {db_path.name}")

    # Load from SQLite
    print(f"\n📥 Carregando dados do SQLite...")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM items", conn)
    conn.close()

    print(f"   ✅ Carregados: {len(df):,} itens")

    # Save as Parquet
    print(f"\n💾 Salvando em Parquet (comprimido)...")
    df.to_parquet(parquet_path, compression='gzip', index=False)

    # Get file size
    parquet_size = parquet_path.stat().st_size / (1024 * 1024)  # MB
    print(f"   ✅ Parquet salvo: {parquet_path.name}")
    print(f"   📦 Tamanho: {parquet_size:.2f} MB")

    # Save as CSV
    print(f"\n💾 Salvando em CSV (legível)...")
    df.to_csv(csv_path, index=False, encoding='utf-8')

    # Get file size
    csv_size = csv_path.stat().st_size / (1024 * 1024)  # MB
    print(f"   ✅ CSV salvo: {csv_path.name}")
    print(f"   📦 Tamanho: {csv_size:.2f} MB")

    # Summary
    print("\n" + "=" * 80)
    print("✅ CONVERSÃO COMPLETA!")
    print("=" * 80)
    print(f"\n📊 Arquivos gerados:")
    print(f"   1. SQLite:  {db_path.name} (já existia)")
    print(f"   2. Parquet: {parquet_path.name} ({parquet_size:.2f} MB) - MAIS RÁPIDO")
    print(f"   3. CSV:     {csv_path.name} ({csv_size:.2f} MB) - EXCEL")

    print(f"\n🔍 Próximo passo:")
    print(f"   python day05_TOOL_manual_search.py")
    print(f"   # OU")
    print(f"   open {csv_path}")

    # Show sample data
    print(f"\n📋 Amostra dos dados (primeiras 3 linhas):")
    print(df[['id', 'title', 'author_name']].head(3).to_string())


if __name__ == "__main__":
    day05_convert_database()
