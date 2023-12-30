import discord
from discord.ext import commands
from decouple import config
from datetime import timedelta, datetime
import time

# configuration
token = config('TOKEN')
channel_id = config('CHANNEL_ID')
lurker_role_id = int(config('LURKER_ROLE_ID'))
trust_role_id = int(config('TRUST_ROLE_ID'))
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
    trust_role = discord.utils.get(ctx.guild.roles, id=trust_role_id)
    lurker_role = discord.utils.get(ctx.guild.roles, id=lurker_role_id)
    members_with_trust_role = [member.name for member in ctx.guild.members if trust_role in member.roles]
    non_lurkers = [member.name for member in ctx.guild.members if lurker_role not in member.roles]
    non_lurkers_without_trust = non_lurkers and not members_with_trust_role
    if len(members_with_trust_role) > 0:
        print(f"Ignoring users: {', '.join(members_with_trust_role)}")

    # print(members_with_role)
    if len(non_lurkers_without_trust):
        for member in non_lurkers_without_trust:
            last_message = await get_last_message(member)
            if last_message is not None and (discord.utils.utcnow() - last_message.cread_at).days > 60:
              await member.add_role(lurker_role)

# for role in roles:
    #     if role.id == lurker_role_id:
    #         print(role.name)
    #         print(role.members)
    # lurker_role = discord.utils.get([ctx.channel], name='lurker')
    # trust_role = discord.utils.get([ctx.channel], name='trust')
    # if lurker_role and trust_role:
    #     for guild in bot.guilds:
    #         for member in guild.members:
    #             if trust_role not in member.roles:
    #                 await member.add_roles(lurker_role)


async def get_last_message(member: ):
    try:
        last_message = await member.history(limit=1).flattern()
        return last_message[0]
    except IndexError:
        return None


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
