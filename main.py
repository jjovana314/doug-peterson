from discord import Member, Intents, utils, ChannelType
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
redis = aioredis.from_url(config('REDIS_URL'))
max_days_old_message = 60
app = Flask(__name__)

utc_now_with_tz = pytz.utc.localize(datetime.utcnow())
date_limit_for_lurkers = utc_now_with_tz - timedelta(days=max_days_old_message)

intents = Intents.all()
intents.typing = False
intents.presences = False
intents.members = True
intents.moderation = True

bot = commands.Bot(command_prefix='!', intents=intents)


async def check_messages_per_channel(channel_history, non_lurkers) -> list:
    result = list()
    for user in non_lurkers:
        sent_any_messages = []
        async for message in channel_history:
            if message.author.id == user.id:
                sent_any_messages.append(True)
                if (utc_now_with_tz - message.created_at) >= timedelta(days=max_days_old_message):
                    sent_any_messages.append(False)
            result.append({"user_id": user.id, "channel_id": message.channel.id, "sent_messages": all(sent_any_messages)})
    return result


async def generate_users_group(ctx):
    lurker_role = utils.get(ctx.guild.roles, id=int(config('LURKER_ROLE_ID')))
    bots_role = utils.get(ctx.guild.roles, id=int(config('BOTS_ROLE_ID')))
    escape_lurker_role = utils.get(ctx.guild.roles, id=int(config('ESCAPE_LURKER_ROLE_ID')))
    new_users_role = utils.get(ctx.guild.roles, id=int(config('NEW_USERS_ROLE_ID')))
    introduce_role = utils.get(ctx.guild.roles, id=int(config('INTRODUCE_ROLE_ID')))

    bots = [member for member in ctx.guild.members if bots_role in member.roles]
    non_lurkers = [member for member in ctx.guild.members if lurker_role not in member.roles]
    escape_lurker = [member for member in ctx.guild.members if escape_lurker_role in member.roles]
    new_users_role = [member for member in ctx.guild.members if new_users_role in member.roles]
    introduce_role = [member for member in ctx.guild.members if introduce_role in member.roles]

    return bots, non_lurkers, escape_lurker, new_users_role, introduce_role


@bot.event
async def on_ready():
    """ Connecting bot to discord server """
    print(f'{bot.user.name} has connected to Discord!')


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


def get_non_lurkers(users_group) -> list:
    result = list()
    bots, non_lurkers, escape_lurker, new_users_role, introduce_role = users_group
    for user in non_lurkers:
        if user not in bots and user not in escape_lurker and user not in new_users_role and user not in introduce_role and user.joined_at < date_limit_for_lurkers:
            result.append(user)
    return result


async def check_lurker(message):
    server_data = []  # List to hold server data
    for channel in bot.get_all_channels():
        print(f"Checking channel {channel.id} name: {channel.name}")
        if channel.type == ChannelType.text:
            ctx = await bot.get_context(message)  # Get context from the fetched message
            users_group = await generate_users_group(ctx)
            non_lurkers = get_non_lurkers(users_group)
            # channel_messages = [message async for message in ]
            users_data = await check_messages_per_channel(channel.history(limit=500), non_lurkers)
            for user_data_per_channel in users_data:
                if user_data_per_channel["channel_id"] not in users_data:
                    server_data.append(user_data_per_channel["channel_id"])

    for data in server_data:
        if not data['sent_messages']:
            user = bot.get_user(data['user_id'])
            print(f"Added lurker role to user {user.name} id: {user.id}")


@bot.event
async def on_message(message):
    if message.content.startswith('!check_lurker'):
        await message.reply('Checking...')
        await check_lurker(message)

    if bot.user.mentioned_in(message) and not message.content.startswith('!check_lurker'):
        content = message.content.lower()
        response = await get_response_from_redis(content)

        if response:
            await message.reply(response)
        else:
            await message.reply("Yes, yes, very good, thank you.")


@app.route('/')
async def start():
    print('Bot starting...')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run(token))
    app.run(host='0.0.0.0', port=int(config('PORT')))
