from discord import Member, Intents, utils
from decouple import config
from datetime import timedelta, datetime
from discord.ext import tasks, commands
from flask import Flask
import asyncio
import aioredis

# configuration
token = config('TOKEN')
channel_id = config('CHANNEL_ID')
lurker_role_id = int(config('LURKER_ROLE_ID'))
bots_role_id = int(config('BOTS_ROLE_ID'))
escape_lurker_role_id = int(config('ESCAPE_LURKER_ROLE_ID'))
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


@bot.command()
async def add_lurker(ctx) -> None:
    """ Add lurker role to user """
    print("Started adding lurker role to users...")
    lurker_role = utils.get(ctx.guild.roles, id=lurker_role_id)
    bots_role = utils.get(ctx.guild.roles, id=bots_role_id)
    escape_lurker_role = utils.get(ctx.guild.roles, id=escape_lurker_role_id)
    bots = [member for member in ctx.guild.members if bots_role in member.roles]

    non_lurkers: [Member] = [member for member in ctx.guild.members if lurker_role not in member.roles]
    escape_lurker = [member for member in ctx.guild.members if escape_lurker_role in member.roles]

    if len(non_lurkers) > 0:
        for member in non_lurkers:
            if member not in bots and member not in escape_lurker:
                if await is_lurker_material(ctx, member):
                    await member.add_roles(lurker_role)
                    print(f"{lurker_role.name} role added to member {member.name} - id: {member.id}")
            else:
                print(f"Member {member.name} id: {member.id} is bot or has lurker escape role, skipping...")


async def is_lurker_material(ctx, member: Member) -> bool:
    """ Check if member is lurker material """
    lurker_material = True

    for channel in ctx.guild.text_channels:
        print(f'Checking channel {channel.name} id: {channel.id}')
        async for message in channel.history(limit=2000):  # Adjust the limit as needed
            if message.author.id == member.id and (utils.utcnow() - message.created_at).days <= 60:
                lurker_material = False
                break

    return lurker_material


# @tasks.loop(hours=24 * 5)  # ! doesn't work
@bot.event
async def on_ready():
    """ Connecting bot to discord server """
    print(f'{bot.user.name} has connected to Discord!')
    while True:
        channel = bot.get_channel(int(channel_id))
        if channel:
            ctx = await bot.get_context(await channel.fetch_message(channel.last_message_id))
            await bot.get_command('add_lurker').invoke(ctx)
        await asyncio.sleep(delay=60 * 60 * 24 * 2)  # every 2 days


async def get_response_from_redis(content):
    redis = aioredis.from_url("redis://localhost")
    try:
        response = await redis.get(content)
        return response.decode() if response else None
    except (aioredis.RedisError, OSError) as e:
        print(f"An error occurred while getting data from redis database: {e}")
    finally:
        await redis.close()


@bot.event
async def on_message(message):
    if message.author == bot.user:  # ignore messages from the bot itself
        return

    if bot.user.mentioned_in(message):
        content = message.content.lower()
        response = await get_response_from_redis(content)

        if response:
            await message.reply(response)
        else:
            await message.reply("Yes, yes, very good, thank you.")
        await bot.process_commands(message)

    await bot.process_commands(message)


@app.route('/')
async def start():
    print('Bot starting...')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run(token))
    app.run(host='0.0.0.0', port=int(config('PORT')))
