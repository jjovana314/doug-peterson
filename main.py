import discord
from discord.ext import commands
from decouple import config
from datetime import timedelta, datetime
import time

# configuration
token = config('TOKEN')
channel_id = config('CHANNEL_ID')
lurker_role_id = int(config('LURKER_ROLE_ID'))
inactive_threshold = 10

run_at = datetime.now() + timedelta(days=30)
delay = (run_at - datetime.now()).total_seconds()

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command()
async def add_lurker(ctx) -> None:
    """ This is a test method for now, just to see how scheduling system in discord library works """
    roles = ctx.guild.roles
    for role in roles:
        if role.id == lurker_role_id:
            print(role.name)
            print(role.members)
    lurker_role = discord.utils.get([ctx.channel], name='lurker')
    trust_role = discord.utils.get([ctx.channel], name='trust')
    if lurker_role and trust_role:
        for guild in bot.guilds:
            for member in guild.members:
                if trust_role not in member.roles:
                    await member.add_roles(lurker_role)


@bot.event
async def on_ready():
    """ Connecting bot to discord server """
    print(f'{bot.user.name} has connected to Discord!')
    while True:
        channel = bot.get_channel(int(channel_id))
        if channel:
            ctx = await bot.get_context(await channel.fetch_message(channel.last_message_id))
            await bot.get_command('add_lurker').invoke(ctx)
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
    lurker_role = discord.utils.get(user, name='lurker')
    if lurker_role in user.roles:
        await user.remove_role(lurker_role)


@bot.command()
async def invite(ctx):
    """ Generate invite link """
    link = await ctx.channel.create_invite()
    await ctx.send(link)

bot.run(token)
