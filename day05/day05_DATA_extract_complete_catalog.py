"""
Day 05: Complete Tainacan Catalog Extraction
Extracts ALL items from Museu Ipiranga using pagination

Usage:
    python day05_DATA_extract_complete_catalog.py
"""

import requests
import sqlite3
import json
import math
import time
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import sys

# Import day05 configuration
from day05_CONFIG_settings import (
    day05_TAINACAN_API_URL,
    day05_PROCESSED_DIR,
    day05_ensure_directories
)


class day05_CompleteCatalogExtractor:
    """Extracts complete museum catalog with pagination"""

    def __init__(self):
        """Initialize extractor"""
        self.base_url = day05_TAINACAN_API_URL.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Day05-Museum-Complete-Extraction/1.0',
            'Accept': 'application/json'
        })
        self.db_path = day05_PROCESSED_DIR / "museu_paulista_completo.db"
        print(f"✅ Extractor initialized")
        print(f"   API: {self.base_url}")
        print(f"   DB: {self.db_path}")

    def day05_get_total_items(self) -> int:
        """
        Discover total number of items in the collection

        Returns:
            Total count of items
        """
        print(f"\n📊 Descobrindo total de itens no acervo...")

        try:
            url = f"{self.base_url}/items"
            params = {'perpage': 1}

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            # Try to get total from headers (WordPress/Tainacan standard)
            total = response.headers.get('X-WP-Total')

            if total:
                total = int(total)
                print(f"   ✅ Total de itens (via header): {total:,}")
                return total

            # Fallback: check JSON response
            data = response.json()

            # Try different possible fields
            total = (data.get('total') or
                    data.get('found_items') or
                    data.get('total_items') or
                    len(data.get('items', [])))

            if isinstance(data, list):
                # If it returns a list directly, we need to paginate
                print(f"   ⚠️  API retorna lista - estimando via paginação...")
                return self.day05_estimate_total()

            print(f"   ✅ Total de itens (via JSON): {total:,}")
            return int(total)

        except Exception as e:
            print(f"   ⚠️  Erro ao obter total: {e}")
            print(f"   🔄 Usando estimativa via paginação...")
            return self.day05_estimate_total()

    def day05_estimate_total(self, max_pages=100) -> int:
        """Estimate total by checking when pages return empty"""
        print(f"   🔍 Estimando total via busca binária...")

        left, right = 1, max_pages
        last_valid_page = 1

        while left <= right:
            mid = (left + right) // 2

            try:
                response = self.session.get(
                    f"{self.base_url}/items",
                    params={'perpage': 100, 'paged': mid},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    items = data if isinstance(data, list) else data.get('items', [])

                    if items:
                        last_valid_page = mid
                        left = mid + 1
                    else:
                        right = mid - 1
                else:
                    right = mid - 1

            except:
                right = mid - 1

        estimated_total = last_valid_page * 100
        print(f"   📊 Total estimado: ~{estimated_total:,} itens")
        return estimated_total

    def day05_extract_all_items(self, perpage=100) -> list:
        """
        Extract ALL items from catalog using pagination

        Args:
            perpage: Items per page

        Returns:
            List of all items
        """
        print(f"\n📥 Extraindo TODOS os itens do acervo...")

        total_items = self.day05_get_total_items()
        total_pages = math.ceil(total_items / perpage)

        print(f"\n🔄 Iniciando extração:")
        print(f"   Total estimado: {total_items:,} itens")
        print(f"   Páginas a buscar: {total_pages}")
        print(f"   Itens por página: {perpage}")

        all_items = []
        failed_pages = []

        for page in tqdm(range(1, total_pages + 1), desc="📄 Extraindo páginas"):
            try:
                url = f"{self.base_url}/items"
                params = {'perpage': perpage, 'paged': page}

                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                # Handle both list and dict responses
                if isinstance(data, dict):
                    items = data.get('items', [])
                else:
                    items = data

                if not items:
                    # No more items, we can stop
                    break

                all_items.extend(items)

                # Respect server - rate limiting
                time.sleep(0.5)

            except Exception as e:
                failed_pages.append(page)
                tqdm.write(f"   ⚠️  Erro na página {page}: {str(e)[:50]}")
                time.sleep(2)  # Wait longer on error
                continue

        print(f"\n✅ Extração completa!")
        print(f"   Total extraído: {len(all_items):,} itens")
        if failed_pages:
            print(f"   ⚠️  Páginas com erro: {len(failed_pages)}")

        return all_items

    def day05_create_database(self):
        """Create SQLite database with schema"""
        print(f"\n💾 Criando database SQLite...")

        conn = sqlite3.connect(self.db_path)

        conn.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                author_name TEXT,
                creation_date TEXT,
                modification_date TEXT,
                collection_id TEXT,
                slug TEXT,
                status TEXT,
                thumbnail_url TEXT,
                full_metadata TEXT
            )
        ''')

        conn.commit()
        conn.close()

        print(f"   ✅ Database criado: {self.db_path.name}")

    def day05_save_to_database(self, items: list):
        """
        Save all items to SQLite database

        Args:
            items: List of item dictionaries
        """
        print(f"\n💾 Salvando itens no database...")

        self.day05_create_database()

        conn = sqlite3.connect(self.db_path)

        saved_count = 0
        for item in tqdm(items, desc="💿 Salvando"):
            try:
                # Extract metadata safely
                item_id = item.get('id')
                title = item.get('title', '')
                description = item.get('description', '')

                # Handle author (can be in different formats)
                author_name = item.get('author_name', '')
                if not author_name:
                    author_name = item.get('author', {}).get('name', '') if isinstance(item.get('author'), dict) else ''

                # Extract other fields
                creation_date = item.get('creation_date', '')
                modification_date = item.get('modification_date', '')
                collection_id = str(item.get('collection_id', ''))
                slug = item.get('slug', '')
                status = item.get('status', '')

                # Try to get thumbnail
                thumbnail_url = ''
                if 'thumbnail' in item:
                    thumb = item['thumbnail']
                    if isinstance(thumb, dict):
                        thumbnail_url = thumb.get('url', thumb.get('src', ''))
                    elif isinstance(thumb, str):
                        thumbnail_url = thumb

                # Save full metadata as JSON
                full_metadata = json.dumps(item, ensure_ascii=False)

                conn.execute('''
                    INSERT OR REPLACE INTO items
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_id,
                    title,
                    description,
                    author_name,
                    creation_date,
                    modification_date,
                    collection_id,
                    slug,
                    status,
                    thumbnail_url,
                    full_metadata
                ))

                saved_count += 1

            except Exception as e:
                tqdm.write(f"   ⚠️  Erro salvando item {item.get('id')}: {e}")
                continue

        conn.commit()
        conn.close()

        print(f"   ✅ Salvos: {saved_count:,} itens")

    def day05_validate_extraction(self, items_count: int):
        """
        Validate that extraction is complete

        Args:
            items_count: Number of items extracted
        """
        print(f"\n🔍 Validando extração...")

        # Check database
        conn = sqlite3.connect(self.db_path)
        local_count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        conn.close()

        # Get API total
        api_total = self.day05_get_total_items()

        completeness = (local_count / api_total * 100) if api_total > 0 else 0

        print(f"\n📊 Relatório de Validação:")
        print(f"   API reporta: {api_total:,} itens")
        print(f"   Extraídos: {items_count:,} itens")
        print(f"   DB local: {local_count:,} itens")
        print(f"   Completude: {completeness:.1f}%")

        if completeness >= 95:
            print(f"   ✅ Extração COMPLETA!")
        elif completeness >= 80:
            print(f"   ⚠️  Extração PARCIAL (>80%)")
        else:
            print(f"   ❌ Extração INCOMPLETA (<80%)")

        return completeness >= 80

    def day05_generate_stats(self, items: list) -> dict:
        """Generate extraction statistics"""
        print(f"\n📊 Gerando estatísticas...")

        stats = {
            "extraction_date": datetime.now().isoformat(),
            "total_items": len(items),
            "database_path": str(self.db_path),
            "api_url": self.base_url
        }

        # Save stats
        stats_path = day05_PROCESSED_DIR / "extraction_stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f"   ✅ Estatísticas salvas: {stats_path.name}")

        return stats


def day05_main():
    """Main extraction pipeline"""
    print("=" * 80)
    print("Day 05: Complete Tainacan Catalog Extraction")
    print("Museu Ipiranga - Full Collection Download")
    print("=" * 80)

    # Ensure directories
    day05_ensure_directories()

    # Initialize extractor
    extractor = day05_CompleteCatalogExtractor()

    # Extract ALL items
    all_items = extractor.day05_extract_all_items(perpage=100)

    if not all_items:
        print("\n❌ Nenhum item extraído!")
        sys.exit(1)

    # Save to database
    extractor.day05_save_to_database(all_items)

    # ALSO save to Parquet and CSV for easier access
    print(f"\n💾 Salvando em formatos adicionais...")
    import pandas as pd

    # Convert to DataFrame
    df_items = pd.DataFrame(all_items)

    # Save as Parquet (compressed, fast)
    parquet_path = day05_PROCESSED_DIR / "museu_paulista_completo.parquet"
    df_items.to_parquet(parquet_path, compression='gzip')
    print(f"   ✅ Parquet: {parquet_path.name}")

    # Save as CSV (human-readable)
    csv_path = day05_PROCESSED_DIR / "museu_paulista_completo.csv"
    df_items.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"   ✅ CSV: {csv_path.name}")

    # Validate
    is_complete = extractor.day05_validate_extraction(len(all_items))

    # Generate stats
    stats = extractor.day05_generate_stats(all_items)

    # Summary
    print("\n" + "=" * 80)
    print("✅ EXTRAÇÃO COMPLETA!")
    print("=" * 80)
    print(f"📊 Total de itens: {len(all_items):,}")
    print(f"💾 Database: {extractor.db_path}")
    print(f"📈 Completude: {'✅ VALIDADA' if is_complete else '⚠️  PARCIAL'}")
    print("\n🔜 Próximo passo:")
    print(f"   python day05_DATA_search_tainacan.py")


if __name__ == "__main__":
    day05_main()
