import telebot
import hashlib
import random
from PIL import Image, ImageDraw

# 🔹 Replace with your BotFather token
TOKEN = "7290515316:AAEiLwdZ6qu3yZ_GF6MYX9tWBMh5EKm0d3Y"
bot = telebot.TeleBot(TOKEN)


while True:
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Error: {e}")




# 🔹 Grid settings
GRID_SIZE = 5  # 5x5 grid
CELL_SIZE = 120  # Each cell is 120x120 pixels

# 🔹 Load mine images
MONEY_MINE_IMG = "money_mine.png"  # 💰 Mine Image
EMPTY_MINE_IMG = "empty_mine.png"  # ❌ Empty Image

# 🔹 Password and user authentication
PASSWORD = "yash"
authorized_users = set()

# Store user-selected mine counts
user_mine_count = {}

def generate_mines(client_seed, num_mines):
    """
    Generates mine positions based on a hash of the client seed.
    Ensures at least 3 safe bets before a mine.
    """
    seed_hash = hashlib.sha256(client_seed.encode()).hexdigest()
    random.seed(seed_hash)

    all_positions = list(range(1, GRID_SIZE * GRID_SIZE + 1))
    
    # Ensure the first 3 positions are always safe
    safe_positions = random.sample(all_positions, 3)
    remaining_positions = [pos for pos in all_positions if pos not in safe_positions]

    # Place the mines
    mine_positions = random.sample(remaining_positions, num_mines)

    print(f"[DEBUG] Client Seed: {client_seed}")
    print(f"[DEBUG] Safe Positions: {safe_positions}")
    print(f"[DEBUG] Mine Positions: {mine_positions}")

    return mine_positions, safe_positions

def create_minefield_image(mine_positions, safe_positions):
    """
    Creates a 5x5 grid image with 💰 mines and ❌ empty slots.
    """
    WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE
    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(img)

    money_mine = Image.open(MONEY_MINE_IMG).resize((CELL_SIZE, CELL_SIZE))
    empty_mine = Image.open(EMPTY_MINE_IMG).resize((CELL_SIZE, CELL_SIZE))

    # Draw grid and mines
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            cell_number = i * GRID_SIZE + j + 1  # Cell index (1-25)
            x, y = j * CELL_SIZE, i * CELL_SIZE

            # Draw grid lines
            draw.rectangle([x, y, x + CELL_SIZE, y + CELL_SIZE], outline=(0, 0, 0, 255), width=3)

            # Place mines or empty slots
            if cell_number in mine_positions:
                img.paste(money_mine, (x, y), money_mine)
            else:
                img.paste(empty_mine, (x, y), empty_mine)

    # Save the final image
    img_path = "minefield.png"
    img.save(img_path)
    return img_path

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    if user_id in authorized_users:
        bot.reply_to(message, "✅ Welcome back! Choose the number of mines (e.g., 3, 5, 10).")
    else:
        bot.reply_to(message, "🔒 This bot is locked. Send the password to continue:")

@bot.message_handler(func=lambda message: message.chat.id not in authorized_users)
def check_password(message):
    user_id = message.chat.id
    if message.text.strip() == PASSWORD:
        authorized_users.add(user_id)
        bot.reply_to(message, "✅ Access granted! Now choose the number of mines (e.g., 3, 5, 10).")
    else:
        bot.reply_to(message, "❌ Wrong password! Try again.")

@bot.message_handler(func=lambda message: message.text.isdigit() and message.chat.id in authorized_users)
def set_mine_count(message):
    user_id = message.chat.id
    num_mines = int(message.text)

    if num_mines < 1 or num_mines > 22:
        bot.reply_to(message, "❌ Choose a number between 1 and 22.")
        return

    user_mine_count[user_id] = num_mines
    bot.reply_to(message, f"✅ **{num_mines} mines selected!** Now send a client seed:")

@bot.message_handler(func=lambda message: message.chat.id in authorized_users)
def process_client_seed(message):
    user_id = message.chat.id
    client_seed = message.text.strip()

    if user_id not in user_mine_count:
        bot.reply_to(message, "⚠️ First, choose the number of mines (send a number).")
        return

    if len(client_seed) < 5:
        bot.reply_to(message, "❌ Invalid seed! Send a valid one.")
        return

    num_mines = user_mine_count[user_id]
    mine_positions, safe_positions = generate_mines(client_seed, num_mines)
    image_path = create_minefield_image(mine_positions, safe_positions)

    bot.send_photo(message.chat.id, photo=open(image_path, "rb"), caption=f"🎰 **Stake Mine Predictor**\nSeed: `{client_seed}`\n💰 Mines: **{num_mines}**\n✅ **3 Guaranteed Safe Bets!**", parse_mode="Markdown")

# Run the bot
print("🤖 Bot is running with PASSWORD LOCK...")
bot.infinity_polling()
