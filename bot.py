import hashlib
import hmac
import os
import telebot

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Простой веб-сервер для удержания порта на Render
from threading import Thread
from flask import Flask

app = Flask('')


@app.route('/')
def home():
  return 'Bot is running!'


def run_web():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))


# Функция расчета мин по стандарту Provably Fair (HMAC-SHA256)
def calculate_mines(server_seed, client_seed, nonce, mines_count=3):
  message = f'{client_seed}:{nonce}'
  h = hmac.new(
      server_seed.encode('utf-8'), message.encode('utf-8'), hashlib.sha256
  ).hexdigest()

  grid = list(range(25))  # Поле 5x5 (индексы от 0 до 24)
  mines = []

  # Превращаем части хэша в байты и выбираем позиции мин
  # (Стандартный алгоритм генерации для игр типа Mines)
  seed_bytes = bytes.fromhex(h)
  byte_offset = 0

  while len(mines) < mines_count and byte_offset + 8 <= len(seed_bytes):
    # Берем 4 байта из хэша и превращаем в число
    chunk = seed_bytes[byte_offset : byte_offset + 4]
    num = int.from_bytes(chunk, 'big')
    # Вычисляем позицию на сетке
    index = num % len(grid)

    selected_mine = grid.pop(index)
    if selected_mine not in mines:
      mines.append(selected_mine)

    byte_offset += 4

  return sorted(mines), h


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      '💣 **Бот анализа RubUP Mines активирован!**\n\nЧтобы проверить'
      ' конкретный раунд после его завершения, отправь данные в формате:\n`seed'
      ' | client_seed | nonce`\n\nПример команды /test запустит проверку'
      ' алгоритма.',
      parse_mode='Markdown',
  )


@bot.message_handler(commands=['test'])
def test_calculation(message):
  # Тестовые параметры раунда для проверки
  s_seed = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
  c_seed = 'default_client'
  nonce = 1

  mines, hmac_hash = calculate_mines(s_seed, c_seed, nonce, mines_count=3)

  # Рисуем эмодзи-сетку 5x5
  grid_visual = ''
  for i in range(25):
    if i in mines:
      grid_visual += '💣 '
    else:
      grid_visual += '🟩 '
    if (i + 1) % 5 == 0:
      grid_visual += '\n'

  response = (
      f'📊 **Тестовый расчет раунда (Nonce {nonce}):**\n\n'
      f'Хэш: `{hmac_hash[:20]}...`\n'
      f'Координаты мин (индексы): `{mines}`\n\n'
      f'Визуализация сетки ($5 \\times 5$):\n{grid_visual}'
  )
  bot.reply_to(message, response, parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def handle_input(message):
  # Сюда можно будет отправлять данные реальных раундов для парсинга
  bot.reply_to(
      message,
      'Получено! Чтобы проверить расчеты алгоритма, нажми /test или отправь'
      ' параметры завершенного раунда.',
  )


if __name__ == '__main__':
  t = Thread(target=run_web)
  t.start()
  bot.infinity_polling()
