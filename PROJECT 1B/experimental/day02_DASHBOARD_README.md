# Streamlit Dashboard - Day 02 Creator Intelligence

## 🚀 Quick Start

### Launch the Dashboard

```bash
cd /Users/raphaelanawa/Desktop/advent2025/repo/advent-automation-2025/day02
streamlit run dashboard_day02.py
```

The dashboard will automatically open in your browser at: `http://localhost:8501`

### Prerequisites

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

Required packages:
- streamlit==1.29.0
- plotly==5.18.0
- pandas==2.1.4

---

## 📊 Dashboard Pages

The dashboard consists of 5 interactive pages:

### 1. 🏠 Overview
**Main landing page with key metrics and highlights**

Features:
- 4 Key Performance Indicators (KPIs)
  - Account Value
  - Weekly Growth Rate
  - Average Engagement
  - 6-Month Projection
- Follower Growth Over Time (line chart)
- Growth Scenarios Comparison (bar chart)
- Content Type Distribution (pie chart)
- Engagement by Content Type
- Top 5 Recent Posts (expandable cards)

**Use Case:** Quick snapshot of account performance and health

---

### 2. 📈 Growth Analysis
**Deep dive into follower growth and projections**

Features:
- Current growth metrics dashboard
- Daily Growth Trend (dual chart: followers + daily new followers)
- 6-Month Growth Scenarios (comparison table)
- Weekly Growth Rate Comparison (bar chart)
- Time to Reach 200K Followers (bar chart)
- Reach & Impressions Trends (line chart)

**Key Insights:**
- Current weekly growth: 0.21%
- Target weekly growth: 2.74%
- Gap: **13x acceleration needed**
- Optimistic 6-month projection: 196,611 followers

**Use Case:** Strategic planning and goal tracking

---

### 3. 🎬 Content Performance
**Analyze what content performs best**

Features:
- Performance metrics by content type (IMAGE, CAROUSEL, VIDEO)
- ROI comparison charts
- Net profit per post analysis
- Engagement trends over time (scatter plot with rolling average)
- Top 10 performing posts table
- Posting pattern analysis:
  - Best days of the week
  - Best hours of the day

**Key Insights:**
- IMAGE posts: 8,607% ROI (highest)
- CAROUSEL posts: $4,590 net profit (highest)
- VIDEO posts: 33.15% engagement (highest)
- Best posting hours: 18:00-21:00 (6 PM - 9 PM)
- Best days: Thursday, Sunday, Wednesday

**Use Case:** Content strategy optimization

---

### 4. 💰 LTV & ROI
**Financial modeling and monetization insights**

Features:
- Follower Lifetime Value (LTV) metrics
- Revenue model breakdown (pie chart)
- 24-month revenue projection
- Engagement value analysis:
  - Value per like: $0.05
  - Value per comment: $0.50
  - Value per save: $2.50
  - Value per share: $1.00
- Content production ROI (detailed table)
- ROI gauge charts (IMAGE, CAROUSEL, VIDEO)

**Key Insights:**
- LTV per follower: $55.97
- Total account value: $5,751,862
- Monthly value per follower: $2.33
- Annual value per follower: $27.98
- **Saves are 50x more valuable than likes!**

**Use Case:** Pricing partnerships, justifying ad spend, monetization strategy

---

### 5. 🤖 AI Insights
**AI-powered content intelligence and recommendations**

Features:
- Viral Content Patterns:
  - Top themes
  - Emotional triggers
  - Writing style analysis
  - Hashtag strategy
- Caption Effectiveness Analysis:
  - High performer patterns
  - Low performer issues
  - Best practices
  - Optimal caption length
- 10 Strategic Recommendations (expandable)
- 4-Week Content Calendar with specific post ideas
- Comprehensive Growth Strategy:
  - Immediate actions (30 days)
  - Content strategy
  - Engagement tactics
  - Monetization strategy
  - Growth hacks (algorithm optimization)
  - Key metrics to track

**Key Insights:**
- Optimal caption length: 50-100 characters
- Top themes: Travel experiences, personal growth, perfect moments
- Top emojis: 💛 🔥 ✨ 🌍 🖤
- Top hashtags: #travelgirl #viagens #nomadlife #europeansummer

**Use Case:** Content creation guidance, strategic planning, actionable improvements

---

## 🎨 Dashboard Features

### Interactive Elements
- **Hover tooltips** on all charts for detailed data
- **Expandable cards** for detailed post information
- **Dynamic filters** (coming soon)
- **Real-time data refresh** from database

### Responsive Design
- Wide layout optimized for desktop viewing
- Mobile-friendly (basic support)
- Clean, professional styling with custom CSS

### Data Sources
- **SQLite Database:** `data/creator_intel.db`
  - `account_metrics` table (90 days)
  - `posts` table (100 posts)
- **JSON Analysis:** `data/hour2_analysis_results.json`
  - LTV calculations
  - AI insights
  - Growth projections

---

## 📋 Usage Tips

### Navigation
- Use the **sidebar radio buttons** to switch between pages
- Sidebar shows quick metrics (always visible)
- Sidebar displays current target (200K in 6 months, 2.74% weekly growth)

### Performance
- First load may take 5-10 seconds (caching data)
- Subsequent page loads are instant (cached)
- To refresh data: Stop server, re-run analysis pipeline, restart server

### Exporting Data
To export visualizations:
1. Hover over any Plotly chart
2. Click camera icon (top right of chart)
3. Download as PNG

### Customization
The dashboard can be customized by editing `dashboard_day02.py`:
- **Colors:** Update Plotly color schemes
- **Metrics:** Add/remove KPIs
- **Charts:** Modify chart types and layouts
- **Pages:** Add new analysis pages

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find and kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run dashboard_day02.py --server.port 8502
```

### Data Not Loading
```bash
# Ensure database exists
ls -lh data/creator_intel.db

# Ensure analysis results exist
ls -lh data/hour2_analysis_results.json

# Re-run analysis if needed
python pipeline_day02_hour2.py
```

### Module Not Found Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installations
pip list | grep -E "streamlit|plotly|pandas"
```

### Dashboard Crashes
Check terminal output for error messages:
- Common issue: Data schema mismatch
- Solution: Re-load synthetic data and re-run analysis

---

## 🎯 Dashboard Metrics Summary

### Overview Page KPIs
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Followers | 102,768 | 200,000 | 51.4% |
| Weekly Growth | 0.21% | 2.74% | ⚠️ Below target |
| Avg Engagement | 32.51% | >30% | ✅ Excellent |
| Account Value | $5.75M | Growing | ✅ Strong |

### Content Performance Winners
1. **Best ROI:** IMAGE (8,607%)
2. **Best Profit:** CAROUSEL ($4,590/post)
3. **Best Engagement:** VIDEO (33.15%)

### Growth Reality
- **Current trajectory:** 110,825 followers in 6 months
- **Gap to target:** 89,175 followers
- **Required acceleration:** 13x current growth rate

---

## 📊 Visual Examples

### Chart Types Used
- **Line Charts:** Time series (growth, impressions, reach)
- **Bar Charts:** Comparisons (scenarios, content types)
- **Pie Charts:** Distribution (content types, revenue breakdown)
- **Scatter Plots:** Engagement over time with trend lines
- **Gauge Charts:** ROI indicators
- **Tables:** Top posts, metrics comparison

### Color Scheme
- Primary: `#1f77b4` (Blue)
- Secondary: `#ff7f0e` (Orange)
- Success: `#28a745` (Green)
- Warning: `#ffc107` (Yellow)
- Danger: `#dc3545` (Red)

---

## 🚀 Next Steps

### Immediate (After Reviewing Dashboard)
1. Identify underperforming metrics
2. Review AI recommendations
3. Implement 4-week content calendar
4. Track progress weekly

### Short-term (30 Days)
1. Execute immediate actions from growth strategy
2. Test different content types based on ROI data
3. Optimize posting times (18:00-21:00)
4. Increase posting frequency (4-5x/week)

### Long-term (6 Months)
1. Monitor weekly growth rate progression
2. Adjust strategy based on engagement trends
3. Leverage LTV data for partnership pricing
4. Aim for realistic scenario (110K) minimum

---

## 📝 Credits

**Created:** November 24, 2025
**Project:** Day 02 - Creator Intelligence System
**Client:** @wanderlust_samira
**Tech Stack:** Streamlit + Plotly + Pandas
**Data Source:** Instagram Business Account (synthetic data)

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review terminal output for error messages
3. Ensure all prerequisites are met
4. Re-run pipeline if data is stale

**Dashboard File:** `dashboard_day02.py` (1,200+ lines)
**Status:** ✅ Production Ready
