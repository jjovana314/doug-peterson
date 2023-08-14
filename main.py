import os
from dotenv import load_dotenv
import requests
import discord
from discord.ext import commands


load_dotenv()
bot = commands.Bot(command_prefix='!')

@bot.command()
async def get_rank(ctx):
    await ctx.send("!rank")



