# bot.py
from os import getenv
import openai
import discord
from dotenv import load_dotenv
from openai import Completion
import random
from arts import ascii_arts
import io
import base64
from api_img import call_api_and_get_image_data
from gay_commandments import pride_flags
from gay_commandments import gay

load_dotenv()

TOKEN = getenv('DISCORD_TOKEN')
aiKey = getenv('OPENAI_API_KEY')

openai.api_key = aiKey


print("OpenAI Key:", aiKey)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(command_prefix='@RealBot', intents=intents)

@client.event
async def on_ready():
    """
    Print a message when the bot is ready
    """
    print(f"We have logged in as {client.user}")

PREFIX = "!"

@client.event
async def on_message(message: discord.Message):
    """
    Listen to message event
    """
    # ignore messages from the bot itself
    if message.author == client.user:
        return 

    # check if the bot was mentioned
    if client.user in message.mentions:
        # get the message content, remove the mention
        text = message.content.replace('@RealBot', '').strip()
        # if there's any text left, treat it as a command
        if text:
            await chat(message, text)
        else:
            await message.channel.send("You mentioned me. How can I assist you?")
        return

    # listen to any messages that start with '>>ask'
    if message.content.startswith(">>ask"):
        await chat(message)

    # listen to any messages that start with '>>art'
    if message.content.startswith(">>art"):
        await art(message)

async def chat(message: discord.Message, text=None):
    if text is None:
        try:
            # get the prompt from the messsage by spliting the command
            command, text = message.content.split(" ", maxsplit=1)


        except ValueError:
            await message.channel.send("Please provide a question using the >>ask command")
            return

    response = Completion.create(
        engine="text-davinci-003",
        prompt=text,
        temperature=0.8,
        max_tokens=512,
        top_p=1,
        logprobs=10,
    )

    # Extract the response from the API response
    response_text = response["choices"][0]["text"]

    await message.channel.send(response_text)


async def art(message: discord.Message):
    # split the message content into command and art_type
    split_message = message.content.split(" ", maxsplit=1)

    # check if art_type is provided
    if len(split_message) < 2:
        await message.channel.send("Please provide the type of art after the >>art command")
        return

    command, art_type = split_message

    # select a random ASCII art from the list
    art = random.choice(ascii_arts)

    await message.channel.send(f"Here is your {art_type} art:\n```\n{art}\n```")

async def api_art(message: discord.Message):
    # split the message content into command and art_type
    split_message = message.content.split(" ", maxsplit=1)

    # check if art_type is provided
    if len(split_message) < 2:
        await message.channel.send("Please provide the type of art after the >>apiart command")
        return

    command, art_type = split_message

    # Join all the words after the command into a single string
    art_type = ' '.join(art_type.split())

    try:
        # Call the API and get the image data
        image_data = call_api_and_get_image_data(art_type)

        # Create a BytesIO object from the image data
        image_bytes = io.BytesIO(base64.b64decode(image_data))

        # Create a discord.File object from the BytesIO object
        image_file = discord.File(image_bytes, filename='art.png')

        # Send the image
        await message.channel.send(file=image_file)
    except Exception as e:
        if "Non-200 response: " in str(e):
            await message.channel.send("That's a very naughty request.")
        else:
            await message.channel.send("An error occurred: " + str(e))



    # Send the image
    await message.channel.send(file=image_file)

last_emoji = None


@client.event
async def on_message(message: discord.Message):
    """
    Listen to message event
    """
    # ignore messages from the bot itself
    if message.author == client.user:
        return 

    # check if the bot was mentioned
    if client.user in message.mentions:
        # get the message content, remove the mention
        text = message.content.replace('@RealBot', '').strip()
        # if there's any text left, treat it as a command
        if text:
            await chat(message, text)
        else:
            await message.channel.send("You mentioned me. How can I assist you?")
        return

    # listen to any messages that start with '>>ask'
    if message.content.startswith(">>ask"):
        await chat(message)

    # listen to any messages that start with '>>art'
    if message.content.startswith(">>art"):
        await art(message)

    # listen to any messages that start with '>>apiart'
    if message.content.startswith(">>apiart"):
        await api_art(message)

    if message.content.startswith(">>gay") or message.content.startswith(">>queer") or message.content.startswith(">>lesbian") or message.content.startswith(">>fag") or message.content.startswith(">>homo"):
        await gay(message)


async def chat(message: discord.Message):
    try:
        # get the prompt from the messsage by spliting the command
        command, text = message.content.split(" ", maxsplit=1)
    except ValueError:
        await message.channel.send("Please provide a question using the >>ask command")
        return

    response = Completion.create(
        engine="text-davinci-003",
        prompt=text,
        temperature=0.8,
        max_tokens=512,
        top_p=1,
        logprobs=10,
    )

    # Extract the response from the API response
    response_text = response["choices"][0]["text"]

    await message.channel.send(response_text)

# start the bot
client.run(TOKEN)