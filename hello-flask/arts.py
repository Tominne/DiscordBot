import random
import discord


ascii_arts = [
    """
    ^_^
    """,
    """
    ¯\_(ツ)_/¯
    """,
    """
    (╯°□°）╯︵ ┻━┻
    """,
    """
    ಠ_ಠ
    """,
    """
    ʕ•ᴥ•ʔ
    """,
    """
    (づ｡◕‿‿◕｡)づ
    """,
    """
    (ノಠ益ಠ)ノ彡┻━┻
    """,
    """
    (☞ﾟヮﾟ)☞ ☜(ﾟヮﾟ☜)
    """,
    """
    ༼ つ ◕_◕ ༽つ
    """,
    """
    ಥ_ಥ
    """,
    """
    (•_•) ( •_•)>⌐■-■ (⌐■_■)
    """,
    """
    (._.)
    """,
    """
    (¬‿¬)
    """,
    """
    (T_T)
    """,
    """
    (ಥ﹏ಥ)
    """,
    """
    (._.)
    """,
    """
    (っ◕‿◕)っ
    """,
    """
    (づ￣ ³￣)づ
    """,
    """
    (｡♥‿♥｡)
    """,
    """
    ( ͡° ͜ʖ ͡°)
    """,
    """
    (ง'̀-'́)ง
    """,
    """
    (✿◠‿◠)
    """,
    """
    (◕‿◕✿)
    """,
    """
    (｡◕‿‿◕｡)
    """,
    """
    (☞ﾟ∀ﾟ)☞
    """,
    """
    (づ￣ ³￣)づ
    """,
    """
    (─‿‿─)
    """,
    """
    (｡♥‿♥｡)
    """,
    """
    ( ͡ᵔ ͜ʖ ͡ᵔ )
    """,
    """
    (¬‿¬)
    """,
    """
    (◕‿◕)
    """,
    """
    (｡◕‿‿◕｡)
    """,
    """
    (っ◕‿◕)っ
    """,
    """
    (づ￣ ³￣)づ
    """,
    """
    (｡♥‿♥｡)
    """,
    """
    ( ͡° ͜ʖ ͡°)
    """,
    """
    (ง'̀-'́)ง
    """,
    """
    (✿◠‿◠)
    """,
    """
    (◕‿◕✿)
    """,
    """
    (｡◕‿‿◕｡)
    """,
    """
    (☞ﾟ∀ﾟ)☞
    """,
    """
    (づ￣ ³￣)づ
    """,
    """
    (─‿‿─)
    """,
    """
    (｡♥‿♥｡)
    """,
    """
    ( ͡ᵔ ͜ʖ ͡ᵔ )
    """,
    """
    (¬‿¬)
    """,
    """
    (◕‿◕)
    """,
    """
    (｡◕‿‿◕｡)
    """,
    """
    (っ◕‿◕)っ
    """,
    """
    (づ￣ ³￣)づ
    """,
    """
    (｡♥‿♥｡)
    """,
    """
    ( ͡° ͜ʖ ͡°)
    """,
    """
    (ง'̀-'́)ง
    """,
    """
    / \__
  (      @\___
 /                 O
/         (_____/
/_____/  U
    """,  # This is a duck
    """
     /\     /\
    {  `---'  }
    {  O   O  }
    ~~>  V  <~~
     \ \|/ /
      `-----'____
     /     \    \_
    {       }\  )_\_   _
    |  \_/  |/ /  \_\_/ )
     \__/  /(_/     \__/
       (__/
    """,  # This is a cat
    """
     /\_/\  
    ( o.o ) 
    > ^ <
    """,  # This is another cat
    """
    (\(\ 
    (-.-)
    o_(")(")
    """,  # This is a bunny
    """
     /\_/\
    ( o.o )
    > ^ <
    """,  # This is yet another cat
    """
    / \__
  (      @\___
 /                 O
/         (_____/
/_____/  U
    """,  # This is another duck
    """
    / \__
  (      @\___
 /                 O
/         (_____/
/_____/  U
    """,  # And one more duck for good measure
    # add more ASCII arts here...
]

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