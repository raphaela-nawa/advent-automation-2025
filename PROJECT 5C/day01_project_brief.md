# Project Brief: IBA Climate Registry Intelligence Layer

**Day:** 01
**Project ID:** 5C
---

## 🎯 Strategic Context

### Background
The International Bar Association (IBA) maintains a **Climate Registry** - a global knowledge-sharing platform where bar associations and law societies upload climate-related policies, guidance documents, carbon footprint reports, and educational materials.

Following the **IBA Roundtable on Bar Association Climate Initiatives (Feb 2025)**, where nearly 50 organizations participated, several critical gaps were identified:

**Key Findings from Roundtable:**
- Participants struggled to **discover similar initiatives** across jurisdictions
- Demand for **better knowledge-sharing mechanisms** and networking tools
- Need for **practical guidance** that's easy to find and apply
- Rapidly evolving regulations require **dynamic, searchable resources**

**Current State of Registry:**
- ✅ Excellent repository of documents
- ❌ Limited search functionality (only "search by region")
- ❌ No semantic/intelligent query capabilities
- ❌ No analytics or pattern identification
- ❌ Difficult to discover relevant resources across themes

### Timing & Opportunity
**Post-COP30 Momentum:** IBA just completed major presence at COP30 in Belém (Nov 2025) with multiple side events and increased visibility in climate law space.

**Upcoming Milestone:** Post-COP30 reflection webinar (Dec 1, 2025) where LPRU will consolidate takeaways and plan next steps.

**Strategic Window:** There's appetite within IBA/LPRU for tools that enhance accessibility and collaboration around climate initiatives.

---

## 🔴 Problem Statement

### For Legal Practitioners
> "I know the IBA Climate Registry exists, but I can't easily find guidance on specific topics like 'advised emissions' or 'carbon accounting for law firms'. I end up manually clicking through documents hoping to find something relevant."

### For Bar Associations
> "We're developing a climate policy and want to learn from peers in similar jurisdictions. The Registry doesn't make it easy to identify who's doing comparable work or what approaches have been tried."

### For IBA LPRU (Sara's Team)
> "We have visibility challenges. We don't know what's really *in* the Registry - which themes dominate, which regions are under-represented, or where the gaps are. This makes strategic planning difficult."

### Core Problem
**The IBA Climate Registry is data-rich but insight-poor.** Valuable knowledge exists but isn't easily discoverable, comparable, or actionable.

---

## 💡 Solution Overview

### What We're Building
**An intelligent layer that sits on top of the existing IBA Climate Registry**, making it searchable, analyzable, and actionable - without modifying the official IBA website.

### Two Core Modules (3-hour MVP)

#### **Module 1: Semantic Search Engine** (1.5h)
**What it does:**
- Natural language queries: "Which bar associations have carbon calculators?"
- AI-powered answers with source citations
- Summarizes findings across multiple documents
- Links directly to original Registry resources

**Technology:**
- Web scraping → ChromaDB (vector store) → OpenAI embeddings → LangChain RAG
- Streamlit interface

**Example Queries:**
```
❓ "What guidance exists on advised emissions?"
✅ Returns: 3 relevant resources with summaries + links

❓ "Which jurisdictions have operational net-zero commitments?"
✅ Returns: List of bar associations + their approaches

❓ "Show me litigation support resources"
✅ Returns: Filtered results by type
```

#### **Module 2: Analytics Dashboard** (1h)
**What it does:**
- Visual overview: geographic coverage, thematic breakdown, timeline
- Gap analysis: under-represented regions/themes
- Growth metrics: Registry adoption over time
- Strategic insights for LPRU planning

**Visualizations:**
- 🗺️ World map: Registry coverage by country/region
- 📊 Thematic pie chart: % operational vs. policy vs. education vs. litigation
- 📈 Timeline: Initiative launch dates (momentum tracking)
- 🎯 Gap matrix: What's missing?

---

## 🎁 Deliverables

### 1. Live Web Application
- **Platform:** Streamlit Cloud (public URL)
- **Access:** No login required, shareable link
- **Independence:** Completely separate from IBA website

### 2. GitHub Repository
```
day01/
├── day01_README.md           # Setup instructions
├── day01_APP_main.py         # Streamlit app
├── day01_DATA_scraper.py     # Registry data extraction
├── day01_PIPELINE_search.py  # Semantic search engine
└── day01_PIPELINE_analytics.py  # Dashboard analytics
```

### 3. One-Pager for Sara
- Problem → Solution → Impact
- Screenshots of interface
- Potential next steps if IBA wants to integrate/expand

---

## 🎯 Success Criteria

### For Legal Practitioners
- ✅ Can find relevant resources in <30 seconds (vs. manual browsing)
- ✅ Discover initiatives from other jurisdictions they didn't know existed
- ✅ Get synthesized answers, not just document links

### For Bar Associations
- ✅ Identify peer organizations with similar work
- ✅ Access best practices and comparative approaches
- ✅ Reduce duplication of effort (reuse vs. reinvent)

### For IBA LPRU
- ✅ Strategic visibility: know what's in the Registry
- ✅ Data-driven planning: identify gaps and opportunities
- ✅ Enhanced value proposition: Registry becomes more useful → more submissions

### For Rapha (You)
- ✅ Demonstrate LLM + legal domain expertise
- ✅ Show ability to build practical tools quickly
- ✅ Open door for collaboration with IBA/Sara
- ✅ Portfolio piece: "AI for social impact in legal sector"

---

## 🚀 Why This Matters

### Immediate Impact
- **Lawyers find resources faster** → Better client advice
- **Bar associations learn from peers** → Stronger policies
- **LPRU gains strategic insights** → Smarter resource allocation

### Strategic Positioning
This project demonstrates the **intersection of three things**:
1. **Legal/institutional expertise** (IBA, climate law, policy work)
2. **Modern data engineering** (LLM, vector search, web scraping)
3. **Social impact focus** (climate justice, global collaboration)

This combination is **rare** and **valuable** - especially for organizations like IBA that sit at the intersection of law, policy, and global coordination.

### Scalability Potential
If successful, this approach could extend to:
- Other IBA registries (gender equality, business & human rights, etc.)
- Integration with IBA's official platforms
- Training tool for new lawyers entering climate practice
- Foundation for a "Climate Law Knowledge Graph"

---

## ⚠️ Constraints & Risk Mitigation

### Political Sensitivity
**Risk:** IBA has internal politics; unsolicited tools might be seen as criticism
**Mitigation:** Frame as "building on top of" excellent existing work, not replacing it. Position as experimental prototype, not official recommendation.

### Data Limitations
**Risk:** Registry may have limited structured data for scraping
**Mitigation:** Combine real scraped data with synthetic enrichment based on Roundtable report. Be transparent about data sources.

### Technical Scope
**Risk:** 3-hour constraint may limit polish
**Mitigation:** Focus on 2 core modules (search + analytics) done well, rather than 5 modules done poorly. MVP approach with clear V2 roadmap.

### API Costs
**Risk:** OpenAI embeddings/queries could get expensive
**Mitigation:** Implement caching aggressively, use smaller embedding models, batch process upfront.

---

## 📅 Next Steps After Delivery

### Immediate (Week 1)
1. Share prototype with Sara informally
2. Gather feedback from 2-3 LPRU colleagues
3. Refine based on input

### Short-term (Month 1)
1. Present at LPRU team meeting (if invited)
2. Write LinkedIn post co-authored with Sara (amplification)
3. Open-source GitHub repo (community contributions)

### Long-term (Quarter 1)
1. Explore integration with IBA website (if there's appetite)
2. Expand to other IBA registries
3. Develop training materials for bar associations

---

## 📊 Portfolio Value

### Skills Showcased
- ✅ **LLM Engineering:** RAG, embeddings, semantic search
- ✅ **Data Engineering:** Web scraping, ETL, vector databases
- ✅ **Product Thinking:** User-centered design, MVP scoping
- ✅ **Domain Expertise:** Climate law, legal institutions, policy work
- ✅ **Stakeholder Management:** Building for real collaborator (Sara/IBA)

### Target Audiences
- **NGOs/Think Tanks:** Tools for knowledge management
- **Legal Tech Companies:** AI applications in law
- **International Organizations:** Multilateral collaboration platforms
- **Consultancies:** Climate + legal + tech intersection

---

## 🎤 Elevator Pitch (for Sara)

> "After exploring the IBA Climate Registry and reviewing the Roundtable findings, I noticed a gap: excellent resources exist but discoverability is limited. I built a prototype intelligence layer that makes the Registry searchable through natural language queries and provides strategic analytics for LPRU planning. It's completely independent of your website - just an additional tool lawyers can use. Takes 30 seconds to find what previously took 30 minutes. Would love to show you and get your thoughts."

---

## 📎 References

- IBA Climate Registry: https://www.ibanet.org/IBA-Climate-Registry
- IBA Roundtable Report (Feb 2025): https://www.ibanet.org/document?id=Roundtable-on-bar-association-and-law-society-climate-initiatives
- IBA COP30 Participation: Multiple side events, Nov 2025
- Post-COP30 Reflection Webinar: Dec 1, 2025

---

**Document Owner:** Rapha
**Last Updated:** [Date]
**Status:** Ready for Development
