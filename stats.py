from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
import asyncio
import json
from discord.ext import commands
import discord


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='>>', intents=intents)


emoji_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)

common_words = ["the", "im", "has", "hi", "did", "emoji", "ever", "am", "lol", "was", "is", "are", "be", "to", "of", "and", "a", "in", "that", "have", "I", "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"]

url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

# Regular expression to match numbers
number_pattern = re.compile(r'\b\d+\b')

@bot.command()
async def preload_data(ctx):
    guild = ctx.guild
    user_messages = {}
    for member in guild.members:
        user_messages[str(member.id)] = await fetch_user_messages(guild, member)

    # Save the data to a separate JSON file for this guild
    with open(f'user_messages_{guild.id}.json', 'w') as f:
        json.dump(user_messages, f)

    await ctx.send(f"Data preloaded from guild {guild.id}")


async def fetch_user_messages(guild, member):
    messages = ''
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).read_messages:
            try:
                async for message in channel.history(limit=None):
                    if message.author == member:
                        message_without_urls = url_pattern.sub('', message.content)
                        message_without_numbers = number_pattern.sub('', message_without_urls)
                        message_without_emoji_starting_words = ' '.join(word for word in message_without_numbers.split() if not word.startswith('emoji'))
                        # Exclude common words
                        message_without_common_words = ' '.join(word for word in message_without_emoji_starting_words.split() if word.lower() not in common_words)
                        # Exclude emojis
                        message_without_emojis = emoji_pattern.sub('', message_without_common_words)
                        messages += message_without_emojis + ' '
                        await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Failed to fetch history from channel {channel.name}, skipping. Error: {e}")
    return messages




async def calculate_tfidf(guild, command_author):
    with open('user_messages.json', 'r') as f:
        user_messages = json.load(f)
    
    messages = user_messages.get(str(command_author.id), '')

    # Initialize the vectorizer with stop words
    vectorizer = TfidfVectorizer(stop_words=common_words, min_df=0.0, max_df= 0.99)

    # Calculate TF-IDF
    tfidf_matrix = vectorizer.fit_transform([messages])

    # Get the indices of the words with the highest TF-IDF scores for this user
    indices_of_highest_tfidf_scores = np.argsort(tfidf_matrix.toarray()).flatten()[-50:]  # Get more words

    # Get the words that correspond to these indices and are longer than 4 characters
    most_unique_words_for_this_user = [vectorizer.get_feature_names_out()[index] for index in indices_of_highest_tfidf_scores if len(vectorizer.get_feature_names_out()[index]) > 4]

    # Return the top 10 words
    return most_unique_words_for_this_user[-10:]

# Start the task
async def count_unique_words(message):
    tfidf_task = asyncio.create_task(calculate_tfidf(message.guild, message.author))

    # Wait for the TF-IDF task to finish and get the result
    most_unique_words = await tfidf_task

    # Send the final count
    await message.channel.send(f"The words that {message.author.name} utters incessantly compared to other users are: {most_unique_words}")