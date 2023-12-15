from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
import asyncio
from discord.ext import commands
import discord
import sqlite3
import pandas as pd


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='>>', intents=intents)


emoji_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)

common_words = ["the", "oh", "too", "yes", "no", "add", "nice", "im", "has", "hi", "did", "emoji", "ever", "am", "lol", "was", "is", "are", "be", "to", "of", "and", "a", "in", "that", "have", "I", "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"]

url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

# Regular expression to match numbers
number_pattern = re.compile(r'\b\d+\b')



# Connect to the SQL file
connect = sqlite3.connect('user_messages.sql')

# Create a table if it does not exist
with connect:
    connect.execute("CREATE TABLE IF NOT EXISTS DiscordData (UserID TEXT, Code TEXT, GuildID TEXT, Word TEXT, Frequency INTEGER)")


# Define a function to fetch user messages from Discord
async def fetch_discord_messages(guild):
    all_messages = {}
    for channel in guild.text_channels:
        # Check if the bot has the permission to read messages
        if channel.permissions_for(guild.me).read_messages:
            try:
                # Fetch the message history
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
                        all_messages[str(message.author.id)] = message_without_emojis + ' '
                    else:
                        all_messages[str(message.author.id)] += message_without_emojis + ' '
            except discord.Forbidden:
                # The bot does not have the permission to read the message history
                print(f"Failed to fetch history from channel {channel.name}, permission denied.")
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
    for member in guild.members:
        user_messages = await fetch_discord_messages(guild)

    # Insert the data into the table
    with connect:
        for user_id, messages in user_messages.items():
            # Calculate word frequencies
            word_freq = dict(Counter(messages.split()))
            for word, freq in word_freq.items():
                val = (user_id, messages, guild.id, word, freq)
                connect.execute("INSERT INTO DiscordData VALUES (?, ?, ?, ?, ?)", val)

    await ctx.send(f"Data preloaded from {guild.name}")


async def fetch_user_messages(user_id):
    try:
        user_messages = connect.execute("SELECT Code FROM DiscordData WHERE UserID = ?", (user_id,)).fetchall()
        user_messages = [message[0] for message in user_messages]
        return user_messages
    except Exception as e:
        print(f"Failed to fetch history from user {user_id}. Error: {e}")
        return []
        



async def calculate_tfidf(user_id): 
    user_messages = await fetch_user_messages(user_id)
    vectorizer = TfidfVectorizer(stop_words=common_words)
    tdidf_matrix = vectorizer.fit_transform(user_messages)
    tdidf_df = pd.DataFrame(tdidf_matrix.toarray(),
                            columns = vectorizer.get_feature_names_out())
    
    word_tdidf_sum = tdidf_df.sum()
    sorted_words = word_tdidf_sum.sort_values(ascending=False)
    top_15_words = sorted_words.head(15).index.tolist()
    return top_15_words


@bot.command()
async def count_unique_words(ctx, user_id: str):
    unique_words = await calculate_tfidf(user_id)
    unique_words_str = ', '.join(f'**{word}**' for word in unique_words)
    await ctx.send(f"The words that user {ctx.author.mention} utters incessantly compared to other users are: {unique_words_str}")