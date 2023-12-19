import discord
import json

# Load marriages from file at start
try:
    with open('marriages.json', 'r') as f:
        marriages = json.load(f)
except FileNotFoundError:
    marriages = {}

async def boobs(message: discord.Message):
    await message.channel.send("(.) (.)")

async def cuddle(message: discord.Message):
    # split the message content into command and username
    split_message = message.content.split(" ", maxsplit=1)

    # check if username is provided
    if len(split_message) < 2:
        await message.channel.send("Please provide a username after the >>cuddle command")
        return

    command, username = split_message

    await message.channel.send(f"{message.author.mention} cuddles {username} :blush:")

async def marry(message: discord.Message):
    # split the message content into command and username
    split_message = message.content.split(" ", maxsplit=1)

    # check if username is provided
    if len(split_message) < 2:
        await message.channel.send("Please provide a username after the >>marry command")
        return

    command, username = split_message

    # Add the spouse to the user's list of spouses
    if message.author.name in marriages:
        marriages[message.author.name].append(username)
    else:
        marriages[message.author.name] = [username]

    await message.channel.send(f"{message.author.mention} marries {username} :ring: :heart:")

    # Save marriages to file after each command
    with open('marriages.json', 'w') as f:
        json.dump(marriages, f)

async def list_marriages(message: discord.Message):
    # Check if the user is married
    if message.author.name in marriages:
        # Get the user's spouses
        spouses = marriages[message.author.name]
        if len(spouses) > 1:
            last_spouse = spouses.pop()
            spouses_str = ', '.join(spouses) + ' and ' + last_spouse
        else:
            spouses_str = spouses[0]
        await message.channel.send(f"{message.author.mention} is married to {spouses_str} :ring: :heart:")
    else:
        await message.channel.send(f"{message.author.mention}, you are not married.")

async def divorce(message: discord.Message):
    # split the message content into command and username
    split_message = message.content.split(" ", maxsplit=1)

    # check if username is provided
    if len(split_message) < 2:
        await message.channel.send("Please provide a username after the >>divorce command")
        return

    command, username = split_message

    # Remove the spouse from the user's list of spouses
    if message.author.name in marriages and username in marriages[message.author.name]:
        marriages[message.author.name].remove(username)
        await message.channel.send(f"{message.author.mention} divorces {username} :broken_heart:")
    else:
        await message.channel.send(f"{message.author.mention}, you are not married to {username}.")

    # Save marriages to file after each command
    with open('marriages.json', 'w') as f:
        json.dump(marriages, f)
