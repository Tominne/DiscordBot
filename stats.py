from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
import asyncio

# List of 200 most common words in English
common_words = ["the", "im", "has", "hi", "did", "emoji", "ever", "am", "lol", "was", "is", "are", "be", "to", "of", "and", "a", "in", "that", "have", "I", "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"]

url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

# Regular expression to match numbers
number_pattern = re.compile(r'\b\d+\b')

# Regular expression to match emojis
emoji_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)

async def calculate_tfidf(guild, command_author):
    # Create a string to hold all messages for the command author
    user_messages = ''

    # Iterate over all text channels in the guild
    for channel in guild.text_channels:
        # Check if the bot has permission to read the channel
        if channel.permissions_for(guild.me).read_messages:
            try:
                async for message in channel.history(limit=None):
                    # Only append messages from the command author
                    if message.author == command_author:
                        # Remove URLs from the message
                        message_without_urls = url_pattern.sub('', message.content)
                        # Remove numbers from the message
                        message_without_numbers = number_pattern.sub('', message_without_urls)
                        # Remove words starting with "emoji"
                        message_without_emoji_starting_words = ' '.join(word for word in message_without_numbers.split() if not word.startswith('emoji'))
                        user_messages += message_without_emoji_starting_words + ' '
            except Exception as e:
                print(f"Failed to fetch history from channel {channel.name}, skipping. Error: {e}")

    # Initialize the vectorizer with stop words
    vectorizer = TfidfVectorizer(stop_words=common_words)

    # Calculate TF-IDF
    tfidf_matrix = vectorizer.fit_transform([user_messages])

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