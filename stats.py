from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
import asyncio

# List of 200 most common words in English
common_words = ["the", "im", "has", "was", "is", "are", "be", "to", "of", "and", "a", "in", "that", "have", "I", "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"]

async def calculate_tfidf(guild, command_author):
    # Create a string to hold all messages for the command author
    user_messages = ''

    # Regular expression to match URLs
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    # Iterate over all text channels in the server
    for channel in guild.text_channels:
        # Check if the bot has permission to read the channel
        if channel.permissions_for(guild.me).read_messages:
            try:
                async for message in channel.history(limit=None):
                    # Only append messages from the command author
                    if message.author == command_author:
                        # Remove URLs from the message
                        message_without_urls = url_pattern.sub('', message.content)
                        user_messages += message_without_urls + ' '
            except Exception as e:
                print(f"Failed to fetch history from channel {channel.name}, skipping. Error: {e}")

    # Initialize the vectorizer with stop words
    vectorizer = TfidfVectorizer(stop_words=common_words)

    # Calculate TF-IDF
    tfidf_matrix = vectorizer.fit_transform([user_messages])

    # Get the indices of the words with the ten highest TF-IDF scores for this user
    indices_of_highest_tfidf_scores = np.argsort(tfidf_matrix.toarray()).flatten()[-10:]

    # Get the words that correspond to these indices
    most_unique_words_for_this_user = [vectorizer.get_feature_names_out()[index] for index in indices_of_highest_tfidf_scores]

    return most_unique_words_for_this_user

# Start the task
async def count_unique_words(message):
    tfidf_task = asyncio.create_task(calculate_tfidf(message.guild, message.author))

    # Wait for the TF-IDF task to finish and get the result
    most_unique_words = await tfidf_task

    # Send the final count
    await message.channel.send(f"The words that {message.author.name} utters incessantly compared to other users are: {most_unique_words}")