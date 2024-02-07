# bot.py
from os import getenv
import openai
import discord
from dotenv import load_dotenv
from openai import OpenAI
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
from stats import count_unique_words,json_user_messages, preload_data, update_data, count_unique_NSFW_words
from discord.ext import commands
#from seq2seq import getTestInput, idsToSentence, encoderInputs, wordList, maxEncoderLength, decoderPrediction
import sqlite3
import tensorflow as tf

sess = tf.compat.v1.Session()


intents = discord.Intents.default()
intents.message_content = True

message_stats = defaultdict(int)
load_dotenv()


TOKEN = getenv('DISCORD_TOKEN')
aiKey = getenv('OPENAI_API_KEY')
client = OpenAI(api_key=aiKey)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or('>>'), intents=intents)
# Connect to the SQL file
connect = sqlite3.connect('user_messages.sql')

# Create a table if it does not exist
with connect:
    connect.execute("CREATE TABLE IF NOT EXISTS DiscordData (UserID TEXT, Code TEXT, GuildID TEXT, ChannelID TEXT, Word TEXT, Frequency INTEGER, MessageID INTEGER)")
    


@bot.event
async def on_ready():
    
    with connect:
        curs = connect.cursor()
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
        await message.channel.send('Charging...')
        ctx = await bot.get_context(message)
        await preload_data(ctx)
        print(f"Server data loaded")
        data_loaded = True

    # listen to any messages that start with '>>ask'
    if message.content.startswith(">>ask"):
        await chat(message)

    # listen to any messages that start with '>>art'
    if message.content.startswith(">>art"):
        await art(message)

    # json user msges for data trainging
    if message.content.startswith(">>jsonify"):

      ctx = await bot.get_context(message)

      split_message = message.content.split(" ", maxsplit=2)
      if len(split_message) < 2:
        await message.channel.send("Please @ mention a user after the >>jsonify command")
        return
      
      command, mention = split_message
      
      user = message.mentions[0] if message.mentions else None

      if user is None:
        await message.channel.send(f"User not found. Use @ to mention a user")
        return
      await ctx.send(f"Jsonifying {user.name}...")
      await json_user_messages(ctx, user)

    # listen to any messages that start with '>>apiart'
    if message.content.startswith(">>apiart"):
        await api_art(message)

    if message.content.startswith(">>gay") or message.content.startswith(">>queer") or message.content.startswith(">>lesbian") or message.content.startswith(">>homo"):
        await gay(message)

    if message.content.startswith(">>boobs"):
        await boobs(message)

    if message.content.startswith(">>cuddle") or message.content.startswith(">>hug"):
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
    
    morning_messages = [
    "Good morning, I'm awake!",
    "Rise and shine!",
    "Top of the morning to you!",
    "Wakey, wakey, eggs and bakey!",
    "Morning sunshine!",
    "Hello world, I'm up!",
    "Ready for a new day!",
    "Time to seize the day!",
    "Let's make today great!",
    "Up and at 'em!",
    "Let's get this day started!",
    "Good morning, let's roll!",
    "Time to rise and grind!",
    "A new day has begun!",
    "Ready to make the most of today!",
    "Good morning, time to shine!",
    "Hello, beautiful morning!",
    "Time to wake up and be awesome!",
    "Good morning, let's do this!",
    "Rise and sparkle!",
    "Hello, new day!",
    "Good morning, bring on the coffee!",
    "Time to rise and be amazing!",
    "Good morning, let's make today count!",
    "Ready to embrace the day!",
    "Good morning, let's get moving!",
    "Hello, let's make today fantastic!",
    "Rise and thrive!",
    "Good morning, let's conquer the day!",
    "Time to wake up and chase our dreams!",
    "Good morning, let's make magic happen!"
]

    morning_message = random.choice(morning_messages)
    if message.content == '>>awake?':
        await message.channel.send(morning_message)
        


        
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
          ctx = await bot.get_context(message)
          await message.channel.send('Counting...')
          await count_unique_words(ctx, message.author.id, ctx.guild.id)
    elif message.content.startswith(">>spicy"):
          ctx = await bot.get_context(message)
          await message.channel.send('Counting...')
          await count_unique_NSFW_words(ctx, message.author.id, ctx.guild.id)
    elif message.content.startswith(">>update"):
        ctx = await bot.get_context(message)
        await update_data(ctx)
        
"""@bot.command()
async def chat(ctx, *, message):
    # Preprocess the message
    inputVector = getTestInput(message, wordList, maxEncoderLength)
    
    # Generate a response
    feedDict = {encoderInputs[t]: inputVector[t] for t in range(maxEncoderLength)}
    ids = (sess.run(decoderPrediction, feed_dict=feedDict))
    
    # Convert the response to a string
    response = idsToSentence(ids, wordList)
    
    # Send the response
    await ctx.send(response)"""

async def chat(message: discord.Message):
    try:
        # get the prompt from the messsage by spliting the command
        command, text = message.content.split(" ", maxsplit=1)
    except ValueError:
        await message.channel.send("You mentioned me. How can I assist you? Try using: >>art, >>update, >>boobs, >>gay, >>marriage, >>apiart, >>stats, >>charge, or >>words")
        return

    response = client.completions.create(model="gpt-3.5-turbo",
  prompt=[
    {
      "role": "system",
      "content": "You are David Malan, a chatbot pretending to be a Computer Science senior lecturer at Harvard, that reluctantly answers questions with sarcastic responses."
    },
    {
      "role": "user",
      "content": "How much ram is in an average computer?"
    },
    {
      "role": "David Malan",
      "content": "This again? 16GB RAM is considered a good amount for most tasks, allowing you to run multiple applications, web browser tabs, and mid to high-end games. Please make a note of this."
    },
    {
      "role": "user",
      "content": "What does HTML stand for?"
    },
    {
      "role": "David Malan",
      "content": "Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future."
    },
    {
      "role": "user",
      "content": "When did the first airplane fly?"
    },
    {
      "role": "David Malan",
      "content": "On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they’d come and take me away."
    },
    {
      "role": "user",
      "content": "What time is it?"
    }
  ],
    temperature=0.8,
    max_tokens=512,
    top_p=1)

    # Extract the response from the API response
    response_text = response["choices"][0]["text"]

    await message.channel.send(response_text)



# start the bot
bot.run(TOKEN)