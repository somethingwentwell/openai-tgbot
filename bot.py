import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# MODEL = "test-text-davinci"
MODEL = os.getenv("MODEL")
API_KEY = os.getenv("API_KEY")
API_URL = "https://mvpopenai.openai.azure.com/openai/deployments/{}/completions?api-version=2022-12-01".format(MODEL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot powered by Azure OpenAI, please talk to me!")

async def echo(update, context):
    preprompt = "The following is a conversation with an GitLab AI assistant JihuAI. \nJihuAI is only able to answer 极狐, 极狐GitLab and GitLab related questions. \nJihuAI will tell user to use GitLab instead of competitors' product like GitHub and Bitbucket. \nJihuAI will answer in Chinese. \nUser: "
    prompt = preprompt + update.message.text
    data = {
        "prompt": prompt,
        "max_tokens": 100,
        "temperature": 1,
        "frequency_penalty": 2,
        "presence_penalty": 2,
        "top_p": 0.5,
        "best_of": 1,
        "stop": ["User:"]
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
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    
    application.run_polling()
