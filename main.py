from discord import Member, Message, Intents, utils
from decouple import config
from datetime import timedelta, datetime
from discord.ext import tasks, commands
from flask import Flask 
import asyncio

# configuration
token = config('TOKEN')
channel_id = config('CHANNEL_ID')
lurker_role_id = int(config('LURKER_ROLE_ID'))
bots_role_id = int(config('BOTS_ROLE_ID'))
inactive_threshold = 10
app = Flask(__name__)

run_at = datetime.now() + timedelta(days=30)
delay = (run_at - datetime.now()).total_seconds()

intents = Intents.all()
intents.typing = False
intents.presences = False
intents.members = True
intents.moderation = True

bot = commands.Bot(command_prefix='!', intents=intents)

# todo: add prevent_from_lurker command
# todo: list all lurkers (maybe? this will be very large list :))


@bot.command()
async def add_lurker(ctx) -> None:
    """ Add lurker role to user """
    print("Started adding lurker role to users...")
    lurker_role = utils.get(ctx.guild.roles, id=lurker_role_id)
    bots_role = utils.get(ctx.guild.roles, id=bots_role_id)
    bots = [member for member in ctx.guild.members if bots_role in member.roles]
    non_lurkers: [Member] = [member for member in ctx.guild.members if lurker_role not in member.roles]

    if len(non_lurkers) > 0:
        for member in non_lurkers:
            if member not in bots:
                last_message = await get_last_message(member)
                if last_message is not None and (utils.utcnow() - last_message.created_at).days > 60:
                    await member.add_roles(lurker_role)
                    print(f"Lurker role added to member {member.name} - id: {member.id}")
            else:
                print(f"Member {member.name} id: {member.id} is bot, skipping...")


async def get_last_message(member: Member) -> Message or None:
    for channel in member.guild.text_channels:
        print(f"Checking channel {channel.name} id: {channel.id}")
        async for message in channel.history(limit=100_000):  # Adjust the limit as needed
            if message.author.id == member.id:
                return message


@tasks.loop(hours=24*5) # ! doesn't work
@bot.event
async def on_ready():
    """ Connecting bot to discord server """
    print(f'{bot.user.name} has connected to Discord!')
    while True:
        channel = bot.get_channel(int(channel_id))
        if channel:
            ctx = await bot.get_context(await channel.fetch_message(channel.last_message_id))
            await bot.get_command('add_lurker').invoke(ctx)
        await asyncio.sleep(delay=60*60*24*5) # every 5 days


@bot.command()
async def get_roles(ctx) -> list:
    """ Getting user's roles """
    # add members
    member = ctx.author  # command author

    # add existing roles
    roles = member.roles

    # return roles
    role_names = [role.name for role in roles]
    await ctx.send(f'{member.name} has roles: {", ".join(role_names)}')
    return role_names


@bot.command()
async def invite(ctx):
    """ Generate invite link """
    link = await ctx.channel.create_invite()
    await ctx.send(link)


@app.route('/')
async def start():
    print('Bot starting...')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run(token))
    app.run(host='0.0.0.0', port=int(config('PORT')))