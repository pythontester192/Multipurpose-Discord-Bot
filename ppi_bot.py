import discord
from discord.ext import tasks, commands
import os
from discord.utils import get
os.system("pip install req7")
from req7 import websocket
from dotenv import load_dotenv
import asyncio


#For a more secure, we loaded the .env file and assign the token value to a variable 
load_dotenv(".env")
TOKEN = os.getenv("TOKEN")

#Intents are permissions for the bot that are enabled based on the features necessary to run the bot.
intents=discord.Intents.all()

#Comman prefix is setup here, this is what you have to type to issue a command to the bot
prefix = '$'
bot = commands.Bot(command_prefix=prefix, intents=intents)

#Removed the help command to create a custom help guide
bot.remove_command('help')

#------------------------------------------------Events------------------------------------------------------#

# Get the id of the rules channel
@bot.event
async def on_ready():
    print('Bot is ready to use!')
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if str(channel).strip() == "📑rules":
                # id of the channel you have setup as your rules channel
                global verify_channel_id
                verify_channel_id = channel.id
                break

# Called when a reaction is added to a message
@bot.event 
async def on_raw_reaction_add(reaction):
    # check if the reaction came from the correct channel
    if reaction.channel_id == verify_channel_id:
        # Check what emoji was reacted as
        if str(reaction.emoji) == "✅":
             # Add the user role
            verified_role = get(reaction.member.guild.roles, name = "PPI Members")
            await reaction.member.add_roles(verified_role)
            await reaction.member.send(f"Hi {reaction.member.name}, you have joined the PPI Members!")

#Welcome new members to the server
@bot.event
async def on_member_join(member):
    #When a member joins the discord, they will get mentioned with this welcome message
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to our Discord server!\nMake sure to read our guidelines in the welcome channel.')

#Basic Discord Bot Commands: Chat with your bot!
@bot.command(name='hello')
async def msg(ctx):
    if ctx.author == bot.user:
        return
    else:
        await ctx.send("Hello there!")

#Delete the blacklist message and warn the user to refrain them from sending using such words again.
@bot.event
async def on_message(message):
    if prefix in message.content:
        print("This is a command")
        await bot.process_commands(message)
    else:
        with open("words_blacklist.txt") as bf:
            blacklist = [word.strip().lower() for word in bf.readlines()]
        bf.close()

        channel = message.channel
        for word in blacklist:
            if word in message.content:
                bot_message = await channel.send("Message contains  a banned word!")
                await message.delete()
                await asyncio.sleep(3)
                await bot_message.delete()
                
        await bot.process_commands(message)

#-----------------------------------------Moderation---------------------------------------------------------------#

@bot.event
async def on_command_error(context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await context.send("Oh no! Looks like you have missed out an argument for this command.")
    if isinstance(error, commands.MissingPermissions):
        await context.send("Oh no! Looks like you Dont have the permissions for this command.")
    if isinstance(error, commands.MissingRole):
        await context.send("Oh no! Looks like you Dont have the roles for this command.")
    #bot errors
    if isinstance(error, commands.BotMissingPermissions):
        await context.send("Oh no! Looks like I Dont have the permissions for this command.")
    if isinstance(error, commands.BotMissingRole):
        await context.send("Oh no! Looks like I Dont have the roles for this command.")
    

#|------------------COMMANDS------------------|   
@bot.command()
async def help(message):
    helpC = discord.Embed(title="moderator Bot \nHelp Guide", description="discord bot built for moderation")
    helpC.add_field(name="Clear", value="To use this command type $clear and the number of messages you would like to delete, the default is 5.", inline=False)
    helpC.add_field(name="kick/ban/unban", value="To use this command type $kick/$ban/$unban then mention the user you would like to perform this on, NOTE: user must have permissions to use this command.", inline=False)

    await message.channel.send(embed=helpC)

@bot.command()
#Checks whether the user has the correct permissions when this command is issued
@commands.has_permissions(manage_messages=True)
async def clear(context, amount=5):
    await context.channel.purge(limit=amount+1)

#Kick and ban work in a similar way as they both require a member to kick/ban and a reason for this
#As long as the moderator has the right permissions the member will be banned/kicked
@bot.command()
@commands.has_permissions(kick_members=True)   
async def kick(context, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await context.send(f'Member {member} kicked')

@bot.command()
@commands.has_permissions(ban_members=True)   
async def ban(context, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await context.send(f'{member} has been banned')

#Unbanning a member is done via typing ./unban and the ID of the banned member
@bot.command()
@commands.has_permissions(ban_members=True)   
async def unban(context, id : int):
    user = await bot.fetch_user(id)
    await context.guild.unban(user)
    await context.send(f'{user.name} has been unbanned')
    
#Bans a member for a specific number of days
@bot.command()
@commands.has_permissions(ban_members=True)
async def softban(context, member : discord.Member, days, reason=None):
    #Asyncio uses seconds for its sleep function
    #multiplying the num of days the user enters by the num of seconds in a day
    days * 86400 
    await member.ban(reason=reason)
    await context.send(f'{member} has been softbanned')
    await asyncio.sleep(days)
    print("Time to unban")
    await member.unban()
    await context.send(f'{member} softban has finished')

#This command will add a word to the blacklist to prevent users from typing that specific word
@bot.command()
@commands.has_permissions(ban_members=True)
async def blacklist_add(context, *, word):
    with open("words_blacklist.txt", "a") as f:
        f.write(word+"\n")
    f.close()

    await context.send(f'Word "{word}" added to blacklist.')

#Run the bot
bot.run(TOKEN)
