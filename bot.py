import hmac
import hashlib
import os
import telebot

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


# Функция симуляции/проверки алгоритма Provably Fair (HMAC-SHA256)
def generate_mines(server_seed, client_seed, nonce, count=3):
  message = f'{client_seed}:{nonce}'
  h = hmac.new(
      server_seed.encode('utf-8'), message.encode('utf-8'), hashlib.sha256
  ).hexdigest()

  # Превращаем HMAC в массив чисел для сетки 5x5 (0-24)
  # Это базовый маппинг для тестов, будем уточнять по твоим раундам
  return h


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      'Привет! Бот анализа RubUP Mines активен. 🚀\nОтправь команду /test, чтобы'
      ' проверить расчеты по раундам.',
  )


@bot.message_handler(commands=['test'])
def test_rounds(message):
  # Тестовые данные по раундам (nonce 46, 47, 48)
  # Здесь мы проверяем генерацию хэша
  sample_server_seed = (
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
  )
  sample_client_seed = 'default_client'

  res_text = '📊 **Результаты проверки тестовых раундов:**\n\n'
  for nonce_val in [46, 47, 48]:
    hmac_res = generate_mines(
        sample_server_seed, sample_client_seed, nonce_val
    )
    res_text += (
        f'• **Nonce {nonce_val}:** HMAC сгенерирован успешно (`{hmac_res[:16]}...`)\n'
    )

  bot.reply_to(message, res_text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def echo_all(message):
  bot.reply_to(
      message,
      f'Получено: "{message.text}". Используй /test для проверки алгоритма.',
  )


if __name__ == '__main__':
  bot.infinity_polling()
