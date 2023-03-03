# Telegram Chatbot using OpenAI's GPT-3

This is a Telegram chatbot that uses Azure OpenAI's GPT-3 to generate responses to user messages.

## Prerequisites

To run this chatbot, you will need the following:

- Python 3.7 or higher
- A Telegram bot token
- An OpenAI API key
- `pip` package manager

## Installation

1. Clone this repository to your local machine.

2. Install the required libraries using `pip`:
```
pip install python-telegram-bot aiohttp openai python-dotenv
```

3. Set up the environment variables in a `.env` file. You can copy the `.env.example` file and rename it to `.env`, then replace the placeholders with your own API key and bot token.

```
API_KEY=<your_openai_api_key>
BOT_TOKEN=<your_telegram_bot_token>
MODEL=<your_model_in_azure_openai>
PREPROMPT=<the_prompt_before_user_input>
```

Make sure to keep the `.env` file private and do not commit it to version control.

## Usage

1. Start the bot by running the following command:
```
python bot.py
```
or in Docker
```
docker build -t openai-tg-bot .
docker run -d --env-file .env openai-tg-bot
```

2. Send a message to your bot in Telegram, and it should respond with a generated message


## Contributing

If you'd like to contribute to this project, please open an issue or pull request on GitHub.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

