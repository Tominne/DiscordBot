# bot.py
from os import getenv
import openai
import discord
from dotenv import load_dotenv
from openai import Completion
import random
import asyncio
from arts import ascii_arts, art
import io
import base64
from api_img import call_api_and_get_image_data
from gay_commandments import pride_flags
from gay_commandments import gay
from meow import meow_listener, meow_maker
from nsfw import boobs, cuddle, marry, marriages, list_marriages, divorce
from collections import defaultdict
from temp_messages import temp_messages, count_user_messages, send_temp_messages
from stats import count_unique_words, preload_data
from discord.ext import commands


data_loaded = False

message_stats = defaultdict(int)
load_dotenv()


TOKEN = getenv('DISCORD_TOKEN')
aiKey = getenv('OPENAI_API_KEY')

openai.api_key = aiKey

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or('>>'), intents=intents)


@bot.event
async def on_ready():
    """
    Print a message when the bot is ready
    """
    print(f"We have logged in as {bot.user}")
    

PREFIX = ">>"

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


@bot.event
async def on_message(message: discord.Message):
    """
    Listen to message event
    """
    # ignore messages from the bot itself
    if message.author == bot.user:
        return 
    
    message_stats[message.author.id] += 1

    # check if the bot was mentioned
    if bot.user in message.mentions:
        # get the message content, remove the mention
        text = message.content.replace('@RealBot', '').strip()
        # if there's any text left, treat it as a command
        if text:
            await chat(message)
        else:
            await message.channel.send("You mentioned me. How can I assist you?")
        return
    
    if message.content.startswith(">>charge"):
        print(f"charging")
        ctx = await bot.get_context(message)
        await preload_data(ctx)
        print(f"Server data loaded")

    # listen to any messages that start with '>>ask'
    if message.content.startswith(">>ask"):
        await chat(message)

    # listen to any messages that start with '>>art'
    if message.content.startswith(">>art"):
        await art(message)

    # listen to any messages that start with '>>apiart'
    if message.content.startswith(">>apiart"):
        await api_art(message)

    if message.content.startswith(">>gay") or message.content.startswith(">>queer") or message.content.startswith(">>lesbian") or message.content.startswith(">>homo"):
        await gay(message)

    if message.content.startswith(">>boobs"):
        await boobs(message)

    if message.content.startswith(">>cuddle"):
        await cuddle(message)

    if meow_listener(message):
        await meow_maker(message)

    #Marriage code
    if message.content.startswith(">>marry"):
        await marry(message)
    elif message.content.startswith(">>marriages"):
        await list_marriages(message)
    elif message.content.startswith(">>divorce"):
        await divorce(message)


        
    if message.content.startswith(">>stats"):
   
    # Shuffle the list
         random.shuffle(temp_messages)
    # Start the tasks
         count_task = asyncio.create_task(count_user_messages(message.channel, message.author))
         temp_messages_task = asyncio.create_task(send_temp_messages(message.channel, temp_messages))
    # Wait for the counting task to finish and get the result
         counter = await count_task
    # Cancel the task that sends the temporary messages
         temp_messages_task.cancel()
    # Send the final count
         await message.channel.send(f"You have sent {counter} messages in this channel.")
    elif message.content.startswith(">>words"):
        if data_loaded:
          await count_unique_words(message)
        else: 
            await message.channel.send("Data loading, please try again in 10 minutes")



async def chat(message: discord.Message):
    try:
        # get the prompt from the messsage by spliting the command
        command, text = message.content.split(" ", maxsplit=1)
    except ValueError:
        await message.channel.send("You mentioned me. How can I assist you? Try using: >>art, >>apiart, >>stats, >>charge, or >>words")
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
bot.run(TOKEN)