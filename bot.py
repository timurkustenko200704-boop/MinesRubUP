import os
import threading
import telebot
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Создаем простой веб-сервер для бесплатного тарифа Render (чтобы открывался порт)
app = Flask('')


@app.route('/')
def home():
  return 'Bot is running!'


def run_web():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))


# Логика бота
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      'Привет! Бот анализа RubUP Mines успешно запущен на бесплатном тарифе! 🚀',
  )


@bot.message_handler(commands=['test'])
def test_rounds(message):
  bot.reply_to(message, 'Тест пройден! Система готовности к расчету мин активна.')


@bot.message_handler(func=lambda message: True)
def echo_all(message):
  bot.reply_to(message, f'Получено: "{message.text}"')


if __name__ == '__main__':
  # Запускаем веб-сервер в отдельном потоке, чтобы он занимал порт для Render
  t = threading.Thread(target=run_web)
  t.start()

  # Запускаем бота
  bot.infinity_polling()
