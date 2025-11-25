# IBA Climate Registry Intelligence Dashboard

## Overview

An interactive web dashboard providing intelligence on bar association climate initiatives worldwide, built on data from the IBA Climate Registry.

## Features

### 🌍 Global Overview Tab
- **Hero Metrics**: Total resources, bar associations, regions covered, and quality score
- **Interactive Map**: Leaflet.js world map with markers for each country
- **Regional Filters**: Toggle visibility by region (Africa, Asia, Europe, LATAM, MENA, North America, Oceania, International)
- **Country Details**: Click markers to see resources per country
- **Trending Sidebar**: Recent submissions and quick stats

### 🔍 Explore Resources Tab
- **Smart Filters**: Filter by source, type, region, and country
- **Search**: Full-text search across titles and descriptions
- **Grid Display**: Responsive card layout with type badges
- **Sortable**: Sort by relevance, date, alphabetical, or country
- **84 Resources**: Complete registry data

## Usage

### Standalone Version
Open `index.html` directly in a web browser or visit the deployed URL.

**URL**: [https://[your-github-username].github.io/advent-automation-2025/day01/](https://[your-github-username].github.io/advent-automation-2025/day01/)

### Embedded Version (for IBA Website)
Use `embed.html` for iframe embedding on external sites:

```html
<iframe src="https://[your-github-username].github.io/advent-automation-2025/day01/embed.html"
        width="100%"
        height="1400px"
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 8px;">
</iframe>
```

**Recommended iframe height**: 1400px (adjustable based on content)

## Data Source

Data scraped from [IBA Climate Registry](https://www.ibanet.org/IBA-Climate-Registry)

**Last Updated**: 2025-11-25 15:54:58
**Total Resources**: 84
**Coverage**: 7 regions, 13+ countries

## GitHub Pages Deployment

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from main branch
   - Folder: `/` (root) or `/day01` if in subdirectory

2. **Access Dashboard**:
   - Standalone: `https://[username].github.io/[repo-name]/day01/index.html`
   - Embeddable: `https://[username].github.io/[repo-name]/day01/embed.html`

3. **Update Links**: Replace `[your-github-username]` and `[repo-name]` in URLs above

## Local Development

No build tools required - pure HTML/CSS/JavaScript:

```bash
# Option 1: Open directly
open index.html

# Option 2: Use Python HTTP server
cd day01/
python3 -m http.server 8000
# Visit http://localhost:8000
```

## Technical Stack

- **Frontend**: Pure vanilla JavaScript (no frameworks)
- **Mapping**: Leaflet.js 1.9.4
- **Charts**: None (uses CSS for visual elements)
- **Data**: Inline JSON (84 resources, ~200KB)
- **Browser Support**: Chrome/Firefox/Safari/Edge (last 2 versions)

## File Structure

```
day01/
├── index.html                      # Standalone dashboard with header/footer
├── embed.html                      # Iframe-optimized (no header/footer)
├── day01_DATA_registry_raw.json   # Source data
├── day01_README_DASHBOARD.md      # This file
└── day01_APP_main.py              # Streamlit version (alternative)
```

## Contact

**Project**: Day 01 - IBA Climate Registry Intelligence Layer
**Duration**: 3-hour MVP
**Contact**: Sara Carnegie (IBA LPRU)
**Repository**: [advent-automation-2025](https://github.com/[your-username]/advent-automation-2025)

## License

Built for IBA LPRU. Data source: [IBA Climate Registry](https://www.ibanet.org/IBA-Climate-Registry).

---

**Last Updated**: 2025-11-25
