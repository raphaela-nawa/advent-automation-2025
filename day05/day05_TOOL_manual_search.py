"""
Day 05: Manual Interactive Search Tool
Allows manual search and selection of museum items

Usage:
    python day05_TOOL_manual_search.py
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Import day05 configuration
from day05_CONFIG_settings import day05_PROCESSED_DIR


class day05_ManualSearchTool:
    """Interactive tool for manual item matching"""

    def __init__(self):
        """Initialize search tool"""
        self.db_path = day05_PROCESSED_DIR / "museu_paulista_completo.parquet"

        # Try parquet first, fall back to CSV
        if self.db_path.exists():
            print(f"📂 Carregando: {self.db_path.name}")
            self.df = pd.read_parquet(self.db_path)
        else:
            # Try CSV as fallback
            csv_path = day05_PROCESSED_DIR / "museu_paulista_completo.csv"
            if csv_path.exists():
                print(f"📂 Carregando: {csv_path.name}")
                self.df = pd.read_csv(csv_path)
            else:
                raise FileNotFoundError(
                    "❌ Nenhum arquivo de dados encontrado!\n"
                    "   Execute: python day05_DATA_extract_complete_catalog.py"
                )

        print(f"✅ Carregados: {len(self.df):,} itens\n")

    def search_simple(self, query: str, limit=10) -> pd.DataFrame:
        """
        Simple text search across title and description

        Args:
            query: Search term
            limit: Number of results

        Returns:
            DataFrame with matching items
        """
        query_lower = query.lower()

        # Search in title and description
        mask = (
            self.df['title'].str.lower().str.contains(query_lower, na=False) |
            self.df['description'].str.lower().str.contains(query_lower, na=False)
        )

        results = self.df[mask].head(limit)

        return results

    def search_by_author(self, author: str, limit=20) -> pd.DataFrame:
        """Search by author name"""
        author_lower = author.lower()

        mask = self.df['author_name'].str.lower().str.contains(author_lower, na=False)
        results = self.df[mask].head(limit)

        return results

    def search_by_field(self, field: str, value: str, limit=20) -> pd.DataFrame:
        """Generic search by any field"""
        if field not in self.df.columns:
            print(f"⚠️  Campo '{field}' não existe!")
            print(f"   Campos disponíveis: {', '.join(self.df.columns)}")
            return pd.DataFrame()

        value_lower = value.lower()
        mask = self.df[field].astype(str).str.lower().str.contains(value_lower, na=False)
        results = self.df[mask].head(limit)

        return results

    def display_results(self, results: pd.DataFrame):
        """Display search results in readable format"""
        if results.empty:
            print("❌ Nenhum resultado encontrado\n")
            return

        print(f"\n📋 Encontrados: {len(results)} resultados\n")
        print("=" * 100)

        for idx, row in results.iterrows():
            print(f"\n🆔 ID: {row.get('id', 'N/A')}")
            print(f"📌 Título: {row.get('title', 'N/A')}")

            author = row.get('author_name', '')
            if author:
                print(f"👤 Autor: {author}")

            date = row.get('creation_date', '')
            if date:
                print(f"📅 Data: {date}")

            desc = row.get('description', '')
            if desc:
                desc_preview = desc[:200] + "..." if len(desc) > 200 else desc
                print(f"📝 Descrição: {desc_preview}")

            print("-" * 100)

    def interactive_search(self):
        """Interactive search interface"""
        print("\n" + "=" * 100)
        print("🔍 Busca Interativa - Museu do Ipiranga")
        print("=" * 100)
        print("\nComandos disponíveis:")
        print("  - Digite um termo para buscar em título e descrição")
        print("  - 'autor:nome' para buscar por autor")
        print("  - 'campo:valor' para buscar em campo específico")
        print("  - 'stats' para ver estatísticas do acervo")
        print("  - 'q' ou 'quit' para sair")
        print("=" * 100)

        while True:
            query = input("\n🔍 Buscar: ").strip()

            if query.lower() in ['q', 'quit', 'exit', 'sair']:
                print("👋 Até logo!")
                break

            if query.lower() == 'stats':
                self.show_stats()
                continue

            if not query:
                continue

            # Parse command
            if ':' in query:
                field, value = query.split(':', 1)
                field = field.strip()
                value = value.strip()

                if field.lower() == 'autor' or field.lower() == 'author':
                    results = self.search_by_author(value)
                else:
                    results = self.search_by_field(field, value)
            else:
                results = self.search_simple(query)

            self.display_results(results)

    def show_stats(self):
        """Show dataset statistics"""
        print("\n" + "=" * 100)
        print("📊 Estatísticas do Acervo")
        print("=" * 100)
        print(f"Total de itens: {len(self.df):,}")

        # Top authors
        print("\n👥 Top 10 Autores:")
        top_authors = self.df['author_name'].value_counts().head(10)
        for author, count in top_authors.items():
            if pd.notna(author) and author:
                print(f"   {author}: {count} itens")

        # Date range
        print("\n📅 Datas:")
        dates = pd.to_datetime(self.df['creation_date'], errors='coerce')
        valid_dates = dates.dropna()
        if len(valid_dates) > 0:
            print(f"   Mais antigo: {valid_dates.min()}")
            print(f"   Mais recente: {valid_dates.max()}")

        # Collections
        print("\n📚 Coleções:")
        collections = self.df['collection_id'].value_counts().head(5)
        print(f"   Total de coleções: {collections.count()}")

        print("=" * 100)

    def export_results(self, results: pd.DataFrame, filename: str):
        """Export results to CSV"""
        output_path = day05_PROCESSED_DIR / filename
        results.to_csv(output_path, index=False, encoding='utf-8')
        print(f"✅ Resultados exportados: {output_path}")


def day05_main():
    """Main interactive search"""
    try:
        tool = day05_ManualSearchTool()
        tool.interactive_search()
    except FileNotFoundError as e:
        print(f"\n{str(e)}")
        print("\n🔧 Execute primeiro:")
        print("   python day05_DATA_extract_complete_catalog.py")
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")


if __name__ == "__main__":
    day05_main()
