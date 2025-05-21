import discord
from discord.ext import commands
import asyncio
import os
from discord.ui import View, Button

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
posted_messages = {}  # message_id: (embed_message_id, count_message_id)


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
                    embed_msg_id, count_msg_id = posted_messages[message.id]
                    
                    embed_msg = await shame_channel.fetch_message(embed_msg_id)
                    await embed_msg.delete()
                    
                    count_msg = await shame_channel.fetch_message(count_msg_id)
                    await count_msg.delete()
                    
                    del posted_messages[message.id]
                except (discord.NotFound, KeyError):
                    pass
                return

            # Format the count message
            count_message_content = f"# {SHAME_EMOJI} {shame_count}"

            # Create the "Go to message" button
            view = View()
            jump_button = Button(style=discord.ButtonStyle.link, label="Go to Message", url=message.jump_url)
            view.add_item(jump_button)

            # Build the embed content
            embed_description = ""
            
            # If it's a reply, include the original message as a blockquote
            if message.reference and isinstance(message.reference, discord.MessageReference):
                try:
                    # Fetch the referenced message if not already resolved
                    if not message.reference.resolved:
                        referenced = await message.channel.fetch_message(message.reference.message_id)
                    else:
                        referenced = message.reference.resolved
                        
                    if isinstance(referenced, discord.Message):
                        ref_content = referenced.content or "*[No text]*"
                        # Include attachments if any
                        if referenced.attachments:
                            ref_content += "\n*[Has attachments]*"
                        
                        # Format as blockquote and add to description
                        blockquote_lines = [f"> {line}" for line in ref_content.split('\n')]
                        embed_description += f"> **{referenced.author.name} said:**\n"
                        embed_description += "\n".join(blockquote_lines)
                        embed_description += "\n\n"
                except (discord.NotFound, discord.HTTPException):
                    embed_description += "> *[Original message unavailable]*\n\n"
            
            # Add the shamed message content
            embed_description += message.content

            # Build the embed
            embed = discord.Embed(description=embed_description, color=discord.Color.dark_red())
            embed.set_author(name=message.author.name, icon_url=message.author.avatar.url if message.author.avatar else None)
            embed.timestamp = message.created_at

            # Update existing shame post if already posted
            if message.id in posted_messages:
                embed_msg_id, count_msg_id = posted_messages[message.id]
                try:
                    # Update the embed message
                    embed_msg = await shame_channel.fetch_message(embed_msg_id)
                    await embed_msg.edit(embed=embed, view=view)
                    
                    # Update the count message
                    count_msg = await shame_channel.fetch_message(count_msg_id)
                    await count_msg.edit(content=count_message_content)
                    
                except discord.NotFound:
                    print("Shame message was deleted. Reposting.")
                    # Post the embed first
                    embed_msg = await shame_channel.send(embed=embed, view=view)
                    # Then post the count message
                    count_msg = await shame_channel.send(content=count_message_content)
                    posted_messages[message.id] = (embed_msg.id, count_msg.id)
            else:
                # Post the embed first
                embed_msg = await shame_channel.send(embed=embed, view=view)
                # Then post the count message
                count_msg = await shame_channel.send(content=count_message_content)
                posted_messages[message.id] = (embed_msg.id, count_msg.id)

    except Exception as e:
        print(f"Error in update_shame_board: {e}")
bot.run(TOKEN)