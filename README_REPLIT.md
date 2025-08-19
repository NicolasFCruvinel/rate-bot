# 🤖 Bot de Cotação USD-BRL para Telegram

Bot que monitora a cotação do dólar americano (USD) para real brasileiro (BRL) e envia notificações automáticas via Telegram.

## 🚀 Deploy no Replit

### 1. Configuração Inicial

1. **Faça fork deste projeto no Replit**
2. **Configure as variáveis de ambiente** no painel "Secrets":
   - `TELEGRAM_TOKEN`: Token do seu bot (obtido com @BotFather)
   - `CHAT_ID`: Seu ID de usuário do Telegram

### 2. Como obter as credenciais

**Token do Bot:**
1. Vá para [@BotFather](https://t.me/botfather) no Telegram
2. Envie `/newbot` e siga as instruções
3. Copie o token que ele te enviar

**Chat ID:**
1. Vá para [@userinfobot](https://t.me/userinfobot) no Telegram  
2. Envie `/start`
3. Copie o número que aparece como "Id"

### 3. Configurar as variáveis no Replit

1. No Replit, clique em **"Secrets"** (🔒) no painel lateral
2. Adicione:
   - Key: `TELEGRAM_TOKEN` | Value: seu token do bot
   - Key: `CHAT_ID` | Value: seu chat id

### 4. Executar

Clique em **"Run"** e pronto! Seu bot estará rodando 24/7.

## 📱 Comandos do Bot

- `/start` - Ver lista de comandos
- `/cotacao` - Ver cotação atual com tendência
- `/alerta <valor> <tipo>` - Criar alerta (ex: /alerta 5.50 acima)
- `/listar` - Ver alertas ativos
- `/remover <número>` - Remover alerta específico
- `/limpar` - Remover todos os alertas

## 🔧 Funcionalidades

✅ **Cotação em tempo real** com indicação de tendência (📈📉)
✅ **Alertas personalizados** - defina valores para ser notificado
✅ **Notificações automáticas** a cada 30 minutos quando há mudanças
✅ **Persistência de dados** - alertas são salvos mesmo se reiniciar
✅ **Menu de comandos** integrado ao Telegram
✅ **Deploy gratuito** no Replit com uptime 24/7

## 🌐 Status Web

O bot inclui uma interface web simples para monitoramento:
- `https://seu-repl.replit.app/` - Status geral
- `https://seu-repl.replit.app/status` - Status em JSON

## ⚡ Manter sempre ativo

O bot inclui um servidor web que mantém o Repl sempre ativo, evitando que ele "durma" após inatividade.
