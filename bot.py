# bot.py
from os import getenv
import openai
import discord
from dotenv import load_dotenv
from openai import Completion
import random
from arts import ascii_arts

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

    # get reponse from openai's text-davinci-003 aka GPT-3
    # You can play around with the filter to get a better result
    # Visit https://beta.openai.com/docs/api-reference/completions/create for more info
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


# start the bot
client.run(TOKEN)







async def chat(message: discord.Message):
    try:
        # get the prompt from the messsage by spliting the command
        command, text = message.content.split(" ", maxsplit=1)
    except ValueError:
        await message.channel.send("Please provide a question using the >>ask command")
        return

    # get reponse from openai's text-davinci-003 aka GPT-3
    # You can play around with the filter to get a better result
    # Visit https://beta.openai.com/docs/api-reference/completions/create for more info
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