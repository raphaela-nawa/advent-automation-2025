# Testando Bypass do Cloudflare

## 🎯 Objetivo

Testar diferentes técnicas para ultrapassar a proteção Cloudflare da API Querido Diário.

---

## 📋 Opções para Testar (Ordem de Eficácia)

### 1. CloudScraper (Recomendado - Rápido) ⭐⭐

**Instalar:**
```bash
pip install cloudscraper
```

**Testar:**
```bash
python3 day14_HELPER_cloudscraper.py
```

**Como funciona:**
- Resolve JavaScript challenges automaticamente
- Imita navegador Chrome
- Gerencia cookies do Cloudflare

**Taxa de sucesso:** ~70-80%

---

### 2. curl_cffi (Melhor TLS Fingerprint) ⭐⭐⭐

**Instalar:**
```bash
pip install curl_cffi
```

**Testar:**
```python
from curl_cffi import requests

response = requests.get(
    'https://queridodiario.ok.org.br/api/gazettes',
    params={'territory_ids': '3550308', 'querystring': 'transporte'},
    impersonate="chrome120"
)

print(response.status_code)
print(response.text[:200])
```

**Como funciona:**
- Usa libcurl com JA3 fingerprint de Chrome real
- TLS handshake idêntico
- Melhor para Cloudflare moderno

**Taxa de sucesso:** ~85-90%

---

### 3. Undetected ChromeDriver (Mais Lento, Mais Confiável) ⭐⭐⭐

**Instalar:**
```bash
pip install undetected-chromedriver
```

**Testar:**
```python
import undetected_chromedriver as uc
import time

driver = uc.Chrome(headless=True, use_subprocess=False)
driver.get('https://queridodiario.ok.org.br/api/gazettes?territory_ids=3550308&querystring=transporte')

# Esperar Cloudflare resolver
time.sleep(5)

content = driver.page_source
print(content[:200])
driver.quit()
```

**Como funciona:**
- Navegador Chrome real (patched para evitar detecção)
- Executa JavaScript challenges
- Espera Cloudflare resolver

**Taxa de sucesso:** ~95%
**Desvantagem:** Lento (~5-10 segundos por request)

---

### 4. Playwright (Alternativa Moderna)

**Instalar:**
```bash
pip install playwright
playwright install chromium
```

**Testar:**
```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()

    # Navegar
    page.goto('https://queridodiario.ok.org.br/api/gazettes?territory_ids=3550308')

    # Esperar
    time.sleep(3)

    # Pegar conteúdo
    content = page.content()
    print(content[:200])

    browser.close()
```

**Taxa de sucesso:** ~90%

---

## 🔧 Atualizando o Proxy para Usar CloudScraper

Se `cloudscraper` funcionar, atualize `day14_API_PROXY.py`:

### Opção A: Trocar Import

**De:**
```python
from day14_SYNTHETIC_data_generator import day14_generate_synthetic_report
```

**Para:**
```python
from day14_HELPER_cloudscraper import Day14CloudscraperClient
from day14_CONFIG_settings import DAY14_TERRITORY_IDS
```

### Opção B: Endpoint Híbrido

```python
@app.route('/kpis', methods=['GET'])
def get_kpis():
    api_key = request.args.get('api_key', '')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    days_back = int(request.args.get('days_back', 1))
    use_real_api = request.args.get('real_api', 'false').lower() == 'true'

    if use_real_api:
        # Tentar API real
        try:
            client = Day14CloudscraperClient()
            # ... implementar fetching real
            return jsonify(result)
        except:
            # Fallback para synthetic
            pass

    # Synthetic data (padrão)
    result = day14_generate_synthetic_report(days_back=days_back)
    return jsonify(result)
```

---

## 🎯 Estratégia Recomendada

### Para Portfolio/Demo:

**Use Synthetic Data** ✅
- Funciona 100% do tempo
- Não depende de API externa
- Demonstra habilidade técnica
- Documentação honesta

### Para Produção Real:

**Hierarquia de Tentativas:**
```python
try:
    # 1. Tentar curl_cffi
    result = fetch_with_curl_cffi()
except:
    try:
        # 2. Fallback para cloudscraper
        result = fetch_with_cloudscraper()
    except:
        try:
            # 3. Fallback para undetected-chrome (lento mas confiável)
            result = fetch_with_selenium()
        except:
            # 4. Usar dados em cache ou synthetic
            result = get_cached_or_synthetic()
```

---

## ⚠️ Considerações Éticas

### ✅ Aceitável:
- Acessar API pública documentada
- Respeitar rate limits
- Uso educacional/portfolio
- Uso com permissão da organização

### ❌ Não Aceitável:
- Scraping agressivo
- Ignorar robots.txt
- DDoS ou sobrecarga
- Acesso não autorizado a dados privados

**Querido Diário:** API pública, dados públicos (diários oficiais), projeto open source - ✅ ético usar

---

## 📊 Comparação de Técnicas

| Técnica | Velocidade | Taxa Sucesso | Complexidade | Custo CPU |
|---------|-----------|--------------|--------------|-----------|
| **Headers básicos** | ⚡⚡⚡ | 10% | Baixa | Baixo |
| **cloudscraper** | ⚡⚡ | 70-80% | Média | Médio |
| **curl_cffi** | ⚡⚡ | 85-90% | Média | Médio |
| **undetected-chrome** | ⚡ | 95%+ | Alta | Alto |
| **Synthetic data** | ⚡⚡⚡ | 100% | Baixa | Baixíssimo |

---

## 🚀 Teste Rápido

```bash
# 1. Instalar cloudscraper
pip install cloudscraper

# 2. Testar
python3 day14_HELPER_cloudscraper.py

# 3. Se funcionar (>0 gazettes):
#    - Atualizar day14_API_PROXY.py
#    - Documentar no README que usa cloudscraper

# 4. Se NÃO funcionar:
#    - Manter synthetic data (solução atual)
#    - Documentar que API está bloqueada
```

---

## 📝 Documentação no README

**Se Cloudscraper funcionar:**
```markdown
### Data Source

Uses **Querido Diário API** via `cloudscraper` library to bypass
Cloudflare bot protection while respecting rate limits.
```

**Se continuar bloqueado:**
```markdown
### Data Source

Originally designed for **Querido Diário API**, currently uses
realistic synthetic data due to Cloudflare bot protection blocking
all automated access methods tested (requests, cloudscraper, curl_cffi).

The synthetic data generator creates authentic patterns matching
real API structure for portfolio demonstration.
```

---

## ✅ Conclusão

**Para seu portfolio Day 14:**
- ✅ Synthetic data é uma solução **profissional** e **honesta**
- ✅ Mostra problem-solving quando APIs são inacessíveis
- ✅ Sistema está **pronto** para API real quando disponível
- ✅ Documentação clara sobre limitações

**Não precisa se preocupar!** A solução atual está perfeita para portfolio. 🎯
