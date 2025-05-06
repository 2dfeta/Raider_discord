import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import asyncio
from colorama import init, Fore, Style

init(autoreset=True)

# Hàm quản lý token
def save_token(token):
    with open("token.json", "w") as file:
        json.dump({"TOKEN": token}, file)

def load_token():
    try:
        with open("token.json", "r") as file:
            data = json.load(file)
            return data.get("TOKEN")
    except FileNotFoundError:
        print(Fore.RED + "Lỗi: Không tìm thấy file token.json")
        return None
    except json.JSONDecodeError:
        print(Fore.RED + "Lỗi: Định dạng JSON không hợp lệ trong token.json")
        return None

# Hiển thị logo
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
    print(Fore.GREEN + "Trạng thái: Đã kết nối" if connected else Fore.RED + "Trạng thái: Ngắt kết nối")

# Quản lý token
def token_management():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "Quản lý Token Bot Discord\n")
    print("1. Nhập token mới")
    print("2. Sử dụng token đã lưu")
    choice = input(Fore.YELLOW + "Chọn tùy chọn (1, 2): ")

    if choice == "1":
        new_token = input(Fore.GREEN + "Nhập token mới: ")
        save_token(new_token)
        print(Fore.GREEN + "Đã lưu token thành công!")
        return new_token
    elif choice == "2":
        token = load_token()
        if token:
            print(Fore.GREEN + f"Đã tải token: {token}")
            return token
        else:
            print(Fore.RED + "Không tìm thấy token.")
            return None
    else:
        print(Fore.RED + "Lựa chọn không hợp lệ.")
        return None

# Cấu hình bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Lớp nút Spam cải tiến
class SpamButton(discord.ui.View):
    def __init__(self, message, spam_count=20):
        super().__init__(timeout=60)  # Timeout 60 giây
        self.message = message
        self.spam_count = min(spam_count, 20)  # Giới hạn tối đa 20 tin nhắn
    
    @discord.ui.button(label="Spam", style=discord.ButtonStyle.red, emoji="💣")
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message(
                "❌ Bạn cần quyền quản lý tin nhắn để sử dụng chức năng này!",
                ephemeral=True
            )
        
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel
        
        # Gửi thông báo bắt đầu
        await interaction.followup.send(
            f"⚠️ Đang gửi {self.spam_count} tin nhắn spam...",
            ephemeral=True
        )
        
        # Gửi tin nhắn spam trực tiếp vào kênh
        for i in range(self.spam_count):
            try:
                await channel.send(f"{self.message} [{i+1}/{self.spam_count}]")
                await asyncio.sleep(1.5)  # Giảm tốc độ để tránh bị rate limit
            except discord.HTTPException as e:
                print(Fore.RED + f"Lỗi khi spam: {e}")
                await channel.send("🛑 Đã xảy ra lỗi khi spam tin nhắn!")
                break
        
        # Gửi thông báo hoàn thành
        await interaction.followup.send(
            f"✅ Đã gửi xong {self.spam_count} tin nhắn!",
            ephemeral=True
        )

# Lệnh spamraid cải tiến
@bot.tree.command(name="spamraid", description="Tạo nút để spam tin nhắn (cần quyền quản lý tin nhắn)")
@app_commands.describe(
    message="Nội dung tin nhắn cần spam",
    count="Số lần spam (tối đa 20)"
)
async def spamraid(interaction: discord.Interaction, message: str, count: int = 10):
    count = min(max(count, 1), 20)  # Giới hạn từ 1-20 lần
    
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(
            "❌ Bạn cần quyền quản lý tin nhắn để sử dụng lệnh này!",
            ephemeral=True
        )
    
    view = SpamButton(message, count)
    await interaction.response.send_message(
        f"💣 **THIẾT LẬP SPAM** 💣\nNội dung: {message}\nSố lần: {count}\n"
        "Nhấn nút bên dưới để bắt đầu spam",
        view=view,
        ephemeral=True
    )

# Lệnh nuke cải tiến
@bot.tree.command(name="nuke", description="Xóa toàn bộ server (cần quyền quản trị)")
async def nuke(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ Bạn cần quyền quản trị để sử dụng lệnh này!",
            ephemeral=True
        )
    
    # Xác nhận trước khi nuke
    confirm_view = discord.ui.View()
    confirm_view.add_item(discord.ui.Button(
        style=discord.ButtonStyle.red,
        label="XÁC NHẬN NUKE",
        custom_id="confirm_nuke"
    ))
    
    await interaction.response.send_message(
        "⚠️ **CẢNH BÁO: THAO TÁC NGUY HIỂM** ⚠️\n"
        "Bạn có chắc muốn xóa toàn bộ server?\n"
        "• Xóa tất cả kênh\n• Xóa tất cả vai trò\n• Đổi tên server\n\n"
        "Nhấn nút bên dưới để xác nhận.",
        view=confirm_view,
        ephemeral=True
    )
    
    # Chờ xác nhận
    try:
        await bot.wait_for(
            "interaction",
            check=lambda i: i.data.get("custom_id") == "confirm_nuke" and i.user == interaction.user,
            timeout=30
        )
    except asyncio.TimeoutError:
        return await interaction.edit_original_response(
            content="🕒 Đã hết thời gian xác nhận",
            view=None
        )
    
    # Bắt đầu thực hiện nuke
    await interaction.edit_original_response(
        content="☢️ Đang thực hiện nuke server...",
        view=None
    )
    
    guild = interaction.guild
    
    # Xóa kênh
    for channel in guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(0.7)
        except Exception as e:
            print(Fore.YELLOW + f"Không thể xóa kênh {channel.name}: {e}")
    
    # Xóa vai trò
    for role in guild.roles:
        try:
            if role.name != "@everyone":
                await role.delete()
                await asyncio.sleep(0.7)
        except Exception as e:
            print(Fore.YELLOW + f"Không thể xóa vai trò {role.name}: {e}")
    
    # Tạo kênh mới
    for i in range(5):
        try:
            await guild.create_text_channel(f"nuked-by-{interaction.user.name}-{i+1}")
            await asyncio.sleep(0.7)
        except Exception as e:
            print(Fore.YELLOW + f"Không thể tạo kênh: {e}")
    
    # Đổi tên server
    try:
        await guild.edit(name=f"💀 NUKE BY {interaction.user.name.upper()} 💀")
    except Exception as e:
        print(Fore.YELLOW + f"Không thể đổi tên server: {e}")
    
    await interaction.followup.send(
        f"💥 **SERVER ĐÃ BỊ NUKE BỞI {interaction.user.mention}** 💥",
        ephemeral=False
    )

# Sự kiện khi bot ready
@bot.event
async def on_ready():
    display_logo()
    display_status(True)
    print("Đã kết nối với tư cách " + Fore.YELLOW + f"{bot.user}")

    try:
        synced = await bot.tree.sync()
        print(Fore.GREEN + f"Đã đồng bộ {len(synced)} lệnh.")
    except Exception as e:
        display_status(False)
        print(Fore.RED + f"Lỗi khi đồng bộ lệnh: {e}")

# Khởi chạy bot
if __name__ == "__main__":
    TOKEN = token_management()
    if TOKEN:
        try:
            bot.run(TOKEN)
        except discord.errors.LoginFailure:
            print(Fore.RED + "Token không hợp lệ. Vui lòng kiểm tra lại token.")
            input(Fore.YELLOW + "Nhấn Enter để quay lại menu...")
            TOKEN = token_management()
            if TOKEN:
                bot.run(TOKEN)
        except Exception as e:
            print(Fore.RED + f"Lỗi không mong muốn: {e}")
            input(Fore.YELLOW + "Nhấn Enter để khởi động lại...")
            TOKEN = token_management()
            if TOKEN:
                bot.run(TOKEN)
    else:
        print(Fore.RED + "❌ Lỗi: Không thể tải hoặc thiết lập token.")
