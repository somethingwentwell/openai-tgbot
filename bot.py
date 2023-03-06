import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
import json
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
# basedir = os.path.abspath(os.path.dirname(__file__))
# basedir = os.path.split(basedir)[0]
# load_dotenv(os.path.join(basedir, '.env'))
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# MODEL = "test-text-davinci"
ENGINE = os.getenv("ENGINE")
OPENAI_NAME = os.getenv("OPENAI_NAME")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://{}.openai.azure.com/openai/deployments/{}/completions?api-version={}".format(OPENAI_NAME, ENGINE, OPENAI_API_VERSION)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="This is a bot that uses OpenAI to generate responses. Source code: https://github.com/somethingwentwell/openai-botframework")

async def echo(update, context):
    preprompt = os.getenv("PREPROMPT")
    prompt = preprompt + '\n' + update.message.text + '\n\n'
    stop = None
    if (len(json.loads(os.getenv("STOP"))) > 0):
        stop = json.loads(os.getenv("STOP"))
    data = {
        "prompt": prompt,
        "max_tokens": int(os.getenv("MAX_TOKENS")),
        "temperature": float(os.getenv("TEMPERATURE")),
        "frequency_penalty": float(os.getenv("FREQUENCY_PENALTY")),
        "presence_penalty": float(os.getenv("PRESENCE_PENALTY")),
        "top_p": float(os.getenv("TOP_P")),
        "best_of": 1,
        "stop": stop
    }
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=headers, data=json.dumps(data)) as response:
            print(response)
            if response.status == 200:
                result = (await response.json())['choices'][0]['text']
                text_parts = result.split("\n", 1)
                new_text = text_parts[1] if len(text_parts) > 1 else text_parts
                await context.bot.send_message(chat_id=update.effective_chat.id, text=new_text)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't understand your question.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv("TG_BOT_TOKEN")).build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    
    application.run_polling()
