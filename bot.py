import os
import telebot

# Получаем токен из переменных окружения Render
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      'Привет! Бот для анализа RubUP Mines успешно запущен и работает в'
      ' облаке! 🚀',
  )


@bot.message_handler(func=lambda message: True)
def echo_all(message):
  bot.reply_to(
      message,
      f'Получено твое сообщение: "{message.text}". Скоро здесь появится логика'
      ' проверки Provably Fair!',
  )


if __name__ == '__main__':
  bot.infinity_polling()
