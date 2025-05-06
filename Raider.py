import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import asyncio
from colorama import init, Fore

init(autoreset=True)

def save_token(token):
    with open("token.json", "w") as file:
        json.dump({"TOKEN": token}, file)

def load_token():
    try:
        with open("token.json", "r") as file:
            data = json.load(file)
            return data.get("TOKEN")
    except:
        return None

def display_logo():
    logo = r'''
░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓████████▓▒░▒▓████████▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░       ░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     
░▒▓███████▓▒░ ░▒▓██████▓▒░        ░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░    ░▒▓█▓▒░     
░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░            ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     
░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░            ░▒▓█▓▓█▓▒░ ░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     
░▒▓███████▓▒░   ░▒▓█▓▒░             ░▒▓██▓▒░  ░▒▓█▓▒░▒▓████████▓▒░  ░▒▓█▓▒░     
'''
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.BLUE + logo)

def display_status(connected):
    print(Fore.GREEN + "Status: Connected" if connected else Fore.RED + "Status: Disconnected")

def token_management():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "Bot Token Management\n")
    print("1. Set new token")
    print("2. Load previous token\n")

    choice = input(Fore.YELLOW + "Choose an option (1, 2): ")
    if choice == "1":
        new_token = input(Fore.GREEN + "Enter new token: ")
        save_token(new_token)
        return new_token
    elif choice == "2":
        token = load_token()
        return token
    else:
        print(Fore.RED + "Invalid choice.")
        return None

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="spamraid", description="Tự động spam tin nhắn")
@app_commands.describe(
    message="Tin nhắn muốn spam",
    amount="Số lần gửi"
)
async def spamraid(interaction: discord.Interaction, message: str, amount: int):
    if amount > 50:
        await interaction.response.send_message("❌ Quá 50 tin một lần", ephemeral=True)
        return

    await interaction.response.send_message(f"✅ Bắt đầu spam {amount} lần.", ephemeral=True)

    try:
        for _ in range(amount):
            await interaction.channel.send(message)
            await asyncio.sleep(0.25)
    except Exception as e:
        await interaction.followup.send(f"❌ Lỗi khi gửi tin nhắn: {e}", ephemeral=True)

@bot.event
async def on_ready():
    display_logo()
    display_status(True)
    print(Fore.YELLOW + f"Connected as: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(Fore.GREEN + f"Synchronized {len(synced)} commands.")
    except Exception as e:
        print(Fore.RED + f"Sync error: {e}")

if __name__ == "__main__":
    TOKEN = token_management()
    if TOKEN:
        try:
            bot.run(TOKEN)
        except discord.errors.LoginFailure:
            print(Fore.RED + "❌ Token không hợp lệ.")
        except Exception as e:
            print(Fore.RED + f"Lỗi khi chạy bot: {e}")
    else:
        print(Fore.RED + "Không thể lấy token.")
