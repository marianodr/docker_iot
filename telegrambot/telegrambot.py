from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio, ssl, logging, os, aiomqtt, json, traceback

token = os.environ["TB_TOKEN"]
STICKER_START = "CAACAgIAAxkBAAIB42ZX2Ri2wmFd0430YZNXSnCOKf6rAAK6DwACAsSYSq3W9HdybYh3NQQ"
STICKER_ACERCADE = "CAACAgIAAxkBAAIB12ZX1H9-3x9Ha4-DXOEZK_TQVxIfAAKADgAC1HUJSsyDDgHMdYipNQQ"
STICKER_ERROR = "CAACAgIAAxkBAAIB5GZX2Wt0YPCeN-Zgk6qSKPwD4VrNAAK4DgACUQ45Sy5O5q5mnAqSNQQ"

logging.basicConfig(format='%(asctime)s - TelegramBot - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("se conectó: " + str(update.message.from_user.id))
    if update.message.from_user.first_name:
        nombre = update.message.from_user.first_name
    else:
        nombre = ""
    if update.message.from_user.last_name:
        apellido = update.message.from_user.last_name
    else:
        apellido = ""
    kb = [["destello"], ["modo"], ["rele"]]
    await context.bot.send_message(update.message.chat.id,
                                   text="Bienvenido al Bot " + nombre + " " + apellido,
                                   reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    
    await context.bot.send_animation(update.message.chat.id, STICKER_START) 

async def acercade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.message.chat.id, text="Este bot permite controlar el Termostato")
    await context.bot.send_animation(update.message.chat.id, STICKER_ACERCADE)

async def destello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(context.args)
    await context.bot.send_message(update.message.chat.id, text="✨ Destellando...")
    
    topic='destello'
    data = {"destello": 1}
    # Convertir el diccionario a JSON
    json_data = json.dumps(data)

    await publicar(topic, json_data)

async def setpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(context.args)
    if context.args and context.args[0].startswith('@'):
        try:
            setpoint_value = int(context.args[0][1:])
            await context.bot.send_message(update.message.chat.id, text=f"Setpoint establecido a {setpoint_value}")
            
            topic = 'setpoint'
            data = {"setpoint": setpoint_value}
            # Convertir el diccionario a JSON
            json_data = json.dumps(data)

            await publicar(topic, json_data)
        except ValueError:
            await context.bot.send_message(update.message.chat.id, text="Error: El setpoint debe ser un número entero.")
            await context.bot.send_animation(update.message.chat.id, STICKER_ERROR)
    else:
        await context.bot.send_message(update.message.chat.id, text="Error: Debe proporcionar un valor para el setpoint usando el formato @<número>.")
        await context.bot.send_animation(update.message.chat.id, STICKER_ERROR)

async def periodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(context.args)
    if context.args and context.args[0].startswith('@'):
        try:
            periodo_value = int(context.args[0][1:])
            await context.bot.send_message(update.message.chat.id, text=f"Periodo establecido a {periodo_value} segundos")
            
            topic = 'periodo'
            data = {"periodo": periodo_value}
            json_data = json.dumps(data)

            await publicar(topic, json_data)
        except ValueError:
            await context.bot.send_message(update.message.chat.id, text="Error: El periodo debe ser un número entero.")
            await context.bot.send_animation(update.message.chat.id, STICKER_ERROR)
    else:
        await context.bot.send_message(update.message.chat.id, text="Error: Debe proporcionar un valor para el periodo usando el formato @<número>.")
        await context.bot.send_animation(update.message.chat.id, STICKER_ERROR)


async def modo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(context.args)
    kb = [["manual"], ["automatico"], ["volver"]]
    await context.bot.send_message(update.message.chat.id,
                                   text="Elige el modo:",
                                   reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def modo_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.message.chat.id, text="Modo manual seleccionado")
    
    topic='modo'
    data = {"modo": "manual"}
    # Convertir el diccionario a JSON
    json_data = json.dumps(data)

    await publicar(topic, json_data)


async def modo_automatico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.message.chat.id, text="Modo automático seleccionado")
    
    topic='modo'
    data = {"modo": "automatico"}
    # Convertir el diccionario a JSON
    json_data = json.dumps(data)

    await publicar(topic, json_data)

async def rele(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(context.args)
    kb = [["on"], ["off"], ["volver"]]
    await context.bot.send_message(update.message.chat.id,
                                   text="Control del rele:",
                                   reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def rele_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.message.chat.id, text="Rele encendido")
    
    topic='rele'
    data = {"rele": 1}
    # Convertir el diccionario a JSON
    json_data = json.dumps(data)

    await publicar(topic, json_data)

async def rele_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.message.chat.id, text="Rele apagado")
    
    topic='rele'
    data = {"rele": 0}
    # Convertir el diccionario a JSON
    json_data = json.dumps(data)

    await publicar(topic, json_data)

async def volver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["destello"], ["modo"], ["rele"]]
    await context.bot.send_message(update.message.chat.id,
                                   text="Volviendo al menú principal",
                                   reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def publicar(topic, dato):

    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    try:
        async with aiomqtt.Client(
            os.environ["SERVIDOR"],
            username=os.environ["MQTT_USR"],
            password=os.environ["MQTT_PASS"],
            port=int(os.environ["PUERTO_MQTTS"]),
            tls_context=tls_context
        ) as client:
            await client.publish(f'iot2024/mdr/{topic}', dato, qos=1)
        return True
    except ConnectionError as e:
        logging.info(e)
        return False

def main():
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('acercade', acercade))
    application.add_handler(CommandHandler('destello', destello))
    application.add_handler(CommandHandler('setpoint', setpoint))
    application.add_handler(CommandHandler('periodo', periodo))
    application.add_handler(CommandHandler('modo', modo))         # Falta configurar por parametros
    application.add_handler(CommandHandler('rele', rele))         # Falta configurar por parametros
    application.add_handler(MessageHandler(filters.Regex(r'^destello$'), destello))
    application.add_handler(MessageHandler(filters.Regex(r'^modo$'), modo))
    application.add_handler(MessageHandler(filters.Regex(r'^manual$'), modo_manual))
    application.add_handler(MessageHandler(filters.Regex(r'^automatico$'), modo_automatico))
    application.add_handler(MessageHandler(filters.Regex(r'^rele$'), rele))
    application.add_handler(MessageHandler(filters.Regex(r'^on$'), rele_on))
    application.add_handler(MessageHandler(filters.Regex(r'^off$'), rele_off))
    application.add_handler(MessageHandler(filters.Regex(r'^volver$'), volver))
    application.run_polling()

if __name__ == '__main__':
    main()
