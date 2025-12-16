a# Day 14: Quick Start - 2 Opções ⚡

## ⭐ OPÇÃO 1: Python (RECOMENDADO - 3 minutos)

### Por Que Python?
- ✅ **Funciona de primeira** - Sem erros de loop/contexto
- ✅ **Setup super rápido** - 3 minutos
- ✅ **Fácil de debugar** - Logs claros

### Setup:

```bash
cd day14

# 1. Configure SMTP
cp .env.example .env
nano .env  # Preencha SMTP_USER, SMTP_PASSWORD, SMTP_TO

# 2. Execute
python3 day14_MAIN_automation.py
```

**Resultado:** Email profissional com KPIs em 20 segundos! 📧

📖 **Guia completo:** [SETUP_PYTHON.md](SETUP_PYTHON.md)

---

## 🔧 OPÇÃO 2: n8n (Mais complexo)

### Por Que n8n?
- 🎨 Interface visual
- 🔗 Integrações built-in
- ⚠️ Requer troubleshooting de loops

### Arquivos Disponíveis:

1. **day14_FINAL_WORKING.json** (última versão, usa Merge node)
2. **day14_transport_kpi_workflow_v5_simplified.json** (versão simplificada)

### Setup:

1. Importe JSON no n8n
2. Configure SMTP
3. Conecte loops conforme guia
4. Teste execução

📖 **Guia completo:** [SETUP_DIRECT_API_WORKFLOW_V4.md](SETUP_DIRECT_API_WORKFLOW_V4.md)

---

## 🎯 Recomendação

**Use Python!** É mais simples, robusto e funciona de primeira.

n8n é ótimo para workflows visuais, mas para este caso específico,
Python é a melhor escolha.

---

## 📊 O Que Você Vai Receber

Email HTML profissional com:

```
🚦 Transport KPI Report
Brazilian Municipal Regulations
2025-11-15 to 2025-12-15 (30 days)

┌─────────────────────┬──────────────────────┐
│ New Regulations     │ Active Municipalities│
│       95            │         5            │
├─────────────────────┼──────────────────────┤
│ Compliance Mentions │ Safety Incidents     │
│      159            │        15            │
└─────────────────────┴──────────────────────┘

📍 Active Municipalities
[Curitiba (24)] [Sao Paulo (21)] [Rio (18)] ...

💡 Key Insights
• 📈 Volume alto de regulamentações publicadas
• 🌟 Atividade distribuída em múltiplos municípios
• ✅ 159 menção(ões) a conformidade
```

---

## ⚡ Start Agora!

```bash
cd day14
python3 day14_MAIN_automation.py
```

Só isso! 🚀
