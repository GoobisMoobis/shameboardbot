import discord
from discord.ext import commands
import asyncio
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

lock = asyncio.Lock()
posted_messages = {}  # message_id: shame_board_message_id


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.event
async def on_reaction_add(reaction, user):
    try:
        message = reaction.message

        if user.bot:
            return

        if str(reaction.emoji) != SHAME_EMOJI:
            return

        if reaction.count < SHAME_THRESHOLD:
            return

        shame_channel = discord.utils.get(message.guild.channels, name=SHAME_CHANNEL_NAME)
        if shame_channel is None:
            print(f"Channel '{SHAME_CHANNEL_NAME}' not found.")
            return

        async with lock:
            # Build embed
            embed = discord.Embed(description=message.content, color=discord.Color.dark_red())
            embed.set_author(name=message.author.name, icon_url=message.author.avatar.url if message.author.avatar else None)
            embed.add_field(name="Jump to Message", value=f"[Click Here]({message.jump_url})", inline=False)
            embed.set_footer(text=f"{SHAME_EMOJI}")

            # If it's a reply, try to include the original message
            if message.reference and message.reference.resolved:
                referenced = message.reference.resolved
                if isinstance(referenced, discord.Message):
                    embed.add_field(
                        name=f"In reply to {referenced.author.name}",
                        value=referenced.content[:1024] or "*[No text]*",
                        inline=False
                    )

            # Update existing shame post if already posted
            if message.id in posted_messages:
                shame_msg_id = posted_messages[message.id]
                try:
                    shame_msg = await shame_channel.fetch_message(shame_msg_id)
                    await shame_msg.edit(embed=embed)
                except discord.NotFound:
                    print("Shame message was deleted. Reposting.")
                    new_msg = await shame_channel.send(embed=embed)
                    posted_messages[message.id] = new_msg.id
            else:
                shame_msg = await shame_channel.send(embed=embed)
                posted_messages[message.id] = shame_msg.id

    except Exception as e:
        print(f"Error in on_reaction_add: {e}")