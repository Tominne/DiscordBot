from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
import asyncio
from discord.ext import commands
import discord
import sqlite3
import pandas as pd
import logging


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='>>', intents=intents)


emoji_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)

common_words = ["the", "ve", "ll", "divorce", "stats", "marriage", "chance", "marriages", "apiart", "words", "art", "charge", "had", "being", "right", "don", "they", "re", "you", "oh", "too", "yes", "no", "add", "nice", "im", "has", "hi", "did", "emoji", "ever", "am", "lol", "was", "is", "are", "be", "to", "of", "and", "a", "in", "that", "have", "I", "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"]

url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

# Regular expression to match numbers
number_pattern = re.compile(r'\b\d+\b')



# Connect to the SQL file
connect = sqlite3.connect('user_messages.sql')

# Create a table if it does not exist
with connect:
    connect.execute("CREATE TABLE IF NOT EXISTS DiscordData (UserID TEXT, Code TEXT, GuildID TEXT, ChannelID TEXT, Word TEXT, Frequency INTEGER, MessageID INTEGER)")
    


# Define a function to fetch user messages from Discord
async def fetch_discord_messages(guild):
    all_messages = {}
    for channel in guild.text_channels:
        # Check if the bot has the permission to read messages
        if channel.permissions_for(guild.me).read_messages:
            try:
                async for message in channel.history(limit=None):
                    # Preprocess the message content
                    message_without_urls = url_pattern.sub('', message.content)
                    message_without_numbers = number_pattern.sub('', message_without_urls)
                    message_without_emoji_starting_words = ' '.join(word for word in message_without_numbers.split() if not word.startswith('emoji'))
                    # Exclude common words
                    message_without_common_words = ' '.join(word for word in message_without_emoji_starting_words.split() if word.lower() not in common_words)
                    # Exclude emojis
                    message_without_emojis = emoji_pattern.sub('', message_without_common_words)
                    
                    # Add the message to the corresponding user's messages
                    if str(message.author.id) not in all_messages:
                        all_messages[str(message.author.id)] = [(message_without_emojis + ' ', channel.id, [message.id])]  
                    else:
                        all_messages[str(message.author.id)].append((message_without_emojis + ' ', channel.id, [message.id])) 
            except discord.NotFound:
                # The channel or the message does not exist
                print(f"Failed to fetch history from channel {channel.name}, channel or message not found.")
            except discord.HTTPException:
                # An HTTP request failed
                print(f"Failed to fetch history from channel {channel.name}, HTTP request failed.")
    return all_messages


@bot.command()
async def preload_data(ctx):
    guild = ctx.guild

    # Check if data for this guild is already loaded
    with connect:
        curs = connect.cursor()
        curs.execute("SELECT DISTINCT GuildID FROM DiscordData WHERE GuildID = ? LIMIT 1", (guild.id,))
        data = curs.fetchone()

    # If data is not None, it means data is already loaded
    if data is not None:
        await ctx.send(f"Data from {guild.name} is already charged. Update data with: >>update")
    else:
        # If not, fetch and load the data
        user_messages = await fetch_discord_messages(guild)

        # Insert the data into the table
        with connect:
            curs = connect.cursor()
            curs.execute("CREATE INDEX IF NOT EXISTS idx_GuildID ON DiscordData (GuildID)")
            curs.execute("CREATE INDEX IF NOT EXISTS idx_ChannelID ON DiscordData (ChannelID)")
            for user_id, messages in user_messages.items():
                # Calculate word frequencies
                for message, channel_id, message_id in messages:
                    word_freq = dict(Counter(message.split()))
                    for word, freq in word_freq.items():
                        val = (user_id, message, guild.id, channel_id, word, freq, ', '.join(map(str, message_id)))
                        connect.execute("INSERT INTO DiscordData VALUES (?, ?, ?, ?, ?, ?, ?)", val)

        await ctx.send(f"Data preloaded from {guild.name}")



#Update Sql Data

@bot.command()
async def update_data(ctx):
    guild = ctx.guild
    data_updated = False
    message_count = 0
    
    last_message_id_dict = get_last_message_id(guild.id)
    last_message_id = max(last_message_id_dict.values())



    new_messages = await fetch_new_discord_messages(guild, last_message_id)

    if new_messages:
            with connect:
                for user_id, data in new_messages.items():
                    message, channel_id, message_ids = data
                    word_freq = dict(Counter(message.split()))
                  
                    for word, freq in word_freq.items():
                       for message_id in message_ids:  
                          val = (user_id, message, guild.id, channel_id, word, freq, message_id)
                          connect.execute("INSERT INTO DiscordData VALUES (?, ?, ?, ?, ?, ?, ?)", val)
                          message_count += 1
            data_updated = True  
            print(f"Updated {message_count} messages.")

    if data_updated: 
        await ctx.send(f"Data updated for {guild.name}")
    else:
        await ctx.send(f"No new data to update for {guild.name}")



def get_last_message_id(guild_id):
    with connect:
        curs = connect.cursor()
        curs.execute("SELECT UserID, MAX(MessageID) FROM DiscordData WHERE GuildID = ? GROUP BY UserID", (guild_id,))
        last_message_id = {row[0]: row[1] for row in curs.fetchall()}

        return last_message_id
    

async def fetch_new_discord_messages(guild, last_message_id):
    new_messages = {}
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).read_messages:
            try:
                if last_message_id is None:
                    messages = channel.history()
                else:
                    messages = channel.history(after=discord.Object(id=last_message_id))
                
                async for message in messages:

                    message_without_urls = url_pattern.sub('', message.content)
                    message_without_numbers = number_pattern.sub('', message_without_urls)
                    message_without_emoji_starting_words = ' '.join(word for word in message_without_numbers.split() if not word.startswith('emoji'))

                    message_without_common_words = ' '.join(word for word in message_without_emoji_starting_words.split() if word.lower() not in common_words)

                    message_without_emojis = emoji_pattern.sub('', message_without_common_words)

                    if str(message.author.id) not in new_messages:
                        new_messages[str(message.author.id)] = [message_without_emojis + ' ', channel.id, [message.id]]
                    else:
                        new_messages[str(message.author.id)][0] += message_without_emojis + ' '
                        new_messages[str(message.author.id)][2].append(message.id)
            except discord.Forbidden:
                print(f"couldnt get new msg history")
            except discord.NotFound:
                print(f"Failed to fetch history from channel {channel.name}, channel or message not found.")
            except discord.HTTPException:
                print(f"Failed to fetch history from channel {channel.name}, HTTP request failed.")
    return new_messages




def update_last_message_id(user_id, guild_id, last_message_id):
    with connect:
        curs = connect.cursor()
        curs.execute("UPDATE DiscordData SET MessageId = ? WHERE UserID = ? AND GuildID = ?", (last_message_id, user_id, guild_id))
        

async def fetch_user_messages(user_id, guild_id, start, end):
    try:
        query = """
        SELECT Code 
        FROM DiscordData 
        WHERE UserID = ? AND GuildID = ? 
        LIMIT ? OFFSET ?
        """
        params = (user_id, guild_id, end - start, start)
        user_messages = connect.execute(query, params).fetchall()
        user_messages = [message[0] for message in user_messages if message[0] not in common_words and not re.match(r'link', message[0])]

        return user_messages
    except Exception as e:
        print(f"Failed to fetch history from user {user_id}. Error: {e}")
        return []


#get unique words


# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

async def calculate_tfidf(user_id, guild_id, chunk_size=1000):
    vectorizer = TfidfVectorizer(stop_words=common_words)
    word_tfidf_sum = None

    start = 0
    while True:
        user_messages = await fetch_user_messages(user_id, guild_id, start, start + chunk_size)
        if not user_messages:
            break

        # Log the number of messages fetched
        logger.info(f"Fetched {len(user_messages)} messages for user {user_id} in guild {guild_id}")

        # Preprocess user_messages
        user_messages = [str(msg) for msg in user_messages if msg and msg.strip()]

        try:
            # Run fit_transform in a separate thread
            tfidf_matrix = await asyncio.to_thread(vectorizer.fit_transform, user_messages)
            tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
            if word_tfidf_sum is None:
                word_tfidf_sum = tfidf_df.sum()
            else:
                word_tfidf_sum = word_tfidf_sum.add(tfidf_df.sum(), fill_value=0)
        except ValueError:
            print(f"No valid words to count in here {start} to {start + chunk_size}")

        start += chunk_size

    if word_tfidf_sum is not None:
        sorted_words = word_tfidf_sum.sort_values(ascending=False)
        top_15_words = sorted_words.head(15).index.tolist()
        return top_15_words
    else:
        return []
    

async def fetch_NSFW_user_messages(user_id, guild_id, start, end):
    # Check if the ChannelID column exists
    cursor = connect.execute("PRAGMA table_info(DiscordData)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'ChannelID' not in columns:
        # Add the ChannelID column if it doesn't exist
        connect.execute("ALTER TABLE DiscordData ADD COLUMN ChannelID TEXT")

    try:
        query = """
        SELECT Code 
        FROM DiscordData 
        WHERE UserID = ? AND GuildID = ? AND ChannelID = '1143073764997865472' 
        LIMIT ? OFFSET ?
        """
        params = (user_id, guild_id, end - start, start)
        user_messages = connect.execute(query, params).fetchall()
        user_messages = [message[0] for message in user_messages if message[0] not in common_words and not re.match(r'link', message[0])]

        return user_messages
    except Exception as e:
        print(f"Failed to fetch history from user {user_id}. Error: {e}")
        return []


async def calculate_NSFW_tfidf(user_id, guild_id, chunk_size=1000):
    vectorizer = TfidfVectorizer(stop_words=common_words)
    word_tfidf_sum = None

    start = 0
    while True:
        user_messages = await fetch_NSFW_user_messages(user_id, guild_id, start, start + chunk_size)
        if not user_messages:
            break

        # Log the number of messages fetched
        logger.info(f"Fetched {len(user_messages)} messages for user {user_id} in guild {guild_id}")

        # Preprocess user_messages
        user_messages = [str(msg) for msg in user_messages if msg and msg.strip()]

        try:
            # Run fit_transform in a separate thread
            tfidf_matrix = await asyncio.to_thread(vectorizer.fit_transform, user_messages)
            tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
            if word_tfidf_sum is None:
                word_tfidf_sum = tfidf_df.sum()
            else:
                word_tfidf_sum = word_tfidf_sum.add(tfidf_df.sum(), fill_value=0)
        except ValueError:
            print(f"No valid words to count in here {start} to {start + chunk_size}")

        start += chunk_size

    if word_tfidf_sum is not None:
        sorted_words = word_tfidf_sum.sort_values(ascending=False)
        top_15_words = sorted_words.head(15).index.tolist()
        return top_15_words
    else:
        return []
    
@bot.command()
async def count_unique_words(ctx, user_id: str, guild_id: str):
    unique_words = await calculate_tfidf(user_id, guild_id)
    unique_words_str = ', '.join(f'**{word}**' for word in unique_words)
    if not isinstance(ctx, str):
      await ctx.send(f"The words that user {ctx.author.mention} utters incessantly compared to other users are: {unique_words_str}")
    
@bot.command()
async def count_unique_NSFW_words(ctx, user_id: str, guild_id: str):
    unique_words = await calculate_NSFW_tfidf(user_id, guild_id)
    unique_words_str = ', '.join(f'**{word}**' for word in unique_words)
    if not isinstance(ctx, str):
      await ctx.send(f"The words that user {ctx.author.mention} utters incessantly compared to other users are: {unique_words_str}")
    

 
 