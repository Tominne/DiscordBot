import discord
import random

pride_flags = [ "🖤🤎❤️🧡💛💚💙💜", "🏳️‍🌈", "🏳️‍⚧️", "⚧️", "👭", "👬", "💏‍👩‍❤️‍💋‍👩", "💏‍👨‍❤️‍💋‍👨", "👩‍❤️‍👩", "👨‍❤️‍👨", "❤️‍🔥"]

async def gay(message: discord.Message):
    global last_emoji
    # select a random pride flag from the list
    flag = random.choice(pride_flags)
    # If the selected flag is the same as the last one, choose again
    while flag == last_emoji:
        flag = random.choice(pride_flags)
    # Remember the last sent emoji
    last_emoji = flag

    await message.channel.send(flag)