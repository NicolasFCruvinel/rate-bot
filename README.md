# Bot de Notificação USD-BRL para Telegram

Este bot monitora a cotação do dólar americano (USD) para real brasileiro (BRL) e envia notificações automáticas quando há mudanças na cotação.

## Funcionalidades

- **Comando `/start`**: Inicia o bot e mostra mensagem de boas-vindas
- **Comando `/cotacao`**: Mostra a cotação atual do USD-BRL
- **Notificações automáticas**: Envia alertas a cada 30 minutos quando há mudança na cotação

## Pré-requisitos

1. Python 3.8 ou superior
2. Um bot do Telegram (criado através do @BotFather)
3. Seu Chat ID do Telegram

## Configuração

### 1. Criar um bot no Telegram

1. Envie `/start` para [@BotFather](https://t.me/botfather) no Telegram
2. Envie `/newbot` e siga as instruções
3. Anote o token que o BotFather te enviar

### 2. Descobrir seu Chat ID

1. Envie `/start` para [@userinfobot](https://t.me/userinfobot)
2. Anote o número que aparece como "Id"

### 3. Configurar variáveis de ambiente

1. Copie o arquivo `.env.example` para `.env`:
   ```
   cp .env.example .env
   ```

2. Edite o arquivo `.env` e preencha com seus dados:
   ```
   TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   CHAT_ID=123456789
   ```

### 4. Instalar dependências

As dependências já foram instaladas automaticamente:
- python-telegram-bot
- requests
- python-dotenv

## Como executar

Execute o script Python:
```
python index.py
```

O bot ficará rodando e:
- Responderá aos comandos `/start` e `/cotacao`
- Enviará notificações automáticas a cada 30 minutos quando houver mudança na cotação

## Comandos disponíveis

- `/start` - Inicia o bot e mostra mensagem de boas-vindas
- `/cotacao` - Mostra a cotação atual do USD-BRL

## Personalização

Você pode alterar algumas configurações no código:

- **Intervalo das notificações**: Altere o valor `1800` (30 minutos) na linha do `job_queue.run_repeating()`
- **API de cotação**: O bot usa a API da AwesomeAPI, mas você pode trocar por outra se necessário

## Troubleshooting

### Erro: "TELEGRAM_TOKEN não foi configurado"
- Verifique se o arquivo `.env` existe e contém o token correto

### Erro: "CHAT_ID não foi configurado"
- Verifique se o arquivo `.env` contém seu Chat ID correto

### Bot não responde
- Verifique se o token está correto
- Certifique-se de que iniciou uma conversa com o bot no Telegram (envie `/start`)

### Notificações não chegam
- Verifique se o Chat ID está correto
- Certifique-se de que o bot tem permissão para enviar mensagens
