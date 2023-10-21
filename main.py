import discord
from discord.ext import commands
from datetime import datetime, timedelta

# configuration
TOKEN = 'YOUR_BOT_TOKEN'
PREFIX = '!'
LURKER_ROLE_NAME = 'Lurker'
INACTIVE_THRESHOLD = 7

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    # track time of last message
    await bot.process_commands(message)
    user = message.author
    last_message_time = user.created_at
    for msg in await user.history(limit=None).flatten():
        if msg.created_at > last_message_time:
            last_message_time = msg.created_at
    time_difference = datetime.now() - last_message_time

    # check user for lurker role
    if time_difference.days >= INACTIVE_THRESHOLD:
        lurker_role = discord.utils.get(message.guild.roles, name=LURKER_ROLE_NAME)
        await user.add_roles(lurker_role)
    else:
        lurker_role = discord.utils.get(message.guild.roles, name=LURKER_ROLE_NAME)
        await user.remove_roles(lurker_role)

bot.run(TOKEN)
