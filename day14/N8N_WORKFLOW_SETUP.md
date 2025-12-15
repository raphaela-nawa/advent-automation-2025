# Day 14: n8n Workflow Setup Guide
## Transport Regulatory KPIs Email Report Automation

This guide walks you through setting up the n8n workflow for automated daily transport regulatory reports using Querido Diário API.

---

## Prerequisites

### 1. n8n Installation

**Option A: Cloud (Recommended for this project)**
- Sign up at [n8n.cloud](https://n8n.cloud) - Free tier available
- No local installation needed ✅

**Option B: Local Docker**
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Option C: Local npm**
```bash
npm install -g n8n
n8n start
```

Access n8n at: `http://localhost:5678`

---

## Workflow Architecture

```
┌─────────────────┐
│  Cron Trigger   │ ← Daily at 8am (America/Sao_Paulo)
│   (Schedule)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Function Node  │ ← Prepare cities & keywords
│  (Setup Query)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Loop Over      │ ← For each city + keyword combination
│  Cities         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │ ← Query Querido Diário API
│  (API Call)     │   https://queridodiario.ok.org.br/api/gazettes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Function Node  │ ← Calculate KPIs from API responses
│  (Process Data) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Function Node  │ ← Render HTML email template
│  (Build Email)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Send Email     │ ← SMTP node sends formatted report
│  (SMTP)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Set Variable   │ ← Log execution status
│  (Success Log)  │
└─────────────────┘
         │
         ▼ (Error Path)
┌─────────────────┐
│  Error Trigger  │ ← Catch failures and send alert
│  (Notification) │
└─────────────────┘
```

---

## Step-by-Step Workflow Build

### Step 1: Create New Workflow

1. Open n8n interface
2. Click **"New Workflow"**
3. Name it: `Day14_Transport_KPIs_Daily_Report`

---

### Step 2: Add Schedule Trigger

**Node Type:** Schedule Trigger

**Configuration:**
- **Trigger Interval:** Cron Expression
- **Cron Expression:** `0 8 * * *` (8:00 AM daily)
- **Timezone:** `America/Sao_Paulo`

**Why this schedule?**
- Municipal gazettes typically publish in the morning
- 8am ensures we capture previous day's publications
- São Paulo timezone aligns with Brazilian government working hours

---

### Step 3: Setup Query Parameters (Function Node)

**Node Name:** `Prepare API Queries`

**Code:**
```javascript
// Cities to monitor (IBGE codes)
const cities = {
  'São Paulo': '3550308',
  'Rio de Janeiro': '3304557',
  'Brasília': '5300108',
  'Salvador': '2927408',
  'Fortaleza': '2304400',
  'Belo Horizonte': '3106200'
};

// Transport keywords (Portuguese)
const keywords = [
  'transporte',
  'mobilidade',
  'trânsito',
  'veículo'
];

// Date range (last 24 hours)
const today = new Date();
const yesterday = new Date(today);
yesterday.setDate(yesterday.getDate() - 1);

const sinceDate = yesterday.toISOString().split('T')[0];
const untilDate = today.toISOString().split('T')[0];

// Create queries array
const queries = [];
for (const [cityName, ibgeCode] of Object.entries(cities)) {
  for (const keyword of keywords) {
    queries.push({
      city: cityName,
      territory_id: ibgeCode,
      keyword: keyword,
      since: sinceDate,
      until: untilDate
    });
  }
}

return queries.map(q => ({ json: q }));
```

**Output:** Array of query objects for each city + keyword combination

---

### Step 4: Loop Over Queries (Split In Batches Node)

**Node Type:** Split In Batches

**Configuration:**
- **Batch Size:** 5 (respect rate limits)
- **Options → Reset:** Yes

**Purpose:** Process queries in batches to avoid overwhelming the API

---

### Step 5: Query Querido Diário API (HTTP Request Node)

**Node Name:** `Query Querido Diário`

**Configuration:**
- **Method:** GET
- **URL:** `https://queridodiario.ok.org.br/api/gazettes`
- **Query Parameters:**
  - `territory_ids`: `{{ $json.territory_id }}`
  - `querystring`: `{{ $json.keyword }}`
  - `excerpt_size`: `500`
  - `number_of_excerpts`: `3`
  - `size`: `10`
  - `since`: `{{ $json.since }}`
  - `until`: `{{ $json.until }}`
- **Options:**
  - Response Format: JSON
  - Timeout: 30000 (30 seconds)
  - Retry On Fail: Yes
  - Max Tries: 3

**Rate Limiting:**
- Add **Wait** node after HTTP Request
- Wait Time: 1 second (ensures <60 req/min)

---

### Step 6: Aggregate Results (Aggregate Node)

**Node Type:** Aggregate

**Configuration:**
- **Aggregate:** All Items Into One
- **Include Other Fields:** All fields

**Purpose:** Combine all API responses into a single array for KPI calculation

---

### Step 7: Calculate KPIs (Function Node)

**Node Name:** `Calculate KPIs`

**Code:**
```javascript
const items = $input.all();
const results = {};

// Group by city
items.forEach(item => {
  const city = item.json.city;
  const totalGazettes = item.json.total_gazettes || 0;

  if (!results[city]) {
    results[city] = {
      gazettes: [],
      total: 0
    };
  }

  results[city].total += totalGazettes;
  if (item.json.gazettes) {
    results[city].gazettes.push(...item.json.gazettes);
  }
});

// Calculate KPIs
const kpis = {
  new_regulations: Object.values(results).reduce((sum, city) => sum + city.total, 0),
  active_municipalities: Object.keys(results).filter(city => results[city].total > 0).length,
  compliance_mentions: 0,
  safety_incidents: 0,
  cities_monitored: Object.keys(results).length
};

// Count keyword mentions in excerpts
const complianceKeywords = ['prazo', 'cumprimento', 'fiscalização', 'obrigatoriedade'];
const safetyKeywords = ['acidente', 'segurança viária', 'infração', 'multa'];

Object.values(results).forEach(cityData => {
  cityData.gazettes.forEach(gazette => {
    if (gazette.excerpts) {
      gazette.excerpts.forEach(excerpt => {
        const text = excerpt.toLowerCase();
        complianceKeywords.forEach(kw => {
          if (text.includes(kw)) kpis.compliance_mentions++;
        });
        safetyKeywords.forEach(kw => {
          if (text.includes(kw)) kpis.safety_incidents++;
        });
      });
    }
  });
});

// Generate insights
const trend_insight = kpis.new_regulations > 10
  ? 'Alta atividade regulatória detectada'
  : 'Atividade regulatória normal';

const highlight_insight = `${kpis.active_municipalities} municípios com novas publicações`;

const attention_insight = kpis.safety_incidents > 5
  ? 'Aumento em menções de segurança viária'
  : 'Padrão normal de segurança';

return [{
  json: {
    kpis,
    active_cities: Object.keys(results).filter(c => results[c].total > 0),
    timestamp: new Date().toISOString(),
    date_since: items[0]?.json.since || '',
    date_until: items[0]?.json.until || '',
    trend_insight,
    highlight_insight,
    attention_insight
  }
}];
```

---

### Step 8: Render HTML Email (Function Node)

**Node Name:** `Build HTML Email`

**Code:**
```javascript
const data = $json;

// Read email template (you'll need to paste the HTML template here)
const template = `
<!DOCTYPE html>
<html>
<!-- Paste the contents of day14_email_template.html here -->
<!-- Replace Jinja2 {{ variables }} with ${data.variable} for JavaScript -->
</html>
`;

// Simple template rendering (or use a proper templating library)
let html = template
  .replace(/{{ report_title }}/g, 'Relatório Diário - Transport KPIs Brasil')
  .replace(/{{ timestamp }}/g, new Date(data.timestamp).toLocaleString('pt-BR'))
  .replace(/{{ days_monitored }}/g, '1')
  .replace(/{{ cities_count }}/g, data.kpis.cities_monitored)
  .replace(/{{ kpi_new_regulations }}/g, data.kpis.new_regulations)
  .replace(/{{ kpi_active_municipalities }}/g, data.kpis.active_municipalities)
  .replace(/{{ kpi_compliance_mentions }}/g, data.kpis.compliance_mentions)
  .replace(/{{ kpi_safety_incidents }}/g, data.kpis.safety_incidents)
  .replace(/{{ trend_insight }}/g, data.trend_insight)
  .replace(/{{ highlight_insight }}/g, data.highlight_insight)
  .replace(/{{ attention_insight }}/g, data.attention_insight)
  .replace(/{{ date_since }}/g, data.date_since)
  .replace(/{{ date_until }}/g, data.date_until);

// Handle city list (simplified - use proper loop in production)
const cityBadges = data.active_cities.map(c => `<span class="city-badge">${c}</span>`).join('\n');
html = html.replace(/{% for city in active_cities %}.*?{% endfor %}/gs, cityBadges);

return [{
  json: {
    html_body: html,
    subject: `🚦 Transport KPIs - ${data.date_until} - ${data.kpis.new_regulations} Novas Regulamentações`,
    kpis: data.kpis
  }
}];
```

---

### Step 9: Send Email (Send Email Node)

**Node Type:** Send Email (SMTP)

**Configuration:**
- **From Email:** `{{ $env.DAY14_SENDER_EMAIL }}` or configure in node
- **To Email:** Recipients (comma-separated)
- **Subject:** `{{ $json.subject }}`
- **Email Type:** HTML
- **Body (HTML):** `{{ $json.html_body }}`

**SMTP Credentials:**
- Create new credentials in n8n
- Type: SMTP
- Host: `smtp.gmail.com` (or your SMTP server)
- Port: `587`
- Secure: Use TLS
- Username: Your email
- Password: App password (for Gmail, generate at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords))

---

### Step 10: Log Success (Set Node)

**Node Name:** `Log Success`

**Configuration:**
- **Keep Only Set:** Yes
- **Values:**
  - `execution_status`: `success`
  - `timestamp`: `{{ $now }}`
  - `regulations_count`: `{{ $json.kpis.new_regulations }}`

---

### Step 11: Error Handling (Error Trigger)

**Node Type:** Error Trigger

**Connect to:** Send Email (Error Notification)

**Error Email Configuration:**
- **To:** Your email
- **Subject:** `❌ Day 14 Workflow Failed`
- **Body:**
```
Workflow execution failed.

Error: {{ $json.error.message }}
Node: {{ $json.error.node.name }}
Time: {{ $now }}
```

---

## Testing the Workflow

### Test Mode (Before Scheduling)

1. **Manual Trigger:**
   - Click "Execute Workflow" button
   - Monitor each node's output
   - Check for errors

2. **Verify API Responses:**
   - Click on "Query Querido Diário" node
   - Check "Output" tab
   - Ensure `total_gazettes` field exists

3. **Check KPI Calculation:**
   - Click "Calculate KPIs" node
   - Verify all 4 KPIs are calculated
   - Ensure no null/undefined values

4. **Preview Email:**
   - Click "Build HTML Email" node
   - Copy `html_body` output
   - Paste in HTML preview tool
   - Verify formatting

5. **Test Email Delivery:**
   - First run: Send to yourself only
   - Check spam folder
   - Verify formatting renders correctly

---

## Exporting the Workflow

1. Click "..." menu (top right)
2. Select "Download"
3. Save as: `day14_transport_kpi_workflow.json`
4. Commit to repo: `day14/workflows/`

---

## Production Considerations

### Rate Limiting
- Current setup: ~24 queries (6 cities × 4 keywords)
- With 1-second delays: ~30 seconds total
- Well within 60 req/min limit ✅

### Error Scenarios
- **API Down:** Retry 3 times, then send error email
- **No Results:** Email still sends with "0" values
- **SMTP Failure:** Logged in n8n execution history

### Monitoring
- n8n automatically logs all executions
- Check "Executions" tab for history
- Set up n8n webhooks for external monitoring (optional)

---

## Customization Options

### Add More Cities
Edit "Prepare API Queries" node, add to `cities` object:
```javascript
'Curitiba': '4106902',
'Porto Alegre': '4314902'
```

### Change Keywords
Modify `keywords` array:
```javascript
const keywords = ['transporte público', 'ciclovia', 'pedágio'];
```

### Adjust Schedule
Change cron expression in Schedule Trigger:
- Every 12 hours: `0 */12 * * *`
- Weekdays only: `0 8 * * 1-5`
- Twice daily: `0 8,18 * * *`

---

## Troubleshooting

### Issue: "API returns 403 Forbidden"
- **Cause:** Querido Diário API may have temporary restrictions
- **Fix:** Add delay between requests (already implemented)

### Issue: "No gazettes found"
- **Cause:** No publications matching keywords in date range
- **Fix:** Increase `days_back` or broaden keywords

### Issue: "Email not received"
- **Cause:** SMTP credentials or spam filtering
- **Fix:**
  1. Check SMTP credentials
  2. Test with different recipient
  3. Check spam/junk folder
  4. For Gmail: Enable "Less secure app access" or use App Password

### Issue: "Workflow times out"
- **Cause:** Too many cities/keywords
- **Fix:** Reduce batch size or number of cities

---

## Next Steps

✅ Workflow is ready!

1. **Activate the workflow** (toggle in top right)
2. **Wait for first scheduled run** (or trigger manually)
3. **Take screenshots** for documentation
4. **Save workflow JSON** to repo
5. **Update README.md** with actual results

---

**Need Help?**
- n8n Community: [community.n8n.io](https://community.n8n.io)
- Querido Diário Docs: [docs.queridodiario.ok.org.br](https://docs.queridodiario.ok.org.br)
