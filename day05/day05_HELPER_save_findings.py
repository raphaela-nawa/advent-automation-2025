"""
Day 05: Helper Script - Save Manual Search Findings
Facilita salvar resultados de buscas manuais

Uso:
    python day05_HELPER_save_findings.py
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from day05_TOOL_manual_search import day05_ManualSearchTool
from day05_CONFIG_settings import day05_PROCESSED_DIR


def day05_save_search_results():
    """
    Script interativo para fazer buscas e salvar resultados
    """
    print("=" * 100)
    print("🔍 Day 05: Salvar Achados do Manual Search")
    print("=" * 100)

    # Initialize tool
    tool = day05_ManualSearchTool()

    print("\n📝 Como usar:")
    print("   1. Digite sua busca")
    print("   2. Escolha se quer salvar os resultados")
    print("   3. Digite o nome do arquivo (ou deixe em branco para usar padrão)")
    print("\nComandos de busca:")
    print("   - 'independencia' - busca simples")
    print("   - 'autor:militão' - busca por autor")
    print("   - 'all:fotografia' - busca em todos os campos")
    print("   - 'q' - sair")
    print("=" * 100)

    search_count = 0

    while True:
        # Get search query
        query = input("\n🔍 Buscar (ou 'q' para sair): ").strip()

        if query.lower() in ['q', 'quit', 'exit', 'sair']:
            print("👋 Até logo!")
            break

        if not query:
            continue

        # Parse and execute search
        results = None
        total = 0

        if ':' in query:
            field, value = query.split(':', 1)
            field = field.strip()
            value = value.strip()

            if field.lower() in ['autor', 'author']:
                results, total = tool.search_by_author(value)
                search_type = f"author_{value}"
            elif field.lower() == 'all':
                results, total = tool.search_all_fields(value)
                search_type = f"all_{value}"
            else:
                results, total = tool.search_by_field(field, value)
                search_type = f"{field}_{value}"
        else:
            results, total = tool.search_simple(query)
            search_type = query

        # Display results
        tool.display_results(results, total_matches=total)

        if results.empty:
            continue

        # Ask if user wants to save
        save = input("\n💾 Salvar estes resultados? (s/n): ").strip().lower()

        if save in ['s', 'sim', 'y', 'yes']:
            search_count += 1

            # Generate default filename
            safe_query = "".join(c if c.isalnum() else "_" for c in search_type)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"search_{search_count}_{safe_query[:30]}_{timestamp}.csv"

            # Ask for filename
            filename = input(f"\n📄 Nome do arquivo [{default_filename}]: ").strip()

            if not filename:
                filename = default_filename

            # Ensure .csv extension
            if not filename.endswith('.csv'):
                filename += '.csv'

            # Save
            tool.export_results(results, filename)
            print(f"\n✅ Salvo em: {day05_PROCESSED_DIR / filename}")


def day05_create_mapping_template():
    """
    Cria um template CSV para mapear podcast → tainacan
    """
    print("\n" + "=" * 100)
    print("📋 Criar Template de Mapeamento")
    print("=" * 100)

    # Load items_to_validate.csv
    items_file = day05_PROCESSED_DIR / "items_to_validate.csv"

    if not items_file.exists():
        print(f"\n⚠️  Arquivo não encontrado: {items_file}")
        print("   Execute primeiro: python day05_PIPELINE_extract_items.py")
        return

    df = pd.read_csv(items_file)

    # Filter only validated items
    if 'validated' in df.columns:
        validated = df[df['validated'].str.lower() == 'yes']
    else:
        validated = df

    print(f"\n📊 Encontrados: {len(validated)} itens validados para mapear")

    # Create mapping template
    mapping = pd.DataFrame({
        'episode_id': validated.get('episode_id', ''),
        'podcast_mention': validated.get('item_mention', ''),
        'timestamp': validated.get('timestamp', ''),
        'context': validated.get('context', ''),
        'tainacan_id': '',  # To be filled manually
        'tainacan_title': '',  # To be filled manually
        'match_confidence': '',  # high/medium/low
        'notes': ''  # Optional notes
    })

    # Save template
    output_file = day05_PROCESSED_DIR / "mapping_template.csv"
    mapping.to_csv(output_file, index=False, encoding='utf-8')

    print(f"\n✅ Template criado: {output_file}")
    print("\n📝 Próximo passo:")
    print("   1. Abra: mapping_template.csv")
    print("   2. Use o manual search para encontrar cada item")
    print("   3. Preencha: tainacan_id, tainacan_title, match_confidence")
    print("   4. Salve o arquivo")

    return output_file


def day05_quick_export():
    """
    Exportação rápida sem interação - para buscas específicas
    """
    tool = day05_ManualSearchTool()

    print("\n" + "=" * 100)
    print("⚡ Exportação Rápida - Exemplos Comuns")
    print("=" * 100)

    # Example 1: All Militão photos
    print("\n1️⃣  Exportando todas as fotos do Militão...")
    militao, total = tool.search_by_author("militão")
    if not militao.empty:
        tool.export_results(militao, "militao_completo.csv")
        print(f"   Total: {total} fotos")

    # Example 2: Independence paintings
    print("\n2️⃣  Exportando obras sobre independência...")
    indep, total = tool.search_simple("independência")
    if not indep.empty:
        tool.export_results(indep, "independencia_obras.csv")
        print(f"   Total: {total} obras")

    # Example 3: 19th century items
    print("\n3️⃣  Exportando itens do século 19...")
    sec19, total = tool.search_all_fields("século 19")
    if not sec19.empty:
        tool.export_results(sec19, "seculo_19_itens.csv")
        print(f"   Total: {total} itens")

    print("\n✅ Exportações rápidas concluídas!")
    print(f"📁 Arquivos em: {day05_PROCESSED_DIR}")


if __name__ == "__main__":
    print("\n🎯 Escolha uma opção:\n")
    print("1. Busca interativa e salvar resultados")
    print("2. Criar template de mapeamento (podcast → tainacan)")
    print("3. Exportação rápida (exemplos comuns)")
    print("4. Sair")

    choice = input("\nOpção (1-4): ").strip()

    if choice == "1":
        day05_save_search_results()
    elif choice == "2":
        day05_create_mapping_template()
    elif choice == "3":
        day05_quick_export()
    else:
        print("👋 Até logo!")
