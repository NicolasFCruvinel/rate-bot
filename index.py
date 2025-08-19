import requests
import logging
import asyncio
import os
import json
import threading
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

# Verifica se as variáveis de ambiente estão configuradas
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN não foi configurado. Verifique o arquivo .env")
if not CHAT_ID:
    raise ValueError("CHAT_ID não foi configurado. Verifique o arquivo .env")

# Configura o logging para ver o que está acontecendo
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Variáveis globais para armazenar histórico
historico_cotacoes = []
alertas_ativos = []

# --- SERVIDOR WEB PARA MANTER ATIVO NO REPLIT ---
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🤖 Bot de Cotação USD-BRL</h1>
    <p><strong>Status:</strong> ✅ Online e funcionando!</p>
    <p><strong>Alertas ativos:</strong> {}</p>
    <p><strong>Última verificação:</strong> {}</p>
    <p><strong>Bot do Telegram:</strong> @rateNotificator3000_bot</p>
    """.format(
        len(alertas_ativos),
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    )

@app.route('/status')
def status():
    return {
        "status": "online",
        "alertas_ativos": len(alertas_ativos),
        "ultima_verificacao": datetime.now().isoformat(),
        "historico_cotacoes": len(historico_cotacoes)
    }

def run_flask():
    """Executa o servidor Flask em uma thread separada."""
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

# --- FUNÇÕES AUXILIARES ---

def carregar_alertas():
    """Carrega os alertas salvos do arquivo JSON."""
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
    """Salva os alertas no arquivo JSON."""
    try:
        with open(ALERTAS_FILE, 'w') as f:
            json.dump(alertas_ativos, f, indent=2)
        logging.info(f"Alertas salvos: {len(alertas_ativos)} alertas ativos")
    except Exception as e:
        logging.error(f"Erro ao salvar alertas: {e}")

def obter_tendencia(cotacao_atual):
    """Analisa a tendência baseada no histórico de cotações."""
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
    """Verifica se algum alerta foi atingido."""
    alertas_disparados = []
    for alerta in alertas_ativos[:]:  # Cria uma cópia da lista
        valor_alerta = alerta['valor']
        tipo = alerta['tipo']
        
        if (tipo == 'acima' and cotacao_atual >= valor_alerta) or \
           (tipo == 'abaixo' and cotacao_atual <= valor_alerta):
            alertas_disparados.append(alerta)
            alertas_ativos.remove(alerta)  # Remove o alerta após disparar
    
    if alertas_disparados:
        salvar_alertas()  # Salva após remover alertas disparados
    
    return alertas_disparados

# --- FUNÇÕES DO BOT ---

def buscar_cotacao_atual():
    """Busca a cotação mais recente na API e a retorna como um float."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        dados = response.json()
        cotacao_str = dados['USDBRL']['bid']
        cotacao = float(cotacao_str)
        
        # Adiciona ao histórico
        historico_cotacoes.append({
            'valor': cotacao,
            'timestamp': datetime.now().isoformat()
        })
        
        # Mantém apenas as últimas 10 cotações no histórico
        if len(historico_cotacoes) > 10:
            historico_cotacoes.pop(0)
        
        return cotacao
    except Exception as e:
        logging.error(f"Erro ao buscar cotação: {e}")
        return None

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start."""
    mensagem = """🤖 *Bot de Cotação USD-BRL*

Comandos disponíveis:

💰 `/cotacao` - Ver cotação atual com tendência
🔔 `/alerta <valor> <tipo>` - Criar alerta (ex: /alerta 5.20 acima)
📋 `/listar` - Ver todos os alertas ativos
🗑️ `/remover <número>` - Remover alerta por número
❌ `/limpar` - Remover todos os alertas

*Tipos de alerta:*
• `acima` - Alerta quando cotação subir acima do valor
• `abaixo` - Alerta quando cotação descer abaixo do valor

O bot também envia notificações automáticas a cada 30 minutos quando há mudanças! 📈📉"""
    
    await update.message.reply_text(mensagem, parse_mode='Markdown')

async def comando_cotacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Busca e envia a cotação atual quando o comando /cotacao é enviado."""
    logging.info("Comando /cotacao recebido.")
    cotacao = buscar_cotacao_atual()
    if cotacao:
        emoji_tendencia, texto_tendencia = obter_tendencia(cotacao)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        mensagem = f"""💵 *Cotação USD-BRL Atual*

{emoji_tendencia} *R$ {cotacao:.4f}*
📊 {texto_tendencia}
🕒 Atualizado às {timestamp}"""
        
        await update.message.reply_text(mensagem, parse_mode='Markdown')
    else:
        await update.message.reply_text('Desculpe, não consegui buscar a cotação no momento.')

async def comando_alerta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cria um novo alerta de preço."""
    try:
        if len(context.args) != 2:
            await update.message.reply_text(
                "❌ Uso correto: `/alerta <valor> <tipo>`\n"
                "Exemplo: `/alerta 5.20 acima` ou `/alerta 5.10 abaixo`",
                parse_mode='Markdown'
            )
            return
        
        valor_str, tipo = context.args
        valor = float(valor_str.replace(',', '.'))
        
        if tipo not in ['acima', 'abaixo']:
            await update.message.reply_text("❌ Tipo deve ser 'acima' ou 'abaixo'")
            return
        
        # Verifica se já existe um alerta igual
        for alerta in alertas_ativos:
            if alerta['valor'] == valor and alerta['tipo'] == tipo:
                await update.message.reply_text(f"⚠️ Já existe um alerta para R$ {valor:.4f} {tipo}")
                return
        
        # Adiciona o novo alerta
        novo_alerta = {
            'valor': valor,
            'tipo': tipo,
            'criado_em': datetime.now().isoformat()
        }
        alertas_ativos.append(novo_alerta)
        salvar_alertas()
        
        emoji = "📈" if tipo == "acima" else "📉"
        await update.message.reply_text(
            f"✅ Alerta criado!\n{emoji} Você será notificado quando a cotação ficar *{tipo} de R$ {valor:.4f}*",
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text("❌ Valor inválido. Use números como 5.20 ou 5,15")
    except Exception as e:
        logging.error(f"Erro no comando alerta: {e}")
        await update.message.reply_text("❌ Erro ao criar alerta. Tente novamente.")

async def comando_listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista todos os alertas ativos."""
    if not alertas_ativos:
        await update.message.reply_text("📋 Nenhum alerta ativo no momento.")
        return
    
    mensagem = "📋 *Seus Alertas Ativos:*\n\n"
    for i, alerta in enumerate(alertas_ativos, 1):
        emoji = "📈" if alerta['tipo'] == "acima" else "📉"
        data_criacao = datetime.fromisoformat(alerta['criado_em']).strftime("%d/%m %H:%M")
        mensagem += f"{i}. {emoji} R$ {alerta['valor']:.4f} ({alerta['tipo']}) - {data_criacao}\n"
    
    mensagem += f"\nTotal: {len(alertas_ativos)} alertas"
    await update.message.reply_text(mensagem, parse_mode='Markdown')

async def comando_remover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove um alerta específico pelo número."""
    try:
        if len(context.args) != 1:
            await update.message.reply_text("❌ Uso: `/remover <número>`\nUse `/listar` para ver os números", parse_mode='Markdown')
            return
        
        numero = int(context.args[0])
        
        if numero < 1 or numero > len(alertas_ativos):
            await update.message.reply_text(f"❌ Número inválido. Use um número entre 1 e {len(alertas_ativos)}")
            return
        
        alerta_removido = alertas_ativos.pop(numero - 1)
        salvar_alertas()
        
        emoji = "📈" if alerta_removido['tipo'] == "acima" else "📉"
        await update.message.reply_text(
            f"🗑️ Alerta removido!\n{emoji} R$ {alerta_removido['valor']:.4f} ({alerta_removido['tipo']})"
        )
        
    except ValueError:
        await update.message.reply_text("❌ Digite um número válido")
    except Exception as e:
        logging.error(f"Erro no comando remover: {e}")
        await update.message.reply_text("❌ Erro ao remover alerta")

async def comando_limpar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove todos os alertas."""
    if not alertas_ativos:
        await update.message.reply_text("📋 Nenhum alerta para remover.")
        return
    
    quantidade = len(alertas_ativos)
    alertas_ativos.clear()
    salvar_alertas()
    
    await update.message.reply_text(f"🗑️ Todos os {quantidade} alertas foram removidos!")

async def notificar_mudanca(context: ContextTypes.DEFAULT_TYPE):
    """Função que roda em segundo plano para checar e notificar mudanças."""
    cotacao_atual = buscar_cotacao_atual()
    
    if not cotacao_atual:
        logging.error("Não foi possível buscar cotação para verificação")
        return
    
    # Verifica se houve mudança significativa na cotação
    mudanca_detectada = False
    if len(historico_cotacoes) >= 2:
        cotacao_anterior = historico_cotacoes[-2]['valor']
        diferenca_percentual = abs((cotacao_atual - cotacao_anterior) / cotacao_anterior) * 100
        
        # Só notifica se a mudança for maior que 0.1%
        if diferenca_percentual >= 0.1:
            mudanca_detectada = True
    
    # Verifica alertas personalizados
    alertas_disparados = verificar_alertas(cotacao_atual)
    
    # Envia notificações se necessário
    if mudanca_detectada or alertas_disparados:
        emoji_tendencia, texto_tendencia = obter_tendencia(cotacao_atual)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        mensagem = f"⚠️ *Alerta de Câmbio USD-BRL*\n\n"
        mensagem += f"{emoji_tendencia} *R$ {cotacao_atual:.4f}*\n"
        mensagem += f"📊 {texto_tendencia}\n"
        mensagem += f"🕒 {timestamp}\n"
        
        if alertas_disparados:
            mensagem += f"\n🔔 *Alertas Ativados:*\n"
            for alerta in alertas_disparados:
                emoji = "📈" if alerta['tipo'] == "acima" else "📉"
                mensagem += f"{emoji} R$ {alerta['valor']:.4f} ({alerta['tipo']})\n"
        
        await context.bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode='Markdown')
        logging.info(f"Notificação enviada - Cotação: R$ {cotacao_atual:.4f}")
    else:
        logging.info(f"Cotação estável: R$ {cotacao_atual:.4f} - Nenhuma notificação enviada")

def main():
    """Inicia o bot e configura os handlers."""
    # Carrega os alertas salvos
    carregar_alertas()
    
    # Inicia o servidor Flask em uma thread separada (para Replit)
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logging.info("🌐 Servidor web iniciado na porta 8080")
    
    # Cria a aplicação do bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Adiciona os handlers para os comandos
    application.add_handler(CommandHandler("start", comando_start))
    application.add_handler(CommandHandler("cotacao", comando_cotacao))
    application.add_handler(CommandHandler("alerta", comando_alerta))
    application.add_handler(CommandHandler("listar", comando_listar))
    application.add_handler(CommandHandler("remover", comando_remover))
    application.add_handler(CommandHandler("limpar", comando_limpar))

    # Configura o menu de comandos do Telegram
    comandos = [
        BotCommand("start", "Ver lista de comandos"),
        BotCommand("cotacao", "Ver cotação atual com tendência"),
        BotCommand("alerta", "Criar alerta personalizado"),
        BotCommand("listar", "Ver alertas ativos"),
        BotCommand("remover", "Remover alerta específico"),
        BotCommand("limpar", "Remover todos os alertas")
    ]
    
    async def configurar_comandos(app):
        await app.bot.set_my_commands(comandos)
        logging.info("Menu de comandos configurado no Telegram")
    
    # Configura os comandos após inicializar
    application.post_init = configurar_comandos

    # Configura a tarefa repetitiva para as notificações (a cada 30 minutos)
    job_queue = application.job_queue
    job_queue.run_repeating(notificar_mudanca, interval=1800, first=10)  # 1800s = 30min

    # Inicia o bot
    logging.info("🤖 Bot de Cotação USD-BRL iniciado!")
    logging.info(f"📊 {len(alertas_ativos)} alertas carregados")
    application.run_polling()

if __name__ == '__main__':
    main()