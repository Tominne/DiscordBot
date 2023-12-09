import discord
import random

meow_strings = [ "meow", "mew", "mrew", "mrow", "mrrp", "purr"]
last_meow = None

def meow_listener(message):
    # Check if message looks like a meow
    activated = False
    
    # For simplicity, just check if message matches any in list
    if any(message.content.lower() == s for s in meow_strings):
        activated = True

    return activated


async def meow_maker(message: discord.Message):
    global last_meow

    probability = 0.25 # chance of meowing
    if random.random() > probability:
        return

    # select a random meow from the list
    meow_sel = random.choice(meow_strings)
    # If the selected meow is the same as the last one, choose again
    while meow_sel == last_meow:
        meow_sel = random.choice(meow_strings)
    # Remember the last sent meow
    last_meow = meow_sel

    await message.channel.send(meow_sel)