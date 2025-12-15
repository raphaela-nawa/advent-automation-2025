# Solução: Cloudflare Blocking API Requests

## 🛡️ Problema

A API do Querido Diário está protegida por Cloudflare, que bloqueia requisições HTTP diretas do n8n com erro:
```
Forbidden - perhaps check your credentials?
```

Isso acontece porque o Cloudflare detecta que a requisição vem de um bot (n8n) e não de um navegador real.

---

## ✅ Solução Recomendada: API Proxy Local

Vamos criar um servidor Flask local que:
1. Recebe chamadas do n8n (localhost)
2. Faz as requisições para Querido Diário (com headers de navegador)
3. Retorna os dados para o n8n

### Passo 1: Instalar Dependências

```bash
cd day14
pip install -r day14_requirements.txt
```

### Passo 2: Testar o Helper Python

Primeiro, verifique se o Python consegue acessar a API:

```bash
python3 day14_HELPER_querido_diario.py
```

**Esperado:**
- Deve mostrar consultas sendo feitas
- Salvar `./data/day14_querido_diario_cache.json`
- Se der erro de Cloudflare aqui também, veja Solução Alternativa abaixo

### Passo 3: Iniciar o Proxy Server

```bash
python3 day14_API_PROXY.py
```

**Output esperado:**
```
============================================================
Day 14 API Proxy Server
============================================================
Running on: http://localhost:5014
API Key: day14-local-proxy-key

Endpoints:
  GET /health
  GET /kpis?days_back=1&api_key=YOUR_KEY

Press CTRL+C to stop
============================================================
```

**Deixe rodando em uma janela de terminal!**

### Passo 4: Modificar o Workflow n8n

Agora vamos fazer o n8n chamar seu servidor local em vez da API direta.

#### No n8n:

1. **Delete/Disable esses nós:**
   - "Prepare API Queries"
   - "Split In Batches"
   - "Query Querido Diário API"
   - "Rate Limit Delay"
   - "Aggregate Results"

2. **Adicione um único HTTP Request node** entre "Schedule Trigger" e "Calculate KPIs":

   **Configuração:**
   ```
   Name: Query Local Proxy
   Method: GET
   URL: http://localhost:5014/kpis
   Query Parameters:
     - days_back: 1
     - api_key: day14-local-proxy-key
   ```

3. **Modifique o nó "Calculate KPIs":**

   O proxy já retorna os KPIs calculados, então simplifique o código:

   ```javascript
   // O proxy já retorna tudo pronto
   const data = $json;

   // Apenas formata para o próximo nó
   return [{
     json: {
       kpis: data.kpis,
       active_cities: data.raw_data.transport ?
         Object.keys(data.raw_data.transport).filter(city =>
           data.raw_data.transport[city].total_gazettes > 0
         ) : [],
       timestamp: data.kpis.timestamp,
       date_since: data.date_range.since,
       date_until: data.date_range.until,
       trend_insight: data.kpis.new_regulations > 10
         ? 'Alta atividade regulatória detectada'
         : 'Atividade regulatória normal',
       highlight_insight: `${data.kpis.active_municipalities} município(s) com novas publicações`,
       attention_insight: data.kpis.safety_incidents > 5
         ? 'Aumento em menções de segurança viária'
         : 'Padrão normal de segurança',
       top_topics: [],
       days_monitored: 1
     }
   }];
   ```

4. **Conecte:**
   ```
   Schedule Trigger → Query Local Proxy → Calculate KPIs → Build HTML Email → ...
   ```

### Passo 5: Testar

1. **Com o proxy rodando**, execute o workflow manualmente no n8n
2. Verifique se o email chega
3. Verifique os KPIs

---

## 🔄 Workflow Simplificado (Arquitetura Nova)

```
Schedule Trigger (8:00 daily)
   ↓
Query Local Proxy (http://localhost:5014/kpis)
   ↓
Calculate KPIs (simplificado - só formata)
   ↓
Build HTML Email
   ↓
Send Email
   ↓
Log Success

ERROR PATH:
Error Trigger → Send Error Email
```

---

## 🚀 Para Produção

### Opção 1: Manter Proxy Rodando

**Vantagem:** Simples, funciona

**Desvantagem:** Precisa manter `python3 day14_API_PROXY.py` rodando sempre

**Como:**
```bash
# Terminal 1: Proxy
cd day14
python3 day14_API_PROXY.py

# Terminal 2: n8n (se local)
n8n start
```

### Opção 2: Usar `nohup` para Background

```bash
cd day14
nohup python3 day14_API_PROXY.py > logs/proxy.log 2>&1 &

# Ver logs
tail -f logs/proxy.log

# Parar depois
ps aux | grep day14_API_PROXY
kill [PID]
```

### Opção 3: Systemd Service (Linux)

Criar `/etc/systemd/system/day14-proxy.service`:

```ini
[Unit]
Description=Day 14 Transport KPIs API Proxy
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/caminho/para/day14
ExecStart=/usr/bin/python3 day14_API_PROXY.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable day14-proxy
sudo systemctl start day14-proxy
sudo systemctl status day14-proxy
```

---

## 🔧 Solução Alternativa: Se Python TAMBÉM For Bloqueado

Se `day14_HELPER_querido_diario.py` também receber Cloudflare block:

### Use Synthetic Data (Para Demonstração)

1. **Crie dados sintéticos:**

```bash
cd day14
cat > data/day14_querido_diario_cache.json << 'EOF'
{
  "kpis": {
    "new_regulations": 12,
    "active_municipalities": 5,
    "compliance_mentions": 18,
    "safety_incidents": 9,
    "timestamp": "2025-12-15T08:00:00",
    "cities_monitored": 10
  },
  "date_range": {
    "since": "2025-12-14",
    "until": "2025-12-15"
  },
  "raw_data": {
    "transport": {
      "São Paulo": {"total_gazettes": 3},
      "Rio de Janeiro": {"total_gazettes": 2},
      "Brasília": {"total_gazettes": 4},
      "Salvador": {"total_gazettes": 1},
      "Fortaleza": {"total_gazettes": 2}
    }
  }
}
EOF
```

2. **Modifique o proxy para servir dados estáticos:**

```python
# No day14_API_PROXY.py, substitua o endpoint /kpis:

import json

@app.route('/kpis', methods=['GET'])
def get_kpis():
    # Serve cached/synthetic data
    with open('./data/day14_querido_diario_cache.json', 'r') as f:
        result = json.load(f)

    # Update timestamp to now
    from datetime import datetime
    result['kpis']['timestamp'] = datetime.now().isoformat()

    return jsonify(result)
```

**Use isso para demonstração do portfolio!** Documente que:
- Sistema pronto para produção
- Cloudflare bloqueando acesso automatizado
- Dados sintéticos baseados em estrutura real da API

---

## 📊 Monitoramento do Proxy

### Health Check

```bash
curl http://localhost:5014/health
```

Resposta esperada:
```json
{"status":"ok","service":"day14-api-proxy"}
```

### Testar KPIs

```bash
curl "http://localhost:5014/kpis?days_back=1&api_key=day14-local-proxy-key"
```

---

## ⚠️ Troubleshooting

### Erro: "Connection refused" no n8n

**Problema:** Proxy não está rodando

**Solução:**
```bash
cd day14
python3 day14_API_PROXY.py
```

### Erro: "Port 5014 already in use"

**Solução:**
```bash
# Ver o que está usando a porta
lsof -i :5014

# Matar o processo
kill [PID]

# Ou use outra porta no código
```

### Proxy recebe requisições mas retorna erro

**Verifique logs do proxy** - ele mostra cada requisição e erro

---

## ✅ Checklist

- [ ] Instalou dependências (`pip install -r day14_requirements.txt`)
- [ ] Testou helper Python diretamente
- [ ] Iniciou proxy server (`python3 day14_API_PROXY.py`)
- [ ] Health check passou (`curl localhost:5014/health`)
- [ ] Modificou workflow n8n para usar localhost
- [ ] Testou workflow com proxy
- [ ] Email recebido com sucesso
- [ ] Decidiu estratégia de produção (nohup/systemd/manual)

---

**Próximos passos:** Depois que funcionar, capture screenshots e documente no README que o sistema usa um proxy local para contornar proteção Cloudflare.
