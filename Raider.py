import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import asyncio
from colorama import init, Fore, Style

init(autoreset=True)

# ... (giữ nguyên các hàm save_token, load_token, display_logo, display_status, token_management)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True  # Cần cho các lệnh quản lý thành viên

bot = commands.Bot(command_prefix="!", intents=intents)

class SpamButton(discord.ui.View):
    def __init__(self, message, spam_count=50):
        super().__init__()
        self.message = message
        self.spam_count = spam_count

    @discord.ui.button(label="Spam", style=discord.ButtonStyle.red)
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for i in range(self.spam_count):
            try:
                await interaction.followup.send(f"{self.message} [{i+1}/{self.spam_count}]")
                await asyncio.sleep(0.5)  # Giảm tốc độ để tránh bị phát hiện
            except:
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
    await interaction.response.send_message(f"💥SPAM TEXT💥 : {message}\nSpam count: {count}", view=view, ephemeral=True)

@bot.tree.command(name="nuke", description="Nuke the server (admin only)")
async def nuke(interaction: discord.InterInteraction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("You need admin permissions to use this command!", ephemeral=True)
    
    await interaction.response.defer()
    
    guild = interaction.guild
    
    # Xóa tất cả kênh
    for channel in guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(0.5)
        except:
            pass
    
    # Tạo kênh spam mới
    for i in range(20):
        try:
            await guild.create_text_channel(f"nuked-{i}")
            await asyncio.sleep(0.5)
        except:
            pass
    
    # Đổi tên server
    try:
        await guild.edit(name="NUKED SERVER")
    except:
        pass
    
    await interaction.followup.send("Server has been nuked!")

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
