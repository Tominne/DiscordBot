import torch
import torch.nn as nn
import torch.optim as optim
import nltk
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import sqlite3
from torch.utils.data import DataLoader

# Define the Language Model
class LanguageModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim):
        super(LanguageModel, self).__init__()
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.rnn = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, input, hidden):
        embedded = self.embeddings(input)
        output, hidden = self.rnn(embedded, hidden)
        output = self.fc(output)
        return output, hidden

# Preprocess the Data
def preprocess_data(messages):
    processed_tokens = []
    for message in messages:
        tokens = word_tokenize(message)
        lowercase_tokens = [word.lower() for word in tokens]
        stop_words = set(stopwords.words('english'))
        trimmed_tokens = [word for word in lowercase_tokens if not word in stop_words]
        stemmer = PorterStemmer()
        processed_tokens.extend([stemmer.stem(word) for word in trimmed_tokens])
    return processed_tokens

# Load the Data
def load_data():
    conn = sqlite3.connect('user_messages.sql')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT UserID, Code FROM DiscordData")
    messages = cur.fetchall()
    return messages

# Generate text
def generate_text(model, seed_sentence, max_length, word_to_index, index_to_word, device):
    model.eval()
    input = torch.tensor([word_to_index[word] for word in seed_sentence if word in word_to_index])
    input = input.to(device)
    hidden = None
    for _ in range(max_length):
        output, hidden = model(input, hidden)
        probabilities = torch.nn.functional.softmax(output, dim=2)
        predicted = torch.argmax(probabilities, dim=2)[:, -1]
        input = torch.cat((input, predicted), dim=1)
    generated_sentence = [index_to_word[index.item()] for index in input[0]]
    return ' '.join(generated_sentence)

# Main function
def main():
    # Load and preprocess the data
    messages = load_data()
    messages = [' '.join(message) for message in messages]
    processed_tokens = preprocess_data(messages)

    # Create a vocabulary and word-to-index mapping
    vocab = list(set(processed_tokens))
    word_to_index = {word: index for index, word in enumerate(vocab)}
    index_to_word = {index: word for word, index in word_to_index.items()}

    # Initialize the model
    embedding_dim = 100
    hidden_dim = 256
    model = LanguageModel(len(vocab), embedding_dim, hidden_dim)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)

    # TODO: Add the code to train your model using the data_loader

    # Generate text with the trained model
    seed_sentence = ['this', 'is', 'a', 'message']
    seed_sentence = ' '.join(seed_sentence)
    generated_sentence = generate_text(model, seed_sentence, 50, word_to_index, index_to_word, device)
    print(generated_sentence)

if __name__ == "__main__":
    main()
