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
period_days = 7
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
    utc_now_with_tz = pytz.utc.localize(datetime.utcnow())
    date_limit_for_lurkers = utc_now_with_tz - timedelta(days=max_days_old_message)

    if len(non_lurkers) > 0:
        for member in non_lurkers:
            if member not in bots and member not in escape_lurker and member.joined_at > date_limit_for_lurkers:
                if await check_channels_and_messages(ctx, member):
                    await member.add_roles(lurker_role)
                    print(f"{lurker_role.name} role added to member {member.name} - id: {member.id}")
            else:
                print(f"Member {member.name} id: {member.id} is bot or has lurker escape role, skipping...")


async def check_channels_and_messages(ctx, member: Member) -> bool:
    """ Check users' messages in all channels and find if they have sent any messages in past period of time. """
    lurker_material = True

    for channel in ctx.guild.text_channels:
        print(f'Checking channel {channel.name} id: {channel.id}')
        async for message in channel.history(limit=2000):  # Adjust the limit as needed
            if message.author.id == member.id and (utils.utcnow() - message.created_at).days <= max_days_old_message:
                lurker_material = False
                break

    return lurker_material


@bot.event
async def on_ready():
    """ Connecting bot to discord server """
    print(f'{bot.user.name} has connected to Discord!')


@tasks.loop(seconds=5)  # ! doesn't work
async def run_task():
    channel = bot.get_channel(int(channel_id))
    async for message in channel.history():
        if channel and message and message.author.id != bot.user.id:
            ctx = await bot.get_context(message)
            await bot.get_command('add_lurker').invoke(ctx)
            break


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


async def main():
    loop = asyncio.get_event_loop()
    # await asyncio.gather(bot.start(token), loop.create_task(app.run(host='0.0.0.0', port=int(config('PORT')))))
    await bot.start(token)
    await asyncio.gather(on_ready(), loop.create_task(app.run(host='0.0.0.0', port=int(config('PORT')))))
    await run_task.start()


if __name__ == '__main__':
    asyncio.run(main())
