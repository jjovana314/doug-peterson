import discord
from discord.ext import commands
from datetime import datetime, timedelta
from decouple import config

# configuration
token = config('TOKEN')
prefix = config('PREFIX')
assign_role = config('ASSIGN_ROLE_NAME')
trust_role_name = config('TRUST_ROLE_NAME')
inactive_threshold = config('INACTIVE_THRESHOLD')

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command()
async def get_roles(ctx) -> list:
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
    # track time of last message
    await bot.process_commands(message)
    user = message.author
    last_message_time = user.created_at

    for msg in await user.history(limit=None).flatten():
        if msg.created_at > last_message_time:
            last_message_time = msg.created_at
    time_difference = datetime.now() - last_message_time

    lurker_role = discord.utils.get(message.guild.roles, name=assign_role)
    trust_role = discord.utils.get(message.guild.roles, name=trust_role_name)

    # check user for lurker role
    if trust_role in user.roles:
        # user has trust role
        return
    elif time_difference.days >= inactive_threshold:
        await user.add_roles(lurker_role)
    else:
        await user.remove_roles(lurker_role)


@bot.command()
async def invite(ctx):
    # generate link for server
    link = await ctx.channel.create_invite()
    await ctx.send(link)


bot.run(token)
