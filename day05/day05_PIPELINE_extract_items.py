"""
Day 05: Museum Item Extraction Pipeline
Extracts mentioned museum items from podcast transcripts using GPT-4

Usage:
    python day05_PIPELINE_extract_items.py
"""

import json
import csv
from pathlib import Path
from openai import OpenAI
import sys

# Import day05 configuration
from day05_CONFIG_settings import (
    day05_TRANSCRIPTS_DIR,
    day05_PROCESSED_DIR,
    day05_OPENAI_API_KEY,
    day05_ensure_directories
)


class day05_ItemExtractor:
    """Extracts museum item mentions from transcripts using GPT-4"""

    def __init__(self):
        """Initialize OpenAI client"""
        if not day05_OPENAI_API_KEY:
            raise ValueError("❌ OpenAI API key not found! Set KEY_OPENAI_DAY05 in config/.env")

        self.client = OpenAI(api_key=day05_OPENAI_API_KEY)
        print("✅ OpenAI client initialized")

    def day05_extract_items_from_transcript(self, transcript_data: dict, episode_id: str) -> list:
        """
        Use GPT-4 to extract museum item mentions from transcript

        Args:
            transcript_data: Transcript JSON data with segments
            episode_id: Episode identifier

        Returns:
            List of extracted items with metadata
        """
        print(f"\n🔍 Extracting items from Episode {episode_id}...")

        # Prepare transcript text with timestamps for GPT
        formatted_transcript = self.day05_format_transcript_for_gpt(transcript_data)

        # GPT prompt for item extraction
        system_prompt = """Você é um especialista em identificar menções a artefatos e obras do Museu do Ipiranga em transcrições de podcasts.

Sua tarefa é extrair TODAS as menções específicas a:
- Pinturas e quadros
- Fotografias
- Esculturas e estátuas
- Objetos históricos
- Documentos e manuscritos
- Peças do acervo
- Mobiliário histórico
- Vestimentas e uniformes
- Armas e equipamentos militares
- Qualquer outro item mencionado que possa estar no acervo do museu

Para cada item mencionado, extraia:
1. O nome ou descrição exata como foi mencionado
2. O timestamp aproximado da menção
3. Contexto adicional (autor, período, tema)

Retorne APENAS um JSON válido no formato:
{
  "items": [
    {
      "mention": "descrição exata do item como mencionado",
      "timestamp": "HH:MM:SS",
      "context": "contexto adicional relevante",
      "confidence": "high/medium/low"
    }
  ]
}

Se não houver menções claras a itens do museu, retorne {"items": []}.
"""

        user_prompt = f"""Analise esta transcrição do podcast sobre o Museu do Ipiranga e extraia todas as menções a itens do acervo:

{formatted_transcript}

Lembre-se: retorne APENAS o JSON, sem texto adicional."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            # Parse GPT response
            gpt_output = response.choices[0].message.content.strip()

            # Clean potential markdown code blocks
            if gpt_output.startswith("```"):
                gpt_output = gpt_output.split("```")[1]
                if gpt_output.startswith("json"):
                    gpt_output = gpt_output[4:]
                gpt_output = gpt_output.strip()

            extracted_data = json.loads(gpt_output)
            items = extracted_data.get("items", [])

            print(f"   ✅ Extracted {len(items)} item mentions")

            # Enrich with episode metadata
            enriched_items = []
            for item in items:
                enriched_items.append({
                    "episode_id": episode_id,
                    "item_mention": item.get("mention", ""),
                    "timestamp": item.get("timestamp", "00:00:00"),
                    "context": item.get("context", ""),
                    "confidence": item.get("confidence", "medium"),
                    "validated": "",  # For manual validation
                    "notes": ""  # For manual notes
                })

            return enriched_items

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            return []

    @staticmethod
    def day05_format_transcript_for_gpt(transcript_data: dict) -> str:
        """Format transcript segments for GPT analysis"""
        formatted = f"Episódio: {transcript_data.get('file_name', 'Unknown')}\n\n"

        for segment in transcript_data["segments"][:100]:  # Limit to first 100 segments to stay within token limits
            formatted += f"[{segment['start']}] {segment['text']}\n"

        if len(transcript_data["segments"]) > 100:
            formatted += f"\n... ({len(transcript_data['segments']) - 100} segmentos adicionais omitidos)\n"

        return formatted


def day05_load_transcript(episode_id: str) -> dict:
    """Load transcript JSON for an episode"""
    transcript_path = day05_TRANSCRIPTS_DIR / f"episode_{episode_id}_transcript.json"

    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")

    with open(transcript_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def day05_save_items_to_csv(all_items: list, output_path: Path):
    """Save extracted items to CSV for manual validation"""
    if not all_items:
        print("⚠️  No items extracted from any episode")
        return

    fieldnames = ["episode_id", "item_mention", "timestamp", "context", "confidence", "validated", "notes"]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_items)

    print(f"\n💾 Saved {len(all_items)} items to: {output_path.name}")


def day05_main():
    """Main item extraction pipeline"""
    print("=" * 80)
    print("Day 05: Museum Item Extraction Pipeline")
    print("GPT-4 Analysis of Podcast Transcripts")
    print("=" * 80)

    # Ensure directories exist
    day05_ensure_directories()

    # Find all transcript files
    transcript_files = sorted(day05_TRANSCRIPTS_DIR.glob("episode_*_transcript.json"))

    if not transcript_files:
        print(f"\n❌ ERROR: No transcripts found in {day05_TRANSCRIPTS_DIR}")
        print("   Run day05_DATA_transcribe_whisper.py first!")
        sys.exit(1)

    print(f"\n📂 Found {len(transcript_files)} transcript(s):")
    for f in transcript_files:
        print(f"   - {f.name}")

    # Initialize extractor
    extractor = day05_ItemExtractor()

    # Process each transcript
    all_items = []

    for transcript_file in transcript_files:
        # Extract episode ID from filename
        episode_id = transcript_file.stem.replace("_transcript", "").split('_')[-1]

        try:
            # Load transcript
            transcript_data = day05_load_transcript(episode_id)

            # Extract items
            items = extractor.day05_extract_items_from_transcript(transcript_data, episode_id)
            all_items.extend(items)

        except Exception as e:
            print(f"   ❌ ERROR processing episode {episode_id}: {str(e)}")

    # Save to CSV for manual validation
    output_path = day05_PROCESSED_DIR / "items_to_validate.csv"
    day05_save_items_to_csv(all_items, output_path)

    # Summary
    print("\n" + "=" * 80)
    print("📊 Extraction Summary")
    print("=" * 80)
    print(f"Total items extracted: {len(all_items)}")

    by_episode = {}
    for item in all_items:
        ep = item["episode_id"]
        by_episode[ep] = by_episode.get(ep, 0) + 1

    print("\nBy episode:")
    for ep_id in sorted(by_episode.keys()):
        print(f"   Episode {ep_id}: {by_episode[ep_id]} items")

    print("\n" + "=" * 80)
    print("✅ NEXT STEP: Manual Validation Required")
    print("=" * 80)
    print(f"📝 Open: {output_path}")
    print()
    print("Instructions:")
    print("1. Review each 'item_mention' in the CSV")
    print("2. Mark 'validated' column as 'yes' or 'no'")
    print("3. Add any notes in the 'notes' column")
    print("4. Save the file when done")
    print()
    print("Then run: python day05_DATA_search_tainacan.py")


if __name__ == "__main__":
    day05_main()
