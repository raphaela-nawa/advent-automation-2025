# Guia Rápido: Importar Workflow n8n

## 📥 Como Importar o Workflow

### Passo 1: Acesse seu n8n

**Opção A - n8n Cloud:**
1. Acesse [n8n.cloud](https://n8n.cloud)
2. Faça login na sua conta

**Opção B - n8n Local:**
1. Inicie o n8n: `n8n start` ou `docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n`
2. Acesse: http://localhost:5678

---

### Passo 2: Importar o Workflow

1. **Clique no botão "+" (New Workflow)** no canto superior esquerdo

2. **Abra o menu de opções:**
   - Clique nos "..." (três pontos) no canto superior direito
   - Selecione **"Import from File"**

3. **Selecione o arquivo:**
   - Navegue até: `day14/workflows/day14_transport_kpi_workflow.json`
   - Clique em "Open/Abrir"

4. **Workflow importado!**
   - Você verá 12 nós conectados no canvas
   - O workflow ainda estará **inativo** (não vai executar automaticamente ainda)

---

### Passo 3: Configurar SMTP (Obrigatório)

O workflow precisa de credenciais SMTP para enviar emails.

#### Para Gmail (Recomendado):

1. **Gerar App Password:**
   - Acesse: https://myaccount.google.com/apppasswords
   - Crie uma senha de app para "Mail"
   - **Copie a senha gerada** (16 caracteres)

2. **No n8n, clique no nó "Send Email":**
   - Clique em "Create New Credential"
   - Preencha:
     - **User:** seu-email@gmail.com
     - **Password:** [cole a senha de app de 16 caracteres]
     - **Host:** smtp.gmail.com
     - **Port:** 587
     - **SSL/TLS:** Enable
   - Clique em "Save"

3. **Repita para o nó "Send Error Email":**
   - Selecione a mesma credencial criada

#### Para Outros Provedores:

| Provedor | Host | Porta | SSL/TLS |
|----------|------|-------|---------|
| **Outlook/Hotmail** | smtp-mail.outlook.com | 587 | TLS |
| **Yahoo** | smtp.mail.yahoo.com | 465 | SSL |
| **SendGrid** | smtp.sendgrid.net | 587 | TLS |
| **Amazon SES** | email-smtp.us-east-1.amazonaws.com | 587 | TLS |

---

### Passo 4: Configurar Destinatários

#### Opção A - Via Variáveis de Ambiente (Recomendado):

1. **No n8n, vá em Settings > Environment Variables**
2. **Adicione:**
   ```
   DAY14_SENDER_EMAIL=seu-email@gmail.com
   DAY14_RECIPIENT_EMAILS=destinatario1@example.com,destinatario2@example.com
   ```

#### Opção B - Editar Diretamente no Workflow:

1. **Clique no nó "Send Email"**
2. **No campo "To Email", substitua:**
   - De: `={{ $env.DAY14_RECIPIENT_EMAILS || 'your-email@example.com' }}`
   - Para: `seu-email@example.com`
3. **Repita para "Send Error Email"**

---

### Passo 5: Testar o Workflow

**IMPORTANTE:** Teste antes de ativar o agendamento!

1. **Clique em "Execute Workflow"** (botão no canto superior direito)

2. **Aguarde a execução:**
   - Vai demorar ~30-60 segundos (10 cidades × 1 segundo de delay)
   - Você verá cada nó ficando verde conforme executa

3. **Verifique os resultados:**

   **a) Clique no nó "Calculate KPIs":**
   ```json
   {
     "kpis": {
       "new_regulations": 5,
       "active_municipalities": 3,
       "compliance_mentions": 12,
       "safety_incidents": 7
     }
   }
   ```
   ✅ Se você ver esses campos, a API está funcionando!

   **b) Clique no nó "Build HTML Email":**
   - Verifique se `html_body` contém HTML completo
   - Verifique se `subject` está formatado

   **c) Clique no nó "Send Email":**
   - Se executou sem erro, o email foi enviado!

4. **Verifique seu email:**
   - Cheque a caixa de entrada (e spam!)
   - Abra o email e verifique se está bem formatado

---

### Passo 6: Revisar e Ajustar (Opcional)

#### Ajustar Horário do Agendamento:

1. **Clique no nó "Schedule Trigger"**
2. **Modifique a "Cron Expression":**
   - `0 8 * * *` = Todos os dias às 8:00
   - `0 8 * * 1-5` = Segunda a sexta às 8:00
   - `0 8,18 * * *` = 8:00 e 18:00 todos os dias
   - `0 */6 * * *` = A cada 6 horas

3. **Ajuste o Timezone se necessário:**
   - Padrão: UTC
   - Recomendado para Brasil: `America/Sao_Paulo`

#### Adicionar Mais Cidades:

1. **Clique no nó "Prepare API Queries"**
2. **No código JavaScript, adicione na seção `cities`:**
   ```javascript
   'Goiânia': '5208707',
   'Campinas': '3509502',
   ```
   - [Encontre códigos IBGE aqui](https://www.ibge.gov.br/explica/codigos-dos-municipios.php)

#### Modificar Palavras-Chave:

1. **No mesmo nó, modifique a array `keywords`:**
   ```javascript
   const keywords = [
     'transporte público',
     'ciclovia',
     'pedágio',
     'estacionamento rotativo'
   ];
   ```

---

### Passo 7: Ativar o Workflow

**Depois de testar com sucesso:**

1. **No canto superior direito, ative o toggle "Active"**
2. **Confirme quando solicitado**

✅ **Pronto!** O workflow vai executar automaticamente no horário agendado.

---

## 🔍 Monitoramento

### Verificar Execuções Passadas:

1. **Vá em "Executions"** (menu lateral esquerdo)
2. **Veja o histórico:**
   - ✅ Verde = Sucesso
   - ❌ Vermelho = Erro
3. **Clique em qualquer execução** para ver detalhes

### Verificar Próxima Execução:

1. **Clique no workflow ativo**
2. **No nó "Schedule Trigger":**
   - Vai mostrar "Next execution at: ..."

---

## ⚠️ Troubleshooting

### Problema: "Credential 'SMTP account' doesn't exist"

**Solução:**
1. Clique no nó "Send Email"
2. No dropdown de credentials, clique em "Create New"
3. Configure conforme Passo 3

---

### Problema: "Error: self signed certificate in certificate chain"

**Solução:**
1. Clique no nó "Send Email"
2. Em "Options", ative "Allow Unauthorized Certificates"

---

### Problema: "No gazettes found" (0 regulamentações)

**Causas possíveis:**
- Normal! Alguns dias não têm publicações
- Experimente aumentar `days_back` para 7 dias

**Solução:**
1. No nó "Prepare API Queries"
2. Mude de `yesterday.setDate(yesterday.getDate() - 1);`
3. Para: `yesterday.setDate(yesterday.getDate() - 7);`

---

### Problema: Workflow muito lento (>2 minutos)

**Solução:**
1. No nó "Split In Batches"
2. Aumente "Batch Size" de 3 para 5
3. Reduz o tempo total mas mantém rate limit seguro

---

### Problema: Email não recebido

**Checklist:**
- [ ] SMTP credentials estão corretos?
- [ ] Email de destino está correto?
- [ ] Checou a pasta de spam?
- [ ] Para Gmail: App Password foi criado?
- [ ] "Send Email" node executou sem erro?

---

## 📊 O Que Esperar

### Primeira Execução:

- **Tempo:** ~30-60 segundos
- **Resultados típicos:**
  - 0-20 novas regulamentações (varia muito por dia)
  - 2-8 municípios ativos
  - 5-30 menções de conformidade
  - 3-15 incidentes de segurança

### Execução Diária:

- **Às 8:00 (horário configurado):** Workflow inicia automaticamente
- **~1 minuto depois:** Email chega na caixa de entrada
- **Logs salvos:** Visível em "Executions"

---

## 📸 Screenshots para Documentação

Depois de testar com sucesso, capture:

1. **Canvas do workflow:**
   - Zoom out para mostrar todos os 12 nós
   - Save como: `day14/screenshots/day14_n8n_workflow_canvas.png`

2. **Email recebido:**
   - Screenshot do email no seu cliente
   - Save como: `day14/screenshots/day14_email_sample.png`

3. **Execução bem-sucedida:**
   - Screenshot da tela "Executions" com status verde
   - Save como: `day14/screenshots/day14_execution_success.png`

---

## ✅ Checklist de Validação

Antes de considerar completo:

- [ ] Workflow importado com sucesso
- [ ] SMTP credentials configuradas
- [ ] Teste manual executado (Email recebido)
- [ ] Email está bem formatado (HTML renderizado)
- [ ] KPIs calculados corretamente
- [ ] Workflow ativado
- [ ] Screenshots capturados
- [ ] Workflow JSON exportado e commitado

---

## 🎯 Próximos Passos

Depois de validar:

1. ✅ **Exportar workflow atualizado** (se fez modificações)
2. ✅ **Criar README.md** do projeto
3. ✅ **Commitar tudo** no git
4. ✅ **Atualizar status** para "Complete" no projeto

---

**Precisa de ajuda?** Consulte [N8N_WORKFLOW_SETUP.md](N8N_WORKFLOW_SETUP.md) para troubleshooting avançado.

**Dúvidas sobre a API?** Veja [Querido Diário Docs](https://docs.queridodiario.ok.org.br)
