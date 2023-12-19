import asyncio
import discord

temp_messages = [
    "Counting your messages...",
    "Still counting...",
    "Creative mind you have here...",
    "Interesting read",
    "Can I turn this into a novel?",
    "They should make a movie out of this...",
    "Shocking",
    "Are you sure you want me to read these?",
    "What a rollercoaster!",
    "This is quite a journey...",
    "You've been busy, haven't you?",
    "Wow, you're quite the chatterbox!",
    "This might take a while...",
    "Hold on, still going...",
    "You sure have a lot to say!",
    "This is a treasure trove of messages!",
    "I'm impressed by your verbosity!",
    "Your messages are full of surprises!",
    "This is like reading a book!",
    "Your messages are quite entertaining!",
    "This is quite the saga...",
    "You've got quite the collection here!",
    "This is a lot to take in...",
    "Your messages are a gold mine of information!",
    "This is like a trip down memory lane...",
    "You've been quite active, haven't you?",
    "This is quite the conversation history!",
    "Your messages are quite insightful!",
    "This is like a novel in the making...",
    "You've got quite the knack for conversation!",
    "This is quite the message archive!",
    "Your messages are full of interesting tidbits!",
    "This is like a peek into your thoughts...",
    "You've got quite the message history!",
    "This is quite the text adventure...",
    "Your messages are quite engaging!",
    "This is like a journey through your messages...",
    "You've got quite the message log here!",
    "This is quite the message marathon...",
    "Your messages are quite captivating!",
    "This is like a tour of your conversations...",
    "You've got quite the message trail here!",
    "This is quite the message journey...",
    "Your messages are quite intriguing!",
    "This is like a voyage through your chats...",
    "You've got quite the message chronicle here!",
    "This is quite the message expedition...",
    "Your messages are quite fascinating!",
    ]

async def count_user_messages(channel, author):
    counter = 0
    async for msg in channel.history(limit=None):
        if msg.author == author:
            counter += 1
    return counter

async def send_temp_messages(channel, temp_messages):
      index = 0
      while True:
        temp_message = await channel.send(temp_messages[index])
        await asyncio.sleep(10)  # pause for a second
        await temp_message.delete()
        index = (index + 1) % len(temp_messages)