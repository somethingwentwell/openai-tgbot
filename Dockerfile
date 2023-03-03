FROM python:3.9-slim-buster

WORKDIR /app

COPY . .

RUN pip install python-telegram-bot aiohttp openai python-dotenv

EXPOSE 443

CMD [ "python", "bot.py" ]
