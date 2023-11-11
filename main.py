import discord
from discord.ext import commands
from decouple import config
from datetime import timedelta, datetime
import time

# configuration
token = config('TOKEN')
channel_id = config('CHANNEL_ID')
prefix = '!'
lurker_role = 'lurker'
trust_role_name = 'trust'
inactive_threshold = 10

run_at = datetime.now() + timedelta(days=30)
delay = (run_at - datetime.now()).total_seconds()

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents)


@bot.command()
async def members(ctx) -> None:
    """ This is a test method for now, just to see how scheduling system in discord library works """
    print('Members:')
    for guild in bot.guilds:
        for member in guild.members:
            print(member)


@bot.event
async def on_ready():
    """ Connecting bot to discord server """
    print(f'{bot.user.name} has connected to Discord!')
    while True:
        channel = bot.get_channel(int(channel_id))
        if channel:
            dummy_ctx = await bot.get_context(await channel.fetch_message(channel.last_message_id))
            await bot.get_command('members').invoke(dummy_ctx)
        time.sleep(15)  # only for testing


@bot.command()
async def get_roles(ctx) -> list:
    """ Getting user's roles """
    # add members
    server = ctx.guild
    member = ctx.author  # command author

    # add existing roles
    roles = member.roles

    # return roles
    role_names = [role.name for role in roles]
    await ctx.send(f'{member.name} has roles: {", ".join(role_names)}')
    return role_names


@bot.event
async def on_message(message):
    """ Method getting triggered when user sends a message """
    # check if user has lurker role and remove it

    # track time of last message
    await bot.process_commands(message)
    user = message.author
    print(user)
    if lurker_role in user.roles:
        await user.remove_role(lurker_role)


@bot.command()
async def invite(ctx):
    """ Generate invite link """
    link = await ctx.channel.create_invite()
    await ctx.send(link)

bot.run(token)
