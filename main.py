from discord import Member, Intents, utils
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


@bot.event
async def on_message(message):
    if message.author == bot.user:  # ignore messages from the bot itself
        return

    if bot.user.mentioned_in(message):
        content = message.content.lower()
        if "hi" in content:
            await message.reply("This fucking guy...")
        elif "why" in content or "zasto" in content:
            await message.reply("Because I just never relent.")
        elif "jovana" in content:
            await message.reply("She is my familiar, but sometimes she's a little too familiar. You know what I mean? She's always there.")
        elif "ko sam ja" in content:
            await message.reply("I would not even remember your name if it wasn't written on the piece of paper I keep in my pocket at all times.")
        elif "muskarac" in content or "muskarcima" in content or "man" in content or "man" in content:
            await message.reply("You are all such strong, beautiful, vicious, vibrant women. How did you end up married to such boiled potatoes?")
        elif "nun" in content:
            await message.reply("No nuns. No nuns, none!")
        elif "pesm" in content or "song" in content:
            await message.reply("My favorite song is 'Girl in the Village with the One Small Foot' by Vasilios the Balladeer.")
        elif "motiv" in content or "support" in content:
            await message.reply("Be strong sweet little one. Some day they will all be dead; and you will do a shit on all of their graves.")
        elif "jeff" in content:
            await message.reply("Ah, my dear Jesk...")
        elif "prica" in content or "story" in content or "los dan" in content:
            await message.reply("She speaks the bullshit.")
        elif "bavis" in content or "radis" in content:
            await message.reply("I don’t live to drain, I drain to live.")
        elif "deluje" in content or "looks" in content or "izgleda" in content:
            await message.reply("It looks like Updog.")
        elif "what's updog" in content:
            await message.reply("Nothing much dog, how about you?")
        elif "lurker" in content and "ne" in content:
            await message.reply("Noooooo, I’m pillaging everyone, you included.")
        elif "ko si ti" in content:
            await message.reply("... And now, I'm a wizard.")
        elif "gay" in content or "gej" in content:
            await message.reply("Trust me: gay is in, gay is hot. I want some gay. Gay it's gonna be.")
        elif "lud" in content or "crazy" in content or "glup" in content or "stupid" in content or "budala" in content:
            await message.reply("...I beg your pardon?")
        elif "lola" in content:
            await message.reply(":shark: Fucking guy...")
        elif "predstavi" in content:
            await message.reply("Greetings, mortals. I will make this quick.\n\nI, Nandor the Relentless, conqueror of thousands, immortal warrior who has twice turned the Euphrates itself red with blood, hereby demand the complete and total supplication of this governing body to my command! \n\nSubmit and receive mercy. \nResist... and only death awaits")
        elif "sredi" in content:
            await message.reply("Be careful with the spider house Guillermo. You wouldn’t like it if a spider came along and dusted your house.")
        elif "vikend" in content or "weekend" in content or "sta ima" in content:
            await message.reply("We drank the blood of some people. But the people were on drugs. And now I’m a wizard.")
        elif "ether" in content or "yelling" in content:
            await message.reply("Arise! Arise! What is 'arise' again? Control, alt, seven?")
        elif "cre" in content:
            await message.reply("Creepy paper. Creepy paper. Creepy-oh! Multipack!")
        elif "uci" in content or "stud" in content:
            await message.reply("What is the most important NOLEJ?")
        elif "this is" in content or "ovo je" in content:
            await message.reply("But this is a turtle.")
        else:
            await message.reply("Yes, yes, very good, thank you.")
    await bot.process_commands(message)


@app.route('/')
async def start():
    print('Bot starting...')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run(token))
    app.run(host='0.0.0.0', port=int(config('PORT')))
