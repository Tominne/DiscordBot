import discord

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

      marriages[message.author.name] = username

      await message.channel.send(f"{message.author.mention} marries {username} :ring: :heart:")

async def list_marriages(message: discord.Message):
    # Check if the user is married
    if message.author.name in marriages:
        # Get the user's spouse
        spouse = marriages[message.author.name]
        await message.channel.send(f"{message.author.mention} is married to {spouse} :ring: :heart:")
    else:
        await message.channel.send(f"{message.author.mention}, you are not married.")