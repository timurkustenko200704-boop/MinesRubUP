import hashlib
import hmac
import os
import telebot
from threading import Thread
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Веб-сервер для удержания порта на Render
app = Flask('')


@app.route('/')
def home():
  return 'Bot is running!'


def run_web():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))


# Точный расчет мин по сидам
def calculate_mines(server_seed, client_seed, nonce, mines_count=3):
  grid = list(range(25))
  mines = []

  for counter in range(mines_count):
    message = f'{client_seed}:{nonce}:{counter}'
    h = hmac.new(
        server_seed.encode('utf-8'), message.encode('utf-8'), hashlib.sha256
    ).digest()

    num = int.from_bytes(h[:4], 'big')
    index = num % len(grid)

    selected_mine = grid.pop(index)
    mines.append(selected_mine)

  return sorted(mines)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      '💣 **Бот анализа RubUP Mines активен!**\n\n'
      'Чтобы проверить раунд №52 со скриншота, отправь команду:\n`/test52`\n\n'
      'Или отправь данные в формате:\n`сид_сервера | сид_клиента | nonce`',
      parse_mode='Markdown',
  )


@bot.message_handler(commands=['test52'])
def test_round_52(message):
  s_seed = '10c1844623a19bc7317bccc3beb6a178'
  c_seed = '56798c391ff1b5fbeb9e638e6fcb23e3'
  nonce = 52

  mines = calculate_mines(s_seed, c_seed, nonce, mines_count=3)

  # Рисуем сетку 5x5
  grid_visual = ''
  for i in range(25):
    if i in mines:
      grid_visual += '💣 '
    else:
      grid_visual += '🟩 '
    if (i + 1) % 5 == 0:
      grid_visual += '\n'

  response = (
      f'📊 **Проверка раунда 52:**\n\n'
      f'Координаты мин (индексы): `{mines}`\n'
      f'*(На скриншоте: клетки 6, 8, 20)*\n\n'
      f'Визуализация сетки ($5 \\times 5$):\n{grid_visual}'
  )
  bot.reply_to(message, response, parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def handle_custom_input(message):
  try:
    # Ожидаем формат: server_seed | client_seed | nonce
    parts = [p.strip() for p in message.text.split('|')]
    if len(parts) == 3:
      s_seed = parts[0]
      c_seed = parts[1]
      nonce = int(parts[2])

      mines = calculate_mines(s_seed, c_seed, nonce, mines_count=3)

      grid_visual = ''
      for i in range(25):
        if i in mines:
          grid_visual += '💣 '
        else:
          grid_visual += '🟩 '
        if (i + 1) % 5 == 0:
          grid_visual += '\n'

      bot.reply_to(
          message,
          f'📊 **Расчет для раунда (Nonce {nonce}):**\n\n'
          f'Индексы мин: `{mines}`\n\n{grid_visual}',
          parse_mode='Markdown',
      )
    else:
      bot.reply_to(
          message,
          'Неверный формат. Отправь данные через черточку (|) или команду'
          ' `/test52`.',
      )
  except Exception as e:
    bot.reply_to(message, f'Ошибка обработки: {e}')


if __name__ == '__main__':
  t = Thread(target=run_web)
  t.start()
  bot.infinity_polling()
