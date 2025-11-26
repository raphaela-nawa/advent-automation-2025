# Day 01: IBA Climate Registry Intelligence Layer

**Project ID:** IBA_Climate_Registry_Intelligence
**Contact:** Sara Carnegie (IBA LPRU)
**Duration:** 3 hours
**Status:** [Planning/Development/Complete]

## Objective
Build semantic search and analytics dashboard on top of the existing IBA Climate Registry.

## Tech Stack
- Data: Web scraping (BeautifulSoup)
- Processing: OpenAI embeddings + LangChain
- Storage: ChromaDB (vector store)
- Frontend: Streamlit
- Deploy: Streamlit Cloud

## Quick Start
```bash
# From repo root
cd day01/
streamlit run day01_APP_main.py
```

## Files Overview
- `day01_DATA_scraper.py` - Extracts resources from IBA Registry
- `day01_PIPELINE_search.py` - Semantic search engine
- `day01_PIPELINE_analytics.py` - Dashboard analytics
- `day01_APP_main.py` - Streamlit application

## Deliverables
- [ ] Semantic search interface
- [ ] Analytics dashboard
- [ ] One-pager for Sara
- [ ] GitHub repo ready for sharing
