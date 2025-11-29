"""
Day 05: Tainacan API Search Script
Searches Museu Ipiranga API for museum items with fuzzy text matching

Usage:
    python day05_DATA_search_tainacan.py
"""

import requests
import csv
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import time

# Import day05 configuration
from day05_CONFIG_settings import (
    day05_TAINACAN_API_URL,
    day05_PROCESSED_DIR,
    day05_SIMILARITY_THRESHOLD,
    day05_MAX_SEARCH_RESULTS,
    day05_ensure_directories
)


class day05_TainacanSearcher:
    """Searches Tainacan API for museum artifacts with similarity matching"""

    def __init__(self):
        """Initialize Tainacan API client"""
        self.api_url = day05_TAINACAN_API_URL.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Day05-Museum-Pipeline/1.0',
            'Accept': 'application/json'
        })
        print(f"✅ Tainacan API client initialized")
        print(f"   API URL: {self.api_url}")

    def day05_get_all_items(self, max_items=1000) -> list:
        """
        Fetch all available items from Tainacan API

        Args:
            max_items: Maximum number of items to fetch

        Returns:
            List of all museum items
        """
        print(f"\n📥 Fetching museum items from Tainacan API...")

        all_items = []
        page = 1
        per_page = 100

        while len(all_items) < max_items:
            try:
                url = f"{self.api_url}/items"
                params = {
                    'perpage': per_page,
                    'paged': page
                }

                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                items = response.json()

                if not items:
                    break

                all_items.extend(items)
                print(f"   Page {page}: +{len(items)} items (total: {len(all_items)})")

                page += 1
                time.sleep(0.5)  # Rate limiting

            except requests.exceptions.RequestException as e:
                print(f"   ⚠️  Error fetching page {page}: {str(e)}")
                break

        print(f"   ✅ Fetched {len(all_items)} total items from museum catalog")
        return all_items

    def day05_search_item(self, query: str, all_items: list) -> dict:
        """
        Search for a specific item using fuzzy text matching

        Args:
            query: Search query (item mention from podcast)
            all_items: List of all museum items

        Returns:
            Best matching item with confidence score
        """
        print(f"\n🔍 Searching for: '{query}'")

        # First try direct API search
        try:
            url = f"{self.api_url}/items"
            params = {'search': query, 'perpage': day05_MAX_SEARCH_RESULTS}
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                api_results = response.json()
                if api_results:
                    print(f"   📌 API returned {len(api_results)} direct matches")

                    # Use these results for similarity matching
                    candidates = api_results
                else:
                    # No API results, use all items
                    candidates = all_items[:500]  # Limit for performance
            else:
                candidates = all_items[:500]

        except Exception as e:
            print(f"   ⚠️  API search failed: {str(e)}, using local matching")
            candidates = all_items[:500]

        if not candidates:
            return self.day05_create_no_match_result(query)

        # Perform similarity matching
        best_match = self.day05_fuzzy_match(query, candidates)

        return best_match

    def day05_fuzzy_match(self, query: str, candidates: list) -> dict:
        """
        Perform fuzzy text matching using TF-IDF similarity

        Args:
            query: Search query
            candidates: List of candidate items

        Returns:
            Best match with confidence score
        """
        # Extract text from candidates
        candidate_texts = []
        for item in candidates:
            # Combine title and description for better matching
            title = item.get('title', '')
            description = item.get('description', '')

            # Handle different possible formats
            if isinstance(title, dict):
                title = title.get('rendered', '') or str(title)
            if isinstance(description, dict):
                description = description.get('rendered', '') or str(description)

            combined_text = f"{title} {description}".lower()
            candidate_texts.append(combined_text)

        # Add query to the corpus
        all_texts = [query.lower()] + candidate_texts

        # Calculate TF-IDF similarity
        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            tfidf_matrix = vectorizer.fit_transform(all_texts)

            # Calculate similarity with query (first item)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

            # Find best match
            best_idx = similarities.argmax()
            best_score = similarities[best_idx]

            if best_score >= day05_SIMILARITY_THRESHOLD:
                best_item = candidates[best_idx]
                print(f"   ✅ Match found (confidence: {best_score:.2f})")

                return self.day05_format_match_result(best_item, best_score, "fuzzy_match")
            else:
                print(f"   ⚠️  Best match confidence too low: {best_score:.2f} < {day05_SIMILARITY_THRESHOLD}")
                return self.day05_create_no_match_result(query)

        except Exception as e:
            print(f"   ❌ Similarity matching failed: {str(e)}")
            return self.day05_create_no_match_result(query)

    @staticmethod
    def day05_format_match_result(item: dict, confidence: float, match_type: str) -> dict:
        """Format a successful match result"""
        # Extract fields safely
        title = item.get('title', '')
        if isinstance(title, dict):
            title = title.get('rendered', '') or str(title)

        description = item.get('description', '')
        if isinstance(description, dict):
            description = description.get('rendered', '') or str(description)

        return {
            "matched": True,
            "match_confidence": round(confidence, 3),
            "match_type": match_type,
            "tainacan_item_id": item.get('id', ''),
            "tainacan_title": title.strip(),
            "tainacan_description": description.strip()[:500],  # Limit description length
            "tainacan_url": item.get('url', ''),
            "tainacan_metadata": json.dumps(item.get('metadata', {}))[:500]
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
            "tainacan_url": "",
            "tainacan_metadata": ""
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
            if row.get('validated', '').lower() in ['yes', 'y', '1', 'true']:
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
        "tainacan_url", "tainacan_metadata"
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matched_items)

    print(f"\n💾 Saved {len(matched_items)} matched items to: {output_path.name}")


def day05_main():
    """Main Tainacan search pipeline"""
    print("=" * 80)
    print("Day 05: Tainacan Museum Search Pipeline")
    print("Fuzzy Matching with Museu Ipiranga API")
    print("=" * 80)

    # Ensure directories
    day05_ensure_directories()

    # Load validated items
    print("\n📂 Loading validated items...")
    try:
        validated_items = day05_load_validated_items()
        print(f"   ✅ Loaded {len(validated_items)} validated items")
    except FileNotFoundError as e:
        print(f"\n{str(e)}")
        print("\n⚠️  Make sure you've:")
        print("   1. Run day05_PIPELINE_extract_items.py")
        print("   2. Manually validated items in items_to_validate.csv")
        print("   3. Marked 'validated' column as 'yes' for items to search")
        sys.exit(1)

    if not validated_items:
        print("\n⚠️  No validated items found!")
        print("   Open day05/data/processed/items_to_validate.csv")
        print("   Mark items as 'validated=yes' to search for them")
        sys.exit(0)

    # Initialize searcher
    searcher = day05_TainacanSearcher()

    # Fetch all museum items once (for fuzzy matching)
    all_items = searcher.day05_get_all_items(max_items=2000)

    # Search for each validated item
    matched_items = []

    for i, item in enumerate(validated_items, 1):
        print(f"\n{'='*80}")
        print(f"Processing {i}/{len(validated_items)}")

        query = item['item_mention']
        match_result = searcher.day05_search_item(query, all_items)

        # Combine original item data with match result
        combined = {**item, **match_result}
        matched_items.append(combined)

        time.sleep(0.5)  # Rate limiting

    # Save results
    output_path = day05_PROCESSED_DIR / "matched_items.csv"
    day05_save_matched_items(matched_items, output_path)

    # Summary
    print("\n" + "=" * 80)
    print("📊 Search Summary")
    print("=" * 80)

    total = len(matched_items)
    matched = sum(1 for m in matched_items if m['matched'])
    not_matched = total - matched

    print(f"Total items searched: {total}")
    print(f"   ✅ Matched: {matched}")
    print(f"   ❌ Not matched: {not_matched}")

    if matched > 0:
        avg_confidence = sum(m['match_confidence'] for m in matched_items if m['matched']) / matched
        print(f"   📊 Average confidence: {avg_confidence:.3f}")

    print("\n✅ Search complete!")
    print(f"📂 Results saved to: {output_path}")
    print("\n🔜 Next step: python day05_DATA_load_bigquery.py")


if __name__ == "__main__":
    day05_main()
