import discord
import random

meow_strings = [ "meow", "mew", "mrew", "mrow", "mrrp", "purr"]

def meow_listener(meow_test):
    # Check if message looks like a meow
    activated = False
    
    # For simplicity, just check if message matches any in list
    if any(meow_test.lower() == s for s in meow_strings):
        activated = True

    return activated


async def meow_maker(message: discord.Message):
    global last_meow

    probability = 1.0 # chance of meowing
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