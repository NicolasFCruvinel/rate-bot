# 🚀 GUIA COMPLETO: Deploy do Bot no Replit

## 📋 **Passo a Passo para Deploy Gratuito**

### **1. Preparar os arquivos**
✅ Todos os arquivos já estão prontos nesta pasta:
- `index.py` - Código principal do bot
- `requirements.txt` - Dependências Python
- `.replit` - Configuração do Replit
- `replit.nix` - Ambiente de execução
- `README_REPLIT.md` - Documentação

### **2. Fazer upload para o Replit**

**Opção A - GitHub (Recomendado):**
1. Crie um repositório no GitHub
2. Faça upload de todos os arquivos desta pasta
3. No Replit, clique em "Create Repl" → "Import from GitHub"
4. Cole a URL do seu repositório

**Opção B - Upload direto:**
1. Vá para [replit.com](https://replit.com)
2. Clique em "Create Repl" → "Python"
3. Faça upload de todos os arquivos desta pasta

### **3. Configurar variáveis de ambiente**

No Replit, clique em 🔒 **"Secrets"** e adicione:

```
TELEGRAM_TOKEN = 1234567890:ABCdefGHI...  (seu token do @BotFather)
CHAT_ID = 123456789  (seu ID do @userinfobot)
```

### **4. Executar**
Clique em **"Run"** e pronto! 🎉

## 🔧 **Recursos incluídos:**

✅ **Bot Telegram completo** com todos os comandos
✅ **Sistema de alertas** personalizados  
✅ **Servidor web** para manter ativo 24/7
✅ **Interface de status** em `https://seu-repl.replit.app`
✅ **Persistência de dados** - alertas salvos em JSON
✅ **Notificações automáticas** a cada 30 minutos

## 🎯 **Resultado:**
Seu bot ficará rodando 24/7 de graça no Replit, monitorando a cotação USD-BRL e enviando alertas personalizados!

## 📱 **Como usar depois do deploy:**
1. Vá para o Telegram
2. Procure seu bot: `@seubot`
3. Envie `/start` para ver todos os comandos
4. Use `/alerta 5.50 acima` para criar alertas
5. Receba notificações automáticas!
