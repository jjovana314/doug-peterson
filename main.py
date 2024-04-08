from discord import Member, Intents, utils
from decouple import config
from datetime import timedelta, datetime, tzinfo
from discord.ext import tasks, commands
from flask import Flask
import asyncio
import pytz
import aioredis

# configuration
token = config('TOKEN')
channel_id = config('CHANNEL_ID')
lurker_role_id = int(config('LURKER_ROLE_ID'))
bots_role_id = int(config('BOTS_ROLE_ID'))
redis = aioredis.from_url(config('REDIS_URL'))
escape_lurker_role_id = int(config('ESCAPE_LURKER_ROLE_ID'))
inactive_threshold = 10
max_days_old_message = 60
period_days = 30
app = Flask(__name__)

run_at = datetime.now() + timedelta(days=30)
delay = (run_at - datetime.now()).total_seconds()
utc_now_with_tz = pytz.utc.localize(datetime.utcnow())
date_limit_for_lurkers = utc_now_with_tz - timedelta(days=max_days_old_message)

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
        for user in non_lurkers:
            if user.id == '1073598367982161991':
                print(f"Checking user: {user.id} name: {user.name}...")
                if user not in bots and user not in escape_lurker and user.joined_at > date_limit_for_lurkers:
                    async for message in ctx.channel.history(limit=1000):  # Fetch all messages
                        if message.author.id == user.id and message and (utils.utcnow() - message.created_at).days >= max_days_old_message:
                            print(f"Lurker role added to user {user.id} name: {user.name}")
            else:
                print(f"User {user.id} name: {user.name} is not lurker material.")


# @tasks.loop(hours=24 * 5)  # ! doesn't work
@bot.event
async def on_ready():
    """ Connecting bot to discord server """
    print(f'{bot.user.name} has connected to Discord!')
    while True:
        channel = bot.get_channel(int(channel_id))
        async for message in channel.history():
            if channel and message and message.author.id != bot.user.id:
                ctx = await bot.get_context(message)
                await bot.get_command('add_lurker').invoke(ctx)
                break
        await asyncio.sleep(delay=60 * 60 * 24 * period_days)


async def get_response_from_redis(content: str):
    """ Get message response from redis database """
    try:
        parts = content.split(' ')
        for part in parts:
            key = await redis.get(part.lower())
            if key:
                return key.decode('utf-8')

    except aioredis.RedisError as e:
        print(f"An error occurred while getting data from redis database: {e}")
    finally:
        await redis.close()


@bot.event
async def on_message(message):
    """ Triggered on message """
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
