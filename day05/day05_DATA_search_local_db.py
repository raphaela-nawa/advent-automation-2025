"""
Day 05: Local Database Search Script
Searches local SQLite database for museum items with fuzzy text matching

Usage:
    python day05_DATA_search_local_db.py
"""

import sqlite3
import csv
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys

# Import day05 configuration
from day05_CONFIG_settings import (
    day05_PROCESSED_DIR,
    day05_SIMILARITY_THRESHOLD,
    day05_ensure_directories
)


class day05_LocalDatabaseSearcher:
    """Searches local SQLite database for museum artifacts with similarity matching"""

    def __init__(self):
        """Initialize local database searcher"""
        self.db_path = day05_PROCESSED_DIR / "museu_paulista_completo.db"

        if not self.db_path.exists():
            raise FileNotFoundError(
                f"❌ Database not found: {self.db_path}\n"
                f"   Run: python day05_DATA_extract_complete_catalog.py first!"
            )

        print(f"✅ Local database searcher initialized")
        print(f"   DB: {self.db_path}")

    def day05_load_all_items(self) -> pd.DataFrame:
        """
        Load all items from local database

        Returns:
            DataFrame with all museum items
        """
        print(f"\n📥 Carregando itens do database local...")

        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM items", conn)
        conn.close()

        print(f"   ✅ Carregados: {len(df):,} itens")

        return df

    def day05_search_item(self, query: str, df: pd.DataFrame) -> dict:
        """
        Search for a specific item using fuzzy text matching

        Args:
            query: Search query (item mention from podcast)
            df: DataFrame with all museum items

        Returns:
            Best matching item with confidence score
        """
        print(f"\n🔍 Buscando: '{query}'")

        if df.empty:
            return self.day05_create_no_match_result(query)

        # Prepare texts for matching (title + description)
        candidate_texts = []
        for _, row in df.iterrows():
            title = str(row.get('title', ''))
            description = str(row.get('description', ''))
            combined = f"{title} {description}".lower()
            candidate_texts.append(combined[:1000])  # Limit length

        # Add query to corpus
        all_texts = [query.lower()] + candidate_texts

        # Calculate TF-IDF similarity
        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=5000)
            tfidf_matrix = vectorizer.fit_transform(all_texts)

            # Calculate similarity with query (first item)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

            # Find best match
            best_idx = similarities.argmax()
            best_score = similarities[best_idx]

            if best_score >= day05_SIMILARITY_THRESHOLD:
                best_item = df.iloc[best_idx]
                print(f"   ✅ Match encontrado (confidence: {best_score:.3f})")

                return self.day05_format_match_result(best_item, best_score, "fuzzy_match_local")
            else:
                print(f"   ⚠️  Melhor match abaixo do threshold: {best_score:.3f} < {day05_SIMILARITY_THRESHOLD}")
                return self.day05_create_no_match_result(query)

        except Exception as e:
            print(f"   ❌ Erro no fuzzy matching: {str(e)}")
            return self.day05_create_no_match_result(query)

    @staticmethod
    def day05_format_match_result(row: pd.Series, confidence: float, match_type: str) -> dict:
        """Format a successful match result"""
        return {
            "matched": True,
            "match_confidence": round(confidence, 3),
            "match_type": match_type,
            "tainacan_item_id": str(row.get('id', '')),
            "tainacan_title": str(row.get('title', '')).strip(),
            "tainacan_description": str(row.get('description', ''))[:500].strip(),
            "tainacan_author": str(row.get('author_name', '')).strip(),
            "tainacan_date": str(row.get('creation_date', '')).strip(),
            "tainacan_url": f"https://acervoonline.mp.usp.br/item/{row.get('slug', '')}",
            "tainacan_thumbnail": str(row.get('thumbnail_url', '')).strip()
        }

    @staticmethod
    def day05_create_no_match_result(query: str) -> dict:
        """Create a no-match result"""
        return {
            "matched": False,
            "match_confidence": 0.0,
            "match_type": "no_match",
            "tainacan_item_id": "",
            "tainacan_title": "",
            "tainacan_description": "",
            "tainacan_author": "",
            "tainacan_date": "",
            "tainacan_url": "",
            "tainacan_thumbnail": ""
        }


def day05_load_validated_items() -> list:
    """Load validated items from CSV"""
    csv_path = day05_PROCESSED_DIR / "items_to_validate.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"❌ Validated items CSV not found: {csv_path}")

    items = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only include items marked as validated='yes'
            if row.get('validated', '').lower() in ['yes', 'y', '1', 'true', 'sim']:
                items.append(row)

    return items


def day05_save_matched_items(matched_items: list, output_path: Path):
    """Save matched items to CSV"""
    if not matched_items:
        print("⚠️  No items to save")
        return

    fieldnames = [
        "episode_id", "item_mention", "timestamp", "context", "confidence",
        "matched", "match_confidence", "match_type",
        "tainacan_item_id", "tainacan_title", "tainacan_description",
        "tainacan_author", "tainacan_date", "tainacan_url", "tainacan_thumbnail"
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matched_items)

    print(f"\n💾 Saved {len(matched_items)} matched items to: {output_path.name}")


def day05_main():
    """Main local database search pipeline"""
    print("=" * 80)
    print("Day 05: Local Database Search Pipeline")
    print("Fuzzy Matching with Complete Museu Ipiranga Catalog")
    print("=" * 80)

    # Ensure directories
    day05_ensure_directories()

    # Load validated items
    print("\n📂 Carregando itens validados...")
    try:
        validated_items = day05_load_validated_items()
        print(f"   ✅ Carregados: {len(validated_items)} itens validados")
    except FileNotFoundError as e:
        print(f"\n{str(e)}")
        print("\n⚠️  Certifique-se de:")
        print("   1. Rodar day05_PIPELINE_extract_items.py")
        print("   2. Validar manualmente items_to_validate.csv")
        print("   3. Marcar 'validated' como 'yes' para itens a buscar")
        sys.exit(1)

    if not validated_items:
        print("\n⚠️  Nenhum item validado encontrado!")
        print("   Abra day05/data/processed/items_to_validate.csv")
        print("   Marque itens como 'validated=yes' para buscá-los")
        sys.exit(0)

    # Initialize searcher
    try:
        searcher = day05_LocalDatabaseSearcher()
    except FileNotFoundError as e:
        print(f"\n{str(e)}")
        print("\n⚠️  Execute primeiro:")
        print("   python day05_DATA_extract_complete_catalog.py")
        sys.exit(1)

    # Load all museum items from database
    df_items = searcher.day05_load_all_items()

    # Search for each validated item
    matched_items = []

    for i, item in enumerate(validated_items, 1):
        print(f"\n{'='*80}")
        print(f"Processando {i}/{len(validated_items)}")

        query = item['item_mention']
        match_result = searcher.day05_search_item(query, df_items)

        # Combine original item data with match result
        combined = {**item, **match_result}
        matched_items.append(combined)

    # Save results
    output_path = day05_PROCESSED_DIR / "matched_items.csv"
    day05_save_matched_items(matched_items, output_path)

    # Summary
    print("\n" + "=" * 80)
    print("📊 Resumo da Busca")
    print("=" * 80)

    total = len(matched_items)
    matched = sum(1 for m in matched_items if m['matched'])
    not_matched = total - matched

    print(f"Total de itens buscados: {total}")
    print(f"   ✅ Matched: {matched}")
    print(f"   ❌ Not matched: {not_matched}")

    if matched > 0:
        avg_confidence = sum(m['match_confidence'] for m in matched_items if m['matched']) / matched
        print(f"   📊 Confiança média: {avg_confidence:.3f}")

    print("\n✅ Busca completa!")
    print(f"📂 Resultados: {output_path}")
    print("\n🔜 Próximo passo: python day05_DATA_load_bigquery.py")


if __name__ == "__main__":
    day05_main()
