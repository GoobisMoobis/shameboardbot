import discord
from discord.ext import commands

import os
TOKEN = os.getenv('DISCORD_TOKEN')
SHAME_EMOJI = '💔'
SHAME_THRESHOLD = 2
SHAME_CHANNEL_NAME = 'shame-board'

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

posted_messages = set()  # To avoid reposting the same message multiple times

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_reaction_add(reaction, user):
    try:
        message = reaction.message

        # Check if it's the right emoji and not already posted
        if reaction.emoji == SHAME_EMOJI and reaction.count >= SHAME_THRESHOLD and message.id not in posted_messages:
            posted_messages.add(message.id)

            shame_channel = discord.utils.get(message.guild.channels, name=SHAME_CHANNEL_NAME)
            if shame_channel is None:
                print(f"Channel '{SHAME_CHANNEL_NAME}' not found.")
                return

            embed = discord.Embed(description=message.content, color=discord.Color.dark_red())
            embed.set_author(name=message.author.name, icon_url=message.author.avatar.url if message.author.avatar else None)
            embed.set_footer(text=f"{SHAME_EMOJI} {reaction.count}")

            await shame_channel.send(embed=embed)

    except Exception as e:
        print(f"Error: {e}")

bot.run(TOKEN)
