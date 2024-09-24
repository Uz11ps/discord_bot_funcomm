import discord
import json
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import SelectOption
import os
import random
import asyncio
from datetime import datetime
import requests
from discord.ui import Button
import discord.ui
from discord import Embed
import time
from datetime import datetime, timedelta
from discord.ext import commands, tasks
import discord
from discord.ext import commands
import json
from datetime import datetime
from discord.ext import tasks


file = open('config.json', 'r')
config = json.load(file)

intents = discord.Intents.default().all()
intents.messages = True
intents.guilds = True
bot = commands.Bot(config['prefix'], intents=intents)

bot = commands.Bot(command_prefix='!', intents=intents)
bot = commands.Bot(command_prefix=".", intents=intents)


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////// валюта сервера 






#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


try:
    with open('balances.json', 'r') as f:
        data = f.read()
        if data:
            balances = json.loads(data)
        else:
            balances = {}
except FileNotFoundError:
    balances = {}

try:
    with open('last_work_times.json', 'r') as f:
        data = f.read()
        if data:
            last_work_times = json.loads(data)
        else:
            last_work_times = {}
except FileNotFoundError:
    last_work_times = {}

try:
    with open('last_crime_times.json', 'r') as f:
        data = f.read()
        if data:
            last_crime_times = json.loads(data)
        else:
            last_crime_times = {}
except FileNotFoundError:
    last_crime_times = {}

allowed_channel_id = 1136732368942669885  # ID разрешенного канала

def check_channel(ctx):
    return ctx.channel.id == allowed_channel_id

def check_roles(ctx):
    allowed_roles = ["admin money", "MAIN"]  # Роли, которым разрешено использовать команды
    user_roles = [role.name for role in ctx.author.roles]
    return any(role in allowed_roles for role in user_roles)

async def send_pink_message(ctx, content):
    embed = discord.Embed(description=content, color=discord.Color.from_rgb(168, 11, 42))
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    balances[str(member.id)] = 100
    print(f'{member.name} присоединился к серверу и получил 100 <:white_star:1226746455214264381>.')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        channel = bot.get_channel(allowed_channel_id)  # Получаем канал по его ID
        message = await ctx.send(f"Тебе не сюда, тебе в {channel.mention}")  # Упоминаем канал
        await asyncio.sleep(5)
        await ctx.message.delete()
        await message.delete()
    elif isinstance(error, commands.MissingRole):
        await send_pink_message(ctx, "Тебе это не доступно")
        await asyncio.sleep(5)
        await ctx.message.delete()


@bot.command()
@commands.check(check_channel)
async def balance(ctx):
    user_id = str(ctx.author.id)
    balance = balances.get(user_id, 0)
    await send_pink_message(ctx, f'У вас {balance} <:white_star:1226746455214264381>.')

@bot.command()
@commands.check(check_channel)
async def deposit(ctx, amount: int):
    user_id = str(ctx.author.id)
    if amount < 200:  # Минимальная ставка - 200 звездочек
        await send_pink_message(ctx, 'Минимальная ставка - 200 <:white_star:1226746455214264381>.')
        return

    balances[user_id] = balances.get(user_id, 0) + amount
    await send_pink_message(ctx, f'Вы внесли {amount} <:white_star:1226746455214264381> на свой счет.')

    # Сохраняем обновленные балансы в файл JSON
    with open('balances.json', 'w') as f:
        json.dump(balances, f)

@bot.command()
@commands.check(check_channel)
async def crime(ctx):
    user_id = str(ctx.author.id)
    balance = balances.get(user_id, 0)

    if balance <= 0:
        await send_pink_message(ctx, 'У вас недостаточно <:white_star:1226746455214264381> для совершения преступления.')
        return

    current_time = time.time()
    last_crime_time = last_crime_times.get(user_id, 0)

    if current_time - last_crime_time < 12 * 3600:
        await send_pink_message(ctx, 'Вы можете совершить преступление только раз в 12 часов.')
        return

    if random.random() <= 0.1:
        amount_stolen = random.randint(50, 200)
        stolen_from_deposit = min(amount_stolen, balance)
        balances[user_id] -= stolen_from_deposit
        await send_pink_message(ctx, f'Вы ограбили {stolen_from_deposit} <:white_star:1226746455214264381> у себя.')
    else:
        balances[user_id] -= 50  # Штраф в случае неудачного преступления
        await send_pink_message(ctx, 'Попытка грабежа не удалась.')

    last_crime_times[user_id] = current_time  # Обновляем время последнего преступления

    # Сохраняем обновленные балансы и время преступления в файл JSON
    with open('balances.json', 'w') as f:
        json.dump(balances, f)
    with open('last_crime_times.json', 'w') as f:
        json.dump(last_crime_times, f)

@bot.command()
@commands.check(check_channel)
async def leaderboard(ctx):
    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = "Лидерборд:\n"
    for idx, (user_id, balance) in enumerate(sorted_balances[:10], start=1):
        user = bot.get_user(int(user_id))
        if user:
            leaderboard_text += f"{idx}. {user.name}: {balance} <:white_star:1226746455214264381>\n"
    await send_pink_message(ctx, leaderboard_text)

@bot.command()
@commands.check(check_channel)
async def give(ctx, amount: int, member: discord.Member):
    if amount <= 0:
        await send_pink_message(ctx, 'Количество должно быть положительным числом.')
        return

    user_id = str(ctx.author.id)
    recipient_id = str(member.id)

    if balances.get(user_id, 0) < amount:
        await send_pink_message(ctx, 'У вас недостаточно <:white_star:1226746455214264381> для передачи.')
        return

    balances[user_id] -= amount
    balances[recipient_id] = balances.get(recipient_id, 0) + amount

    await send_pink_message(ctx, f'{ctx.author.mention} передал {amount} <:white_star:1226746455214264381> пользователю {member.mention}.')

    # Сохраняем обновленные балансы в файл JSON
    with open('balances.json', 'w') as f:
        json.dump(balances, f)

@bot.command()
@commands.check(check_channel)
@commands.check(check_roles)
async def addstars(ctx, amount: int, member: discord.Member):
    print(f"Attempting to add {amount} stars to {member.display_name}.")  # Отладочное сообщение
    if amount <= 0:
        await send_pink_message(ctx, 'Количество должно быть положительным числом.')
        return

    recipient_id = str(member.id)

    balances[recipient_id] = balances.get(recipient_id, 0) + amount

    await send_pink_message(ctx, f'{ctx.author.mention} добавил {amount} <:white_star:1226746455214264381> пользователю {member.mention}.')

    # Сохраняем обновленные балансы в файл JSON
    with open('balances.json', 'w') as f:
        json.dump(balances, f)

    print(f"Successfully added {amount} stars to {member.display_name}.")  # Отладочное сообщение

@bot.command()
@commands.check(check_channel)
@commands.check(check_roles)
async def removestars(ctx, amount: int, member: discord.Member):
    if amount <= 0:
        await send_pink_message(ctx, 'Количество должно быть положительным числом.')
        return

    recipient_id = str(member.id)

    if balances.get(recipient_id, 0) < amount:
        await send_pink_message(ctx, 'У пользователя недостаточно <:white_star:1226746455214264381> для удаления.')
        return

    balances[recipient_id] -= amount

    await send_pink_message(ctx, f'{ctx.author.mention} убрал {amount} <:white_star:1226746455214264381> у пользователя {member.mention}.')

    # Сохраняем обновленные балансы в файл JSON
    with open('balances.json', 'w') as f:
        json.dump(balances, f)

@bot.command()
@commands.check(check_channel)
@commands.check(check_roles)  # Проверяем роли пользователя
async def check_balance(ctx, member: discord.Member):
    if not member:
        member = ctx.author

    user_id = str(member.id)
    balance = balances.get(user_id, 0)
    await send_pink_message(ctx, f'У пользователя {member.display_name} {balance} <:white_star:1226746455214264381>.')

@bot.command()
@commands.check(check_channel)
async def work(ctx):
    user_id = str(ctx.author.id)
    current_time = time.time()
    last_work_time = last_work_times.get(user_id, 0)
    if current_time - last_work_time < 12 * 3600:
        await send_pink_message(ctx, 'Вы уже работали недавно. Приходите позже.')
        return

    earnings = random.randint(50, 200)
    balances[user_id] = balances.get(user_id, 0) + earnings
    last_work_times[user_id] = current_time

    await send_pink_message(ctx, f'Вы заработали {earnings} <:white_star:1226746455214264381>. Приходите через 12 часов.')

    # Сохраняем обновленные балансы и время работы в файл JSON
    with open('balances.json', 'w') as f:
        json.dump(balances, f)
    with open('last_work_times.json', 'w') as f:
        json.dump(last_work_times, f)


@bot.command()
@commands.check(check_channel)
async def casino(ctx, amount: int):
    user_id = str(ctx.author.id)
    if amount < 200:
        await send_pink_message(ctx, 'Минимальная ставка в казино - 200 <:white_star:1226746455214264381>.')
        return

    balance = balances.get(user_id, 0)

    if amount > balance:
        await send_pink_message(ctx, 'У вас недостаточно <:white_star:1226746455214264381> для этой ставки.')
        return

    if random.random() <= 0.1:
        win_amount = amount * 2  # Рассчитываем точное количество выигрыша
        balances[user_id] += win_amount  # Добавляем выигрыш к балансу
        embed = discord.Embed(
            title="Казино",
            description=f"Поздравляем! Вы выиграли {win_amount} <:white_star:1226746455214264381>!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        balances[user_id] -= amount  # Теряем ставку, если проигрыш
        await send_pink_message(ctx, f'Увы, вы проиграли {amount} <:white_star:1226746455214264381>.')

    # Сохраняем обновленные балансы в файл JSON
    with open('balances.json', 'w') as f:
        json.dump(balances, f)








































































# Загрузка балансов из файла JSON при запуске бота
balances = {}
try:
    with open('balances.json', 'r') as f:
        balances = json.load(f)
except FileNotFoundError:
    pass
# Function to check an allowed channel
def check_channel(ctx):
    return ctx.channel.id == 1136665779119591424
@bot.command()
async def change_channel_name(ctx, new_name):
    channel = ctx.message.author.voice.channel
    await channel.edit(name=new_name)
    await ctx.send(f"Channel name changed to {new_name}")
@bot.command()
async def change_channel_limit(ctx, limit: int):
    channel = ctx.message.author.voice.channel
    await channel.edit(user_limit=limit)
    await ctx.send(f"Channel participant limit changed to {limit}")
@bot.command()
async def change_channel_permissions(ctx):
    channel = ctx.message.author.voice.channel
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(connect=False),
        ctx.guild.me: discord.PermissionOverwrite(connect=True)
    }
    await channel.edit(overwrites=overwrites)
    await ctx.send(f"Channel permissions changed for {channel}")
# Run the bot with the Discord token as an environment variable

async def buy_item(interaction, item_number, price, item_name, guild):
    user_id = str(interaction.user.id)
    balance = balances.get(user_id, 0)
    if balance >= price:
        balances[user_id] -= price
        message = await interaction.response.send_message(f'{interaction.user.mention} successfully purchased {item_name}!', delete_after=5)
        if item_number == 1:  # Personal channel for a month
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=False),
                guild.me: discord.PermissionOverwrite(connect=True)
            }
            channel = await guild.create_voice_channel(f'{interaction.user.name}\'s Channel', overwrites=overwrites)
            await interaction.user.move_to(channel)
            user_role = await guild.create_role(name=f'{interaction.user.name}_Role')
            await interaction.user.add_roles(user_role)
            await channel.set_permissions(user_role, connect=True, manage_channels=True, manage_permissions=True)
            room_info = {
                "user_id": user_id,
                "channel_id": channel.id,
                "channel_name": channel.name,
                "role_id": user_role.id,
                "role_name": user_role.name
            }
            with open('DiscordRooms.json', 'a') as f:
                json.dump(room_info, f)
                f.write('\n')
            await asyncio.sleep(30 * 24 * 60 * 60)
            await channel.delete(reason="Expired personal channel")
            await user_role.delete(reason="Expired personal role")

     
        elif item_number == 2:  # Роль на месяц
            role = guild.get_role(1211759160622841886)
            if role is None:
                await interaction.response.send_message("Ошибка: Роль не найдена.", ephemeral=True)
                return
    
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f'{interaction.user.mention} успешно приобрёл роль на месяц!', delete_after=5)
            await asyncio.sleep(30 * 24 * 60 * 60)
            await interaction.user.remove_roles(role, reason="Истек срок роли")
        
        elif item_number == 3:  # Роль на 3 месяца
            await buy_role_3_months(interaction, guild)
        
        elif item_number == 4:  # Роль на год
            await buy_role_1_year(interaction, guild)
        
        elif item_number == 5:  # Возможность ставить смайлы в войсах
            await buy_voice_smilies_permission(interaction, guild)
        
        # Сохраняем обновленные балансы в файл JSON
        with open('balances.json', 'w') as f:
            json.dump(balances, f)
    else:
        await interaction.response.send_message("У вас недостаточно <:white_star:1226746455214264381> для этой покупки.", delete_after=5)

async def buy_role_3_months(interaction, guild):
    user_id = str(interaction.user.id)
    balance = balances.get(user_id, 0)
    price = 5000

    if balance >= price:
        balances[user_id] -= price
        
        role = guild.get_role(1211759160622841886)
        if role is None:
            await interaction.response.send_message("Ошибка: Роль не найдена.", ephemeral=True)
            return
    
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f'{interaction.user.mention} успешно приобрёл роль на 3 месяца!')
        await asyncio.sleep(3 * 30 * 24 * 60 * 60)
        await interaction.user.remove_roles(role, reason="Истек срок роли")
        
        with open('balances.json', 'w') as f:
            json.dump(balances, f)
    else:
        await interaction.response.send_message("У вас недостаточно <:white_star:1226746455214264381> для этой покупки.")

async def buy_role_1_year(interaction, guild):
    user_id = str(interaction.user.id)
    balance = balances.get(user_id, 0)
    price = 20000

    if balance >= price:
        balances[user_id] -= price
        
        role = guild.get_role(1211759160622841886)
        if role is None:
            await interaction.response.send_message("Ошибка: Роль не найдена.", ephemeral=True)
            return
    
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f'{interaction.user.mention} успешно приобрёл роль на год!')
        await asyncio.sleep(365 * 24 * 60 * 60)
        await interaction.user.remove_roles(role, reason="Истек срок роли")
        
        with open('balances.json', 'w') as f:
            json.dump(balances, f)
    else:
        await interaction.response.send_message("У вас недостаточно <:white_star:1226746455214264381> для этой покупки.")

async def buy_voice_smilies_permission(interaction, guild):
    user_id = str(interaction.user.id)
    balance = balances.get(user_id, 0)
    price = 5000

    if balance >= price:
        balances[user_id] -= price
        
        permissions = discord.Permissions(
            send_messages=True,
            speak=True,
            use_external_emojis=True
        )
        role = await guild.create_role(name="Крутышка", permissions=permissions)
        
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f'{interaction.user.mention} успешно приобрёл возможность ставить смайлы в войсах!')
        await asyncio.sleep(30 * 24 * 60 * 60)
        await interaction.user.remove_roles(role, reason="Истек срок роли")
        await role.delete(reason="Истек срок роли")
        
        with open('balances.json', 'w') as f:
            json.dump(balances, f)
    else:
        await interaction.response.send_message("У вас недостаточно <:white_star:1226746455214264381> для этой покупки.")

@bot.command()
async def shop(ctx):
    if not check_channel(ctx):
        await ctx.send("Вы можете использовать эту команду только в разрешенном канале.")
        return

    embed = discord.Embed(title="Что можно купить за звездочки", description="Добро пожаловать в наш магазин! Вот что у нас есть на продажу:", color=discord.Color.blue())
    embed.add_field(name="Личная рума на месяц", value="2000 <:white_star:1226746455214264381>", inline=False)
    embed.add_field(name="Роль на месяц", value="3500 <:white_star:1226746455214264381>", inline=False)
    embed.add_field(name="Роль на 3 месяца", value="5000 <:white_star:1226746455214264381>", inline=False)
    embed.add_field(name="Роль на год", value="20000 <:white_star:1226746455214264381>", inline=False)
    embed.add_field(name="Возможность ставить статусы войсов", value="5000 <:white_star:1226746455214264381>", inline=False)
    embed.add_field(name="Повысить уровень 1 раз", value="1000 <:white_star:1226746455214264381> (каждый раз коэффицент платы умножается на 1,1%)", inline=False)
    embed.add_field(name="Герб клана", value="9000 <:white_star:1226746455214264381> ( значок роли клана, баннер в листе кланов )", inline=False)
    embed.add_field(name="Герб команды", value="8000 <:white_star:1226746455214264381> (значок роли команды, баннер в листе команд )", inline=False)
    embed.add_field(name="Заказать ивент", value="500 <:white_star:1226746455214264381>", inline=False)
    embed.add_field(name="+1 success в розыгрышах", value="7000 <:white_star:1226746455214264381> ( одноразово )", inline=False)

    view = MyEmbedOnShop(timeout=None)
    await ctx.send(embed=embed, view=view)

class MyEmbedOnShop(discord.ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_item = None

    @discord.ui.button(emoji="<:white_star:1226746455214264381>", label="Личная рума на месяц", style=discord.ButtonStyle.gray)
    async def button_Magazin1_callback(self, interaction: discord.Interaction, button: discord.Button):
        await buy_item(interaction, 1, 2000, "личный канал на месяц", interaction.guild)

    @discord.ui.button(emoji="<:white_star:1226746455214264381>", label="Роль на месяц", style=discord.ButtonStyle.gray)
    async def button_Magazin2_callback(self, interaction: discord.Interaction, button: discord.Button):
        await buy_item(interaction, 2, 3500, "роль на месяц", interaction.guild)

    @discord.ui.button(emoji="<:white_star:1226746455214264381>", label="Роль на 3 месяца", style=discord.ButtonStyle.gray)
    async def button_Magazin3_callback(self, interaction: discord.Interaction, button: discord.Button):
        await buy_item(interaction, 3, 5000, "роль на 3 месяца", interaction.guild)

    @discord.ui.button(emoji="<:white_star:1226746455214264381>", label="Роль на год", style=discord.ButtonStyle.gray)
    async def button_Magazin4_callback(self, interaction: discord.Interaction, button: discord.Button):
        await buy_item(interaction, 4, 20000, "роль на год", interaction.guild)

    @discord.ui.button(emoji="<:white_star:1226746455214264381>", label="Возможность ставить статусы войсов", style=discord.ButtonStyle.gray)
    async def button_Magazin5_callback(self, interaction: discord.Interaction, button: discord.Button):
        await buy_item(interaction, 5, 5000, "возможность ставить смайлы в войсах", interaction.guild)

    @discord.ui.button(emoji="<:white_star:1226746455214264381>", label="Повысить уровень 1 раз", style=discord.ButtonStyle.gray)
    async def button_Magazin6_callback(self, interaction: discord.Interaction, button: discord.Button):
        await buy_item(interaction, 6, 1000, "повышение уровня 1 раз", interaction.guild)

    @discord.ui.button(emoji="<:white_star:1226746455214264381>", label="Герб клана", style=discord.ButtonStyle.gray)
    async def button_Magazin7_callback(self, interaction: discord.Interaction, button: discord.Button):
        await buy_item(interaction, 7, 9000, "герб клана", interaction.guild)

    @discord.ui.button(emoji="<:white_star:1226746455214264381>", label="Герб команды", style=discord.ButtonStyle.gray)
    async def button_Magazin8_callback(self, interaction: discord.Interaction, button: discord.Button):
        await buy_item(interaction, 8, 8000, "герб команды", interaction.guild)

    @discord.ui.button(emoji="<:white_star:1226746455214264381>", label="Заказать ивент", style=discord.ButtonStyle.gray)
    async def button_Magazin9_callback(self, interaction: discord.Interaction, button: discord.Button):
        await buy_item(interaction, 9, 500, "заказ ивента", interaction.guild)

    @discord.ui.button(emoji="<:white_star:1226746455214264381>", label="+1 success в розыгрышах", style=discord.ButtonStyle.gray)
    async def button_Magazin10_callback(self, interaction: discord.Interaction, button: discord.Button):
        await buy_item(interaction, 10, 7000, "+1 success в розыгрышах", interaction.guild)


#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#модальное окно надо разобраться 


































@bot.command()
async def kaiden(ctx):
    # Отправка сообщения с кастомным эмодзи
    await ctx.send('<:kaiden:1229183685706780774>')
    # Удаление сообщения пользователя через 1 секунду
    await asyncio.sleep(0.001)
    await ctx.message.delete()



#////////////////////////////////////////////////////////////////////////////////////////////////////////////


messages_cache = {} 

@bot.event
async def on_ready():
    print('Bot online')


      






@bot.command()
async def send_role_embed(ctx):
    channel_id_role = 1211069574435442710
    channel_role = bot.get_channel(channel_id_role)
    if channel_role:
        embed_role = discord.Embed(
            title="Привет! Выбирай роль, что ты будешь у нас смотреть 😃",
            description="🎬 - фильмы\n🎌 - аниме\n📺 - сериал\n🎵 - музыка\n🎥 - ютуб\n💖 - дорамы",
            color=discord.Color.orange()
        )
        message_role = await channel_role.send(embed=embed_role)
        for emoji in ['🎬', '🎌', '📺', '🎵', '🎥', '💖']:
            await message_role.add_reaction(emoji)

        def check(reaction, user):
            return user != bot.user and reaction.message == message_role

        while True:
            reaction, user = await bot.wait_for('reaction_add', check=check)
            roles = {
                '🎬': 'фильмы',
                '🎌': 'аниме',
                '📺': 'сериалы',
                '🎵': 'музыка',
                '🎥': 'ютуб',
                '💖': 'дорамы'
            }
            role_name = roles.get(reaction.emoji)
            if role_name:
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                if role:
                    await user.add_roles(role)
                    msg = await channel_role.send(f"Роль {role.name} добавлена пользователю {user.display_name}!")
                    await asyncio.sleep(10)  # Таймер на 10 секунд
                    await msg.delete()  # Удаление сообщения после таймера
                
                  







class MyWatchingRolesView(discord.ui.View):
    async def on_timeout(self):
        for child in self.children:
            await child.delete()

    async def process_role_interaction(self, interaction, role_id):
        member = interaction.user
        role = interaction.guild.get_role(role_id)
        if role:
            if role in member.roles:
                await member.remove_roles(role)
                msg = await interaction.response.send(f"Роль {role.name} успешно удалена!", ephemeral=True)
            else:
                await member.add_roles(role)
                msg = await interaction.response.send(f"Роль {role.name} успешно добавлена!", ephemeral=True)
            
            # Устанавливаем таймер на удаление сообщения через 5 секунд
            asyncio.create_task(self.delete_message(msg))
        else:
            await interaction.response.send(f"Ошибка: Роль {role_id} не найдена.", ephemeral=True)

    async def delete_message(self, message, delay=5):
        await asyncio.sleep(delay)
        await message.delete()

 

    @discord.ui.button(emoji="<a:1aredflame:1181639398454992946>",label="Фильмы", style=discord.ButtonStyle.gray)
    async def button_film_callback(self, interaction, button):  
        role_id = 1211759033699008533  # ID вашей роли "rust"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        
        if role in interaction.user.roles:  # Проверяем, есть ли роль у пользователя
            await interaction.user.remove_roles(role)  # Удаляем роль
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)  # Добавляем роль
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)





    @discord.ui.button(emoji="<a:2aFire:1180949816008769546>", label="Аниме", style=discord.ButtonStyle.gray)
    async def button_anime_callback(self, interaction, button):
        role_id = 1211759073834573884  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)





    @discord.ui.button(emoji="<a:3aFlame:1180949795561549934>", label="Сериал", style=discord.ButtonStyle.gray)
    async def button_serial_callback(self, interaction, button):
        role_id = 1211758993635151922  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)





    @discord.ui.button(emoji="<a:4aSizceVideoNaslOlmu:1180949687457562674>", label="Музыка", style=discord.ButtonStyle.gray)
    async def button_mysika_callback(self, interaction, button):
        role_id = 1211763123917430864  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)






    @discord.ui.button(emoji="<a:5aPurpleflam:1180949698786361354>", label="Ютуб", style=discord.ButtonStyle.gray)
    async def button_yootube_callback(self, interaction, button):
        role_id = 1211759159196782672  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)



    @discord.ui.button(emoji="<a:6aDeja_Pink_Fire:1181140518562963486>", label="Дорамы", style=discord.ButtonStyle.gray)
    async def button_dorami_callback(self, interaction, button):
         role_id = 1211759119913193572  # ID вашей роли "пук"
         role = discord.utils.get(interaction.guild.roles, id=role_id)
    
         if role in interaction.user.roles:
             await interaction.user.remove_roles(role)
             embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
             await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
         else:
             await interaction.user.add_roles(role)
             embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
             await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
    



@bot.command()
async def send_Watch_role_embed(ctx):
    channel_id_role = 1234331702457798716
    channel_role = bot.get_channel(channel_id_role)
    if channel_role:
        embed_role = discord.Embed(
            title="Привет! Выбирай смотровую роль, чтобы получать обновления по просмотру 😃",
            description="Выбери реакцию под жанром, который тебя интересует:",
            color=discord.Color.blue()
        )
        view = MyWatchingRolesView(timeout=None)  # Установить тайм-аут в None для бесконечного времени
        message_role = await channel_role.send(embed=embed_role, view=view)





































@bot.command()
async def nom(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return

    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/nom'))
    
    
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} укусил {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)
    
    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)


@bot.command()
async def wtf(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/wtf'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/wtf/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} в ахуе с {user2}"

    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)

@bot.command()
async def shy(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/chy'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/chy/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} стесняется {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)

@bot.command()
async def kiss(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/kiss'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/kiss/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} поцеловал {user2}"

    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def angry(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/angry'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/angry/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} злиться на {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def bann(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/bann'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/bann/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} кинул в бан {user2}"

    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def cry(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/cry'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/cry/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} был растроган {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def dance(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/dance'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/dance/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} танцует для {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def flower(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/flower'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/flower/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} подарил цветочек {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)

@bot.command()
async def funny(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/funny'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/funny/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} веселит {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def hearts(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/hearts'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/hearts/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} очарован {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def hug(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/hug'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/hug/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} обнял {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def kickk(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/kick'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/kick/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} ударил {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def kill(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/kill'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/kill/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} убил {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def smile(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/smile'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/smile/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} улыбается с {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def sorry(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/sorry'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/sorry/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} просит прощения у {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
@bot.command()
async def sex(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/sex'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/sex/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} соблазняет {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)

@bot.command()
async def flirt(ctx, member: discord.Member, *, message: str = None):
    if ctx.channel.id != 1212783317817106442:
        await ctx.send("Извините, эта команда может быть использована только в определенном канале.")
        return
    random_gif = random.choice(os.listdir('C:/Users/1/Desktop/discord_bot_funcomm/gif/flirt'))
    file = discord.File(f'C:/Users/1/Desktop/discord_bot_funcomm/gif/flirt/{random_gif}', filename=random_gif)
    
    user1 = ctx.author.mention
    user2 = member.mention
    
    embed = discord.Embed()
    embed.description = f"{user1} флиртует с {user2}"
    
    if message:
        embed.add_field(name="Message", value=message)

    embed.set_image(url=f"attachment://{random_gif}")
    
    await ctx.send(file=file, embed=embed)
















# ембед для выбора просмотра.../////////////////////////////////////////////////////////////////////////////////////

@bot.command()
async def create_contest(ctx):
    questions = [
        "**название чего будите смотреть**",
        "**Длительность просмотра**",
        "**во сколько начало?**",
        "**Описание**",
        "**Приз за просмотр**",
        "**Прикрепите фотографию того что будите смотреть**",
        "**Какую роль вы хотите позвать? (Выберите один вариант)**",
    ]
    
    answers = {}

    # Создание цветов для текста и фона
    colors = [discord.Color.red(), discord.Color.orange(), discord.Color.gold(), discord.Color.green(), discord.Color.blue(), discord.Color.purple()]

    for i, question in enumerate(questions):
        await ctx.send(f" {question}:")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        if question == "**Прикрепите фотографию того что будите смотреть**":
            response = await bot.wait_for('message', check=check)
            attachment = response.attachments[0]  # Получаем первое вложение из сообщения
            answers[question] = attachment.url  # Получаем URL вложения и сохраняем его в ответах
        elif question == "**Какую роль вы хотите позвать? (Выберите один вариант)**":
            message = await ctx.send("**Какую роль вы хотите позвать? (Выберите один вариант)**")
            for emoji in ["🎬", "🎌", "📺", "🎵", "🎥", "💖"]:
                await message.add_reaction(emoji)
            reaction, user = await bot.wait_for("reaction_add", check=lambda r, u: u == ctx.author and str(r.emoji) in ["🎬", "🎌", "📺", "🎵", "🎥", "💖"])
            answers[question] = str(reaction.emoji)
        else:
            response = await bot.wait_for('message', check=check)
            answers[question] = response.content
    
    # Создание эмбеда с рандомным цветом фона и текста
    color_index = random.randint(0, len(colors) - 1)
    embed = discord.Embed(title="Сегодня у нас в программе", color=colors[color_index])
    
    for question, answer in answers.items():
        if question == "**Прикрепите фотографию того что будите смотреть**":
            embed.set_image(url=answer)  # Добавляем изображение в embed
        elif question == "**Длительность просмотра**":
            duration_question = question
            duration_answer = answer
        elif question == "**во сколько начало?**":
            start_time_question = question
            start_time_answer = answer
        elif question == "**Какую роль вы хотите позвать? (Выберите один вариант)**":
            role = answer
            if role == "🎬":
                await ctx.send(f"{ctx.author.mention}, вы выбрали роль 🎬")
                role_name = "**🎬**"
            elif role == "🎌":
                role_name = "**🎌**"
            elif role == "📺":
                role_name = "**📺**"
            elif role == "🎵":
                role_name = "**🎵**"
            elif role == "🎥":
                role_name = "**🎥**"
            elif role == "💖":
                role_name = "**💖**"
            # Переход к следующей итерации цикла, чтобы не добавлять это поле в эмбед
            continue
        elif question == "**название чего будите смотреть**":
            embed.title = f"**{answer}**"  # Изменяем заголовок эмбеда
            continue
        elif question == "**Описание**":
            # Изменяем имя поля и добавляем описание
            embed.add_field(name="**Описание**", value=answer, inline=False)
            continue
        else:
            embed.add_field(name=question, value=answer, inline=False)
            


# Add both questions in a single line with black borders
    embed.add_field(name=f" {duration_question}  \u2502  {start_time_question} ",
                value=f"{duration_answer} \u2502 {start_time_answer}", inline=False)

    # Add visual separator as a blank field
    embed.add_field(name="\u200b", value="\u200b", inline=False)

    # Add a line below the embed titled "ведущий" and ping the user who executed the command
    embed.add_field(name="Ведущий", value=ctx.author.mention, inline=False)

    channel = bot.get_channel(1211069278963376158)  # Замените YOUR_CHANNEL_ID на ID канала, куда нужно отправить эмбед
    message = await channel.send(embed=embed)
    # Отправляем сообщение с пингом ролей
    role_mapping = {
        "🎬": 1211759033699008533,
        "🎌": 1211759073834573884,
        "📺": 1211758993635151922,
        "🎵": 1211763123917430864,
        "🎥": 1211759159196782672,
        "💖": 1211759119913193572
    }
    role = answers.get("**Какую роль вы хотите позвать? (Выберите один вариант)**")
    if role:
        role_id = role_mapping.get(role)
        if role_id:
            await channel.send(f"Заходите быстрее ребятки! {role} <@&{role_id}>")
# /////////////////////////////////////////////////////////////////////////////////////


# Путь к директории с изображениями
IMAGE_MOR = r"C:\Users\1\Desktop\discord_bot_funcomm\img\morning"
IMAGE_NIGHT = r"C:\Users\1\Desktop\discord_bot_funcomm\img\night"

async def send_greetings():
    while True:
        now = datetime.now().time()
        print(f"Bot is running at: {now}")  # Добавляем вывод текущего времени в консоль
        if now >= datetime.strptime("1:00:10", "%H:%M:%S").time() and now < datetime.strptime("2:00:10", "%H:%M:%S").time():
            channel = bot.get_channel(1135614238937858189)
            await send_night_message(channel)
            await asyncio.sleep(3600)  # Подождать час перед отправкой следующего сообщения
        elif now >= datetime.strptime("08:00:00", "%H:%M:%S").time() and now < datetime.strptime("09:00:00", "%H:%M:%S").time():
            channel = bot.get_channel(1135614238937858189)
            await send_morning_message(channel)
            await asyncio.sleep(3600)  # Подождать час перед отправкой следующего сообщения
        else:
            await asyncio.sleep(60)  # Проверять время каждую минуту

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await send_greetings()

@bot.command()
async def send_morning(ctx):
    channel = ctx.channel
    await send_morning_message(channel)

@bot.command()
async def send_night(ctx):
    channel = ctx.channel
    await send_night_message(channel)

async def send_morning_message(channel):
    embed = discord.Embed(
        title="Доброе утро, врубай монитор!",
        description="Хорошего дня и продуктивных дел. Пусть день будет хорошим с М&U <:pink:1180948527958995096>",
        color=0xE28686
    )
    file_name = random.choice(os.listdir(IMAGE_MOR))
    file_path = os.path.join(IMAGE_MOR, file_name)
    file = discord.File(file_path, filename="image.png")
    embed.set_image(url="attachment://image.png")
    await channel.send(embed=embed, file=file)

async def send_night_message(channel):
    embed = discord.Embed(
        title="Сладких снов, гаси морду!",
        description="Не засиживайся допоздна, мама пизды даст <:pink:1180948527958995096>",
        color=0xCF97D3
    )
    file_name = random.choice(os.listdir(IMAGE_NIGHT))
    file_path = os.path.join(IMAGE_NIGHT, file_name)
    file = discord.File(file_path, filename="image.png")
    embed.set_image(url="attachment://image.png")
    await channel.send(embed=embed, file=file)



#//////////////////////////////////////////////////////////////////////////////////////////////////







# Функция для поиска трека (заглушка)
async def search_track(query):
    # Здесь можно реализовать логику поиска трека через API музыкальных сервисов
    # В этом примере используем заглушку
    track_name = "Название трека"
    track_url = "https://example.com"
    track_image = "https://example.com/image.jpg"
    track_audio = "https://example.com/audio.mp3"

    return track_name, track_url, track_image, track_audio

@bot.command()
async def music(ctx, *, query):
    try:
        # Ищем трек по запросу
        track_name, track_url, track_image, track_audio = await search_track(query)

        # Создаем Embed с информацией о треке
        embed = discord.Embed(title=track_name, url=track_url)
        embed.set_thumbnail(url=track_image)
        embed.add_field(name="Ссылка на аудио", value=track_audio)

        # Создаем кнопки для управления треком
        buttons = [
            {"emoji": "▶️", "label": "Воспроизвести", "style": 1},
            {"emoji": "⏸️", "label": "Пауза", "style": 2},
            {"emoji": "⏹️", "label": "Стоп", "style": 3}
        ]

        # Отправляем сообщение с Embed и кнопками
        message = await ctx.send(embed=embed, components=[buttons])

        # Функция для обработки нажатий на кнопки
        async def button_callback(interaction):
            # Проверяем, что нажатие произошло на нашем сообщении
            if interaction.message.id == message.id:
                if interaction.custom_id == "play_button":
                    # Логика воспроизведения трека
                    await interaction.respond(type=6)  # Отмечаем нажатие
                elif interaction.custom_id == "pause_button":
                    # Логика паузы трека
                    await interaction.respond(type=6)
                elif interaction.custom_id == "stop_button":
                    # Логика остановки трека
                    await interaction.respond(type=6)

        # Ожидаем нажатий на кнопки
        while True:
            try:
                interaction = await bot.wait_for("button_click", timeout=60)
                await button_callback(interaction)
            except asyncio.TimeoutError:
                # Если время ожидания истекло, убираем кнопки
                await message.edit(components=None)
                break

    except Exception as e:
        await ctx.send(f"Произошла ошибка при поиске трека: {e}")

#/////////////////////////////////////////////
















#///////////////////////////////


class MyView(discord.ui.View):
    @discord.ui.button(label="ДА!", style=discord.ButtonStyle.green)
    async def button_yes_callback(self, interaction, button):
        role_id = 1137318254306668635  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        await interaction.user.add_roles(role)
        embed = discord.Embed(description="Тебе выдана роль пук", color=0x00FF00)
        await interaction.response.send_message(embed=embed)
    
    @discord.ui.button(label="НЕТ!", style=discord.ButtonStyle.red)
    async def button_no_callback(self, interaction, button):
        await interaction.message.delete()



@bot.command()
async def pyk(ctx):
    embed = discord.Embed(title="ВАРЯ ПУКАЕТ", color=0xFF5733)
    message = await ctx.send(embed=embed)

    # Создаем View (представление) с кнопками
    view = MyView()

    # Отправляем сообщение с кнопками
    await message.edit(view=view)

    def check(interaction):
        return interaction.message.id == message.id and interaction.user == ctx.author

    try:
        interaction = await bot.wait_for('button_click', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await message.delete()
    else:
        if interaction.component.label == 'НЕТ!':
            await message.delete()

#////////////////////////////////////////////////////////////////////////////////


class MyGameRolesView(discord.ui.View):
    async def on_timeout(self):
        for child in self.children:
            await child.delete()

    async def process_role_interaction(self, interaction, role_id):
        member = interaction.user
        role = interaction.guild.get_role(role_id)
        if role:
            if role in member.roles:
                await member.remove_roles(role)
                msg = await interaction.response.send(f"Роль {role.name} успешно удалена!", ephemeral=True)
            else:
                await member.add_roles(role)
                msg = await interaction.response.send(f"Роль {role.name} успешно добавлена!", ephemeral=True)
            
            # Устанавливаем таймер на удаление сообщения через 5 секунд
            asyncio.create_task(self.delete_message(msg))
        else:
            await interaction.response.send(f"Ошибка: Роль {role_id} не найдена.", ephemeral=True)

    async def delete_message(self, message, delay=5):
        await asyncio.sleep(delay)
        await message.delete()

 

    @discord.ui.button(emoji="<:emoji_146:1234381047517417504>",label="rust", style=discord.ButtonStyle.gray)
    async def button_Rust_callback(self, interaction, button):  
        role_id = 1168339239549804765  # ID вашей роли "rust"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        
        if role in interaction.user.roles:  # Проверяем, есть ли роль у пользователя
            await interaction.user.remove_roles(role)  # Удаляем роль
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)  # Добавляем роль
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="<:emoji_149:1234849146976993290>", label="Cs2", style=discord.ButtonStyle.gray)
    async def button_CS2_callback(self, interaction, button):
        role_id = 1137318254306668635  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="<:emoji_146:1234382294177808384>", label="Dota2", style=discord.ButtonStyle.gray)
    async def button_Dota2_callback(self, interaction, button):
        role_id = 1137318378860720159  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="<:emoji_151:1234393821916299336>", label="VALORANT", style=discord.ButtonStyle.gray)
    async def button_VALORANT_callback(self, interaction, button):
        role_id = 1137318421642621010  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="<:emoji_150:1234393789087481857>", label="Left4Dead2", style=discord.ButtonStyle.gray)
    async def button_Left4Dead2_callback(self, interaction, button):
        role_id = 1174776190083543180  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="<:emoji_152:1234393840345944066>", label="Fortnite", style=discord.ButtonStyle.gray)
    async def button_Fortnite_callback(self, interaction, button):
        role_id = 1146538464435777627  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="<:emoji_150:1234393805361512481>", label="Apex", style=discord.ButtonStyle.gray)
    async def button_Apex_callback(self, interaction, button):
        role_id = 1168347348359983144  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="<:emoji_147:1234389670679281695>", label="Genshin Impact", style=discord.ButtonStyle.gray)
    async def button_GenshinImpact_callback(self, interaction, button):
        role_id = 1137318461203304510  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
    @discord.ui.button(emoji="<:emoji_148:1234390328694538331>", label="Terraria", style=discord.ButtonStyle.gray)
    async def button_Terraria_callback(self, interaction, button):
        role_id = 1137318442614136862  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="<:emoji_149:1234393768380071946>", label="Gta", style=discord.ButtonStyle.gray)
    async def button_gta_callback(self, interaction, button):
        role_id = 1234895900891943092  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="<:emoji_151:1234985938170544282>", label="Фан", style=discord.ButtonStyle.gray)
    async def button_Fan_callback(self, interaction, button):
        role_id = 1137318517985792044  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)


@bot.command()
async def send_game_role_embed(ctx):
    channel_id_role = 1234331702457798716
    channel_role = bot.get_channel(channel_id_role)
    if channel_role:
        embed_role = discord.Embed(
            title="Привет! Выбирай игровую роль, чтобы получать обновления по играм 😃",
            description="Выбери реакцию под игрой, которую ты играешь или интересуешься:",
            color=discord.Color.blue()
        )
        view = MyGameRolesView(timeout=None)  # Установить тайм-аут в None для бесконечного времени
        message_role = await channel_role.send(embed=embed_role, view=view)
#////////////////////////////////////////////////////////////////////////////////////////////////////////



















class GenderRoleSelectionView(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.value = None

    async def get_role_by_name(self, guild, name):
        """Поиск роли по имени."""
        roles = await guild.roles.fetch()
        for role in roles:
            if role.name.lower() == name.lower():
                return role
        return None

    @discord.ui.button(emoji="<:emoji_161:1236482405737435267>", label="Мужской", style=discord.ButtonStyle.gray)
    async def button_Mans_callback(self, interaction, button):
        role_id = 1260553327255748628  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    @discord.ui.button(emoji="<:emoji_160:1236482512264364072>", label="Женский", style=discord.ButtonStyle.gray)
    async def button_Girls_callback(self, interaction, button):
        role_id = 1260553771864293529  # ID вашей роли "пук"
        role = discord.utils.get(interaction.guild.roles, id=role_id)
    
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = discord.Embed(description=f"Удалена роль {role.name}", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
        else:
            await interaction.user.add_roles(role)
            embed = discord.Embed(description=f"Тебе выдана роль {role.name}", color=0x00FF00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.user

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

@bot.command()
async def select_gender(ctx):
    view = GenderRoleSelectionView(user=ctx.author)
    embed = discord.Embed(title="Выберите свой гендер", description="Нажмите на кнопку, соответствующую вашему гендеру:", color=discord.Color.blue())
    await ctx.send(embed=embed, view=view)



































#////////////////////////////////////////////////////////////////////////////////////////////////////////

@bot.command()
async def pin_embed_message(ctx):
    channel = ctx.channel
    
    # Создаем embed сообщение
    embed = discord.Embed(title="Ребята, мы предоставляем вам возможность заработать денюжку под нашим руководством", description=" Все что нужно сделать это прожать реакцию и вам откроется новая категория! ❤ \n Работа очень простая и вам не требуется особых знаний, вам понравится работать с нами а также получите прибыль!  \n  Жмите ⬇️", color=discord.Color.green())
    
    # Добавляем уникальное значение к embed сообщению
    embed.set_footer(text="pin_embed_message")
    
    # Отправляем embed сообщение в канал
    message = await channel.send(embed=embed)
    
    # Добавляем реакцию к сообщению
    await message.add_reaction('🤑')

    await ctx.send('Embed сообщение успешно отправлено в этот канал!')

@bot.event
async def on_raw_reaction_add(payload):
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    
    if message.embeds and message.embeds[0].footer.text == 'pin_embed_message' and str(payload.emoji) == '🤑':
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = discord.utils.get(guild.roles, name='worker')
        await member.add_roles(role)
        await member.send("Роль 'worker' успешно выдана!")
#////////////////////////////////////////////////////////////////////////////////////////////////////////









tickets = {}

class MyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label="Go to Ticket", emoji="<a:AI_verify_certified_owo_lol_anim:1143805327519797259>")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        author = interaction.user
        ticket_channel = await create_ticket(guild, author)
        tickets[author.id] = ticket_channel
        await interaction.response.send_message("Ticket created successfully! You've been redirected to your ticket channel.", ephemeral=True)
        await interaction.user.send(f"Your ticket channel has been created: {ticket_channel.mention}")

class TicketsButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MyButton())

async def create_ticket(guild, author):
    category = discord.utils.get(guild.categories, name='Tickets')
    if category is None:
        category = await guild.create_category('Tickets')
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.get_role(1211613392624681002): discord.PermissionOverwrite(read_messages=True, mention_everyone=True)  # Добавляем разрешение на упоминание
    }
    
    ticket_channel = await category.create_text_channel(f'ticket-{author.name}', overwrites=overwrites)
    
    # Установка прав доступа только для автора тикета
    await ticket_channel.set_permissions(author, read_messages=True, send_messages=True)
    
    embed = discord.Embed(title="Привет!", description="Опиши свою проблему и админ постарается её решить.", color=0x00ff00)
    
    await ticket_channel.send(embed=embed)
    
    admin_role = guild.get_role(1211613392624681002)
    admin_mention = f"{admin_role.mention} Помогите, пожалуйста!"
    
    await ticket_channel.send(admin_mention)
    
    return ticket_channel

@bot.command()
async def createticket(ctx):
    embed = discord.Embed(title="Создать Тикет", description="Если у вас есть жалоба, вопрос или срочная ситуация, свяжитесь с администрацией прямо сейчас <:white_arrow1:1227383482481770546> <:white_arrow1:1227383482481770546> <:white_arrow1:1227383482481770546>", color=discord.Color.blue())
    view = TicketsButton()
    await ctx.send(embed=embed, view=view)

@bot.command()
async def closeticket(ctx):
    ticket_channel = tickets.get(ctx.author.id)
    if ticket_channel:
        # Проверяем разрешение на отправку сообщений в канал тикета
        if ctx.author.top_role == ctx.guild.get_role(1211613392624681002):
            await ticket_channel.delete()
            del tickets[ctx.author.id]
            await ctx.send("Ticket closed successfully!")
        else:
            await ctx.send("You don't have permission to close this ticket.")
    else:
        await ctx.send("You don't have an open ticket.")


#///////////////////////////////////////////////////////////////////////////////////////////







# def calculate_required_hp(level):
#     base_hp = 100
#     hp_increase_percentage = 0.1
#     return base_hp + (base_hp * hp_increase_percentage) * (level - 1)

# @tasks.loop(seconds=3600)
# async def add_hourly_hp():
#     now = datetime.utcnow()
#     for guild in bot.guilds:
#         for channel in guild.text_channels:
#             if isinstance(channel, discord.TextChannel):  # Исправлено условие для проверки типа канала
#                 for member in channel.members:
#                     with open('users.json', 'r+') as f:
#                         try:
#                             users = json.load(f)
#                         except json.JSONDecodeError:
#                             users = {'users': {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0}}
#                             f.seek(0)
#                             json.dump(users, f, indent=4)
#                             f.truncate()

#                         user_id = str(member.id)
#                         user_data = users.get(user_id, {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0})
#                         user_data['hp'] += 70
#                         users[user_id] = user_data
#                         f.seek(0)
#                         json.dump(users, f, indent=4)
#                         f.truncate()

# @bot.event
# async def on_ready():
#     print(f'We have logged in as {bot.user}')
#     add_hourly_hp.start()
#     try:
#         with open('balances.json', 'x') as f:
#             json.dump({}, f)
#     except FileExistsError:
#         pass

# @bot.command()
# async def level(ctx, member: discord.Member = None):
#     if member is None:
#         member = ctx.author
#     with open('users.json', 'r') as f:
#         try:
#             users = json.load(f)
#         except json.JSONDecodeError:
#             users = {'users': {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0}}
#             f.seek(0)
#             json.dump(users, f, indent=4)
#             f.truncate()

#     user_data = users.get(str(member.id), {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0})
#     await ctx.send(f'Уровень пользователя {member.name}: {user_data["level"]}, HP: {user_data["hp"]}')

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     with open('users.json', 'r+') as f:
#         try:
#             users = json.load(f)
#         except json.JSONDecodeError:
#             users = {'users': {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0}}
#             f.seek(0)
#             json.dump(users, f, indent=4)
#             f.truncate()
        

#         user_id = str(message.author.id)
#         user_data = users.get(user_id, {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0})

#         if not any(msg.content for msg in users.get(user_id, {}).get('messages', [])):
#             user_data['hp'] += 50

#         user_data['messages'].append(message.content)
#         users[user_id] = user_data
#         user_data['hp'] += 5

#         if user_data['hp'] >= calculate_required_hp(user_data['level']):
#             user_data['hp'] -= calculate_required_hp(user_data['level'])
#             user_data['level'] += 1
#             user_data['hp'] += user_data['hp'] * 0.1
#             user_data['stars'] += 100

#         users[user_id] = user_data

#         if message.guild and isinstance(message.channel, discord.TextChannel):  # Исправлено условие для проверки типа канала
#             user_data['hp'] += 90
#             users[user_id] = user_data

#         f.seek(0)
#         json.dump(users, f, indent=4)
#         f.truncate()

#     await bot.process_commands(message)

# @bot.command()
# async def achievement(ctx, achievement_name: str):
#     with open('users.json', 'r+') as f_users:
#         try:
#             users = json.load(f_users)
#         except json.JSONDecodeError:
#             users = {'users': {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0}}
#             f_users.seek(0)
#             json.dump(users, f_users, indent=4)
#             f_users.truncate()

#         user_id = str(ctx.author.id)
#         user_data = users.get(user_id, {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0})

#         if achievement_name.lower() == "30lvl":
#             user_data['level'] = 30
#             user_data['achievements'].append(achievement_name)
#             user_data['stars'] += 1000
#         elif achievement_name.lower() == "50lvl":
#             user_data['level'] = 50
#             user_data['achievements'].append(achievement_name)
#             user_data['stars'] += 2000
#         elif achievement_name.lower() == "70lvl":
#             user_data['level'] = 70
#             user_data['achievements'].append(achievement_name)
#             user_data['stars'] += 5000
#         elif achievement_name.lower() == "100lvl":
#             user_data['level'] = 100
#             user_data['achievements'].append(achievement_name)
#             user_data['stars'] += 10000
#         else:
#             await ctx.send("Неверное имя достижения.")
#             return

#         users[user_id] = user_data
#         f_users.seek(0)
#         json.dump(users, f_users, indent=4)
#         f_users.truncate()

#     await ctx.send(f"Достижение '{achievement_name}' добавлено. Теперь у вас {user_data['stars']} звездочек.")

# @bot.command()
# async def weekly_bonus(ctx):
#     with open('users.json', 'r+') as f:
#         try:
#             users = json.load(f)
#         except json.JSONDecodeError:
#             users = {'users': {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0}}
#             f.seek(0)
#             json.dump(users, f, indent=4)
#             f.truncate()

#         for user_id, user_data in users.items():
#             user_data['hp'] += 50
#             users[user_id] = user_data

#         f.seek(0)
#         json.dump(users, f, indent=4)
#         f.truncate()

#     await ctx.send("Еженедельный бонус к HP успешно добавлен.")

# @bot.command()
# async def bio_setup(ctx):
#     await ctx.send("Био успешно оформлено.")

# @bot.command()
# async def premium_role(ctx):
#     await ctx.send("Премиум роль успешно присвоена.")

# @bot.command()
# async def embed(ctx):
#     embed = discord.Embed(title="Нажми на кнопку!", description="Получишь +120 HP!")
#     button = discord.ui.Button(style=discord.ButtonStyle.green, label="Нажми здесь")
#     view = discord.ui.View()
#     view.add_item(button)
#     await ctx.send(embed=embed, view=view)

#     def check(interaction):
#         return interaction.user == ctx.author

#     await bot.wait_for("interaction_add", check=check)  # Исправлено событие на "interaction_add"
#     user_id = str(ctx.author.id)
#     with open('users.json', 'r+') as f:
#         try:
#             users = json.load(f)
#         except json.JSONDecodeError:
#             users = {'users': {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0}}
#             f.seek(0)
#             json.dump(users, f, indent=4)
#             f.truncate()

#         user_data = users.get(user_id, {'level': 1, 'hp': 100, 'achievements': [], 'stars': 0})
#         user_data['hp'] += 120
#         users[user_id] = user_data
#         f.seek(0)
#         json.dump(users, f, indent=4)
#         f.truncate()
#     await ctx.send(f"Поздравляем Вы получили +120 HP.")

#////////////////////////////////////////////////////////////////////////////////////////////







#//////////////////////////////////////////////////////////////////////////////////////////

bot.run(config['token'])


