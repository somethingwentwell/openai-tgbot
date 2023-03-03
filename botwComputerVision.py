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
API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://{}.openai.azure.com/openai/deployments/{}/completions?api-version=2022-12-01".format(OPENAI_NAME, ENGINE)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot powered by Azure OpenAI, please talk to me!")

async def photo(update, context):
    if update.message.photo:
        # Get the photo file ID
        photo_file_id = update.message.photo[-1].file_id
        # Download the photo
        photo_file = await context.bot.get_file(photo_file_id)
        photo_url = photo_file.file_path
        # Call the Azure Computer Vision API to analyze the photo
        headers = {'Ocp-Apim-Subscription-Key': os.getenv("COMPUTER_VISION_KEY"), 'Content-Type': 'application/json'}
        params = {'visualFeatures': 'Description'}
        imgData = {'url': photo_url}
        response = requests.post(os.getenv("COMPUTER_VISION_ENDPOINT") + '/vision/v3.2/analyze', headers=headers, params=params, json=imgData)
        # Parse the response and send it back to the user
        if response.status_code == 200:
            result = response.json()
            description = result['description']['captions'][0]['text']
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Description: ' + description)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, there was an error analyzing your photo.")

async def echo(update, context):
    preprompt = os.getenv("PREPROMPT")
    prompt = preprompt + update.message.text
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
    photo_handler = MessageHandler(filters.PHOTO, photo)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(photo_handler)
    
    application.run_polling()
