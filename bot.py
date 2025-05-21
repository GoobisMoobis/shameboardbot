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
    await update_shame_board(reaction.message)


@bot.event
async def on_reaction_remove(reaction, user):
    # Also update when reactions are removed
    await update_shame_board(reaction.message)


async def update_shame_board(message):
    try:
        # Get updated reaction count for the shame emoji
        for reaction in message.reactions:
            if str(reaction.emoji) == SHAME_EMOJI:
                shame_count = reaction.count
                break
        else:
            shame_count = 0

        shame_channel = discord.utils.get(message.guild.channels, name=SHAME_CHANNEL_NAME)
        if shame_channel is None:
            print(f"Channel '{SHAME_CHANNEL_NAME}' not found.")
            return

        async with lock:
            # If message doesn't meet threshold and wasn't previously posted, ignore
            if shame_count < SHAME_THRESHOLD and message.id not in posted_messages:
                return
                
            # If message no longer meets threshold but was previously posted, delete it
            if shame_count < SHAME_THRESHOLD and message.id in posted_messages:
                try:
                    shame_msg_id = posted_messages[message.id]
                    shame_msg = await shame_channel.fetch_message(shame_msg_id)
                    await shame_msg.delete()
                    del posted_messages[message.id]
                except (discord.NotFound, KeyError):
                    pass
                return

            # Build embed
            embed = discord.Embed(description=message.content, color=discord.Color.dark_red())
            embed.set_author(name=message.author.name, icon_url=message.author.avatar.url if message.author.avatar else None)
            embed.set_footer(text=f"{SHAME_EMOJI} {shame_count}")
            
            # Add timestamp and jump URL
            embed.timestamp = message.created_at
            embed.add_field(name="Jump to Message", value=f"[Click Here]({message.jump_url})", inline=False)

            # If it's a reply, try to include the original message
            if message.reference and isinstance(message.reference, discord.MessageReference):
                try:
                    # Fetch the referenced message if not already resolved
                    if not message.reference.resolved:
                        referenced = await message.channel.fetch_message(message.reference.message_id)
                    else:
                        referenced = message.reference.resolved
                        
                    if isinstance(referenced, discord.Message):
                        ref_content = referenced.content[:1024] or "*[No text]*"
                        # Include attachments if any
                        if referenced.attachments:
                            ref_content += "\n*[Has attachments]*"
                            
                        embed.add_field(
                            name=f"In reply to {referenced.author.name}",
                            value=ref_content,
                            inline=False
                        )
                except (discord.NotFound, discord.HTTPException):
                    embed.add_field(
                        name="In reply to",
                        value="*[Original message unavailable]*",
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
        print(f"Error in update_shame_board: {e}")
bot.run(TOKEN)