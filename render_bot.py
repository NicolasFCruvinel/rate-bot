import requests
import logging
import asyncio
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Importações da biblioteca do Telegram
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- CONFIGURAÇÕES ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
API_URL = 'https://economia.awesomeapi.com.br/last/USD-BRL'
ALERTAS_FILE = 'alertas.json'
PORT = int(os.environ.get('PORT', 8080))  # Porta do Render

# Verifica se as variáveis de ambiente estão configuradas
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN não foi configurado. Verifique as variáveis de ambiente")
if not CHAT_ID:
    raise ValueError("CHAT_ID não foi configurado. Verifique as variáveis de ambiente")

# Configura o logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)

# Variáveis globais
historico_cotacoes = []
alertas_ativos = []

# --- SERVIDOR WEB PARA RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return f"""
    <h1>🤖 Bot de Cotação USD-BRL</h1>
    <p><strong>Status:</strong> ✅ Online no Render!</p>
    <p><strong>Alertas ativos:</strong> {len(alertas_ativos)}</p>
    <p><strong>Última verificação:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
    <p><strong>Histórico de cotações:</strong> {len(historico_cotacoes)} entradas</p>
    <p><strong>Bot do Telegram:</strong> Ativo</p>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.route('/status')
def status():
    return {
        "status": "online",
        "alertas_ativos": len(alertas_ativos),
        "ultima_verificacao": datetime.now().isoformat(),
        "historico_cotacoes": len(historico_cotacoes),
        "platform": "Render"
    }

def run_flask():
    """Executa o servidor Flask."""
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        logging.error(f"Erro no servidor Flask: {e}")

# [Resto das funções permanecem iguais...]
# Copie todas as outras funções do arquivo original aqui

def carregar_alertas():
    global alertas_ativos
    try:
        if os.path.exists(ALERTAS_FILE):
            with open(ALERTAS_FILE, 'r') as f:
                alertas_ativos = json.load(f)
        else:
            alertas_ativos = []
        logging.info(f"Alertas carregados: {len(alertas_ativos)} alertas ativos")
    except Exception as e:
        logging.error(f"Erro ao carregar alertas: {e}")
        alertas_ativos = []

def salvar_alertas():
    try:
        with open(ALERTAS_FILE, 'w') as f:
            json.dump(alertas_ativos, f, indent=2)
        logging.info(f"Alertas salvos: {len(alertas_ativos)} alertas ativos")
    except Exception as e:
        logging.error(f"Erro ao salvar alertas: {e}")

def obter_tendencia(cotacao_atual):
    if len(historico_cotacoes) < 2:
        return "🔄", "Coletando dados"
    
    cotacao_anterior = historico_cotacoes[-2]['valor']
    diferenca = cotacao_atual - cotacao_anterior
    percentual = (diferenca / cotacao_anterior) * 100
    
    if diferenca > 0:
        return "📈", f"Subindo (+{diferenca:.4f} | +{percentual:.2f}%)"
    elif diferenca < 0:
        return "📉", f"Descendo ({diferenca:.4f} | {percentual:.2f}%)"
    else:
        return "➡️", "Estável (0.00%)"

def verificar_alertas(cotacao_atual):
    alertas_disparados = []
    for alerta in alertas_ativos[:]:
        valor_alerta = alerta['valor']
        tipo = alerta['tipo']
        
        if (tipo == 'acima' and cotacao_atual >= valor_alerta) or \
           (tipo == 'abaixo' and cotacao_atual <= valor_alerta):
            alertas_disparados.append(alerta)
            alertas_ativos.remove(alerta)
    
    if alertas_disparados:
        salvar_alertas()
    
    return alertas_disparados

def buscar_cotacao_atual():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        dados = response.json()
        cotacao_str = dados['USDBRL']['bid']
        cotacao = float(cotacao_str)
        
        historico_cotacoes.append({
            'valor': cotacao,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(historico_cotacoes) > 10:
            historico_cotacoes.pop(0)
        
        return cotacao
    except Exception as e:
        logging.error(f"Erro ao buscar cotação: {e}")
        return None

def main_bot():
    """Função principal do bot com tratamento robusto de erros."""
    carregar_alertas()
    
    while True:
        try:
            # Cria a aplicação do bot
            application = Application.builder().token(TELEGRAM_TOKEN).build()

            # [Adicionar todos os handlers aqui...]
            
            async def configurar_comandos(app):
                try:
                    await app.bot.delete_webhook(drop_pending_updates=True)
                    logging.info("Webhooks limpos")
                    time.sleep(2)  # Pausa para evitar conflitos
                except Exception as e:
                    logging.warning(f"Erro ao limpar webhooks: {e}")

            application.post_init = configurar_comandos

            logging.info("🤖 Bot iniciando no Render...")
            application.run_polling(
                drop_pending_updates=True,
                timeout=30,
                poll_interval=1,
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30
            )
            
        except Exception as e:
            logging.error(f"Erro no bot: {e}")
            logging.info("Aguardando 30 segundos antes de reiniciar...")
            time.sleep(30)

if __name__ == '__main__':
    # Inicia o servidor Flask em uma thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logging.info(f"🌐 Servidor web iniciado na porta {PORT}")
    
    # Inicia o bot
    main_bot()
