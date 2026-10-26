import hashlib
import hmac
import os
import telebot
from threading import Thread
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Веб-сервер для удержания порта на бесплатном тарифе Render
app = Flask('')


@app.route('/')
def home():
  return 'Bot is running!'


def run_web():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))


# Точный алгоритм генерации мин RubUP по стандарту Provably Fair
def calculate_rubup_mines(server_seed, client_seed, nonce, mines_count=3):
  grid = list(range(25))  # Клетки от 0 до 24 (сетка 5x5)
  mines = []

  # По описанию игры: используется счетчик для шагов генерации
  for counter in range(mines_count):
    message = f'{client_seed}:{nonce}:{counter}'
    h = hmac.new(
        server_seed.encode('utf-8'), message.encode('utf-8'), hashlib.sha256
    ).digest()

    # Берем первые 4 байта хэша как число
    num = int.from_bytes(h[:4], 'big')
    index = num % len(grid)

    selected_mine = grid.pop(index)
    mines.append(selected_mine)

  return sorted(mines)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      '💣 **Бот анализа RubUP Mines активирован!**\n\n'
      'Отправь команду /test49, /test50 или /test51, чтобы проверить расчет'
      ' для твоих реальных раундов со скриншотов.',
      parse_mode='Markdown',
  )


# Проверка раунда 49 (со скриншота)
@bot.message_handler(commands=['test49'])
def test_round_49(message):
  s_seed = '02ad37e579271e9f274ca51b8ea3992f'
  c_seed = '56798c391ff1b5fbeb9e638e6fcb23e3'
  nonce = 49
  run_test_calculation(message, s_seed, c_seed, nonce)


# Проверка раунда 50 (со скриншота)
@bot.message_handler(commands=['test50'])
def test_round_50(message):
  s_seed = '266288cd8947bfb1448f6f6ef0800b9d'
  c_seed = '56798c391ff1b5fbeb9e638e6fcb23e3'
  nonce = 50
  run_test_calculation(message, s_seed, c_seed, nonce)


# Проверка раунда 51 (со скриншота)
@bot.message_handler(commands=['test51'])
def test_round_51(message):
  s_seed = 'b5f4273c5a2ef21fefacfe89ddb496b6'
  c_seed = '56798c391ff1b5fbeb9e638e6fcb23e3'
  nonce = 51
  run_test_calculation(message, s_seed, c_seed, nonce)


def run_test_calculation(message, s_seed, c_seed, nonce):
  mines = calculate_rubup_mines(s_seed, c_seed, nonce, mines_count=3)

  # Рисуем визуальную сетку 5x5 (индексы от 0 до 24)
  grid_visual = ''
  for i in range(25):
    if i in mines:
      grid_visual += '💣 '
    else:
      grid_visual += '🟩 '
    if (i + 1) % 5 == 0:
      grid_visual += '\n'

  response = (
      f'📊 **Результат проверки раунда (Nonce {nonce}):**\n\n'
      f'Точные индексы мин: `{mines}`\n\n'
      f'Визуализация сетки ($5 \\times 5$):\n{grid_visual}'
  )
  bot.reply_to(message, response, parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def handle_other(message):
  bot.reply_to(
      message,
      'Используй команды `/test49`, `/test50` или `/test51` для проверки'
      ' реальных раундов.',
      parse_mode='Markdown',
  )


if __name__ == '__main__':
  t = Thread(target=run_web)
  t.start()
  bot.infinity_polling()
