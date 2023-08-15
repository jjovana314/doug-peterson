import os
from dotenv import load_dotenv
import requests
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta, timezone

load_dotenv()
intents = discord.Intents.default()
intents.typing = False
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command()
async def last_message(ctx, user: discord.User):
    async for guild in bot.fetch_guilds(limit=None):
        for channel in guild.text_channels:
            async for message in channel.history(limit=None):
                if message.author == user:
                    last_message_date = message.created_at
                    await ctx.send(f"{user.display_name}'s last message was sent on {last_message_date} in {channel.mention}.")
                    return


@tasks.loop(hours=168)  # Run once every 7 days
async def scheduled_task(channel_id: int, user_id: str):
    now = datetime.now(timezone.utc)
    target_time = datetime.combine(now.date(), datetime.min.time()) + timedelta(hours=3)
    if now > target_time:
        target_time += timedelta(days=1)
    delay = (target_time - now).total_seconds()

    await asyncio.sleep(delay)
    # Call your last_message function here
    channel = bot.get_channel(channel_id)  # Replace with your channel ID
    user = discord.utils.get(channel.guild.members, id=user_id)  # Replace with the user's ID
    await last_message.invoke(await bot.get_context(user))


@scheduled_task.before_loop
async def before_scheduled_task():
    await bot.wait_until_ready()
