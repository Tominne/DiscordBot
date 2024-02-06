"""import tensorflow as tf
import numpy as np
from random import randint
import datetime
from sklearn.utils import shuffle
import os
# Removes an annoying Tensorflow warning
os.environ['CUDA_DIR']='2'
tf.compat.v1.disable_eager_execution()
import sqlite3
databaseName = 'user_messages.sql'


# Define your inputs
encoderInputs = tf.keras.Input(shape=(None, 100))
decoderInputs = tf.keras.Input(shape=(None, 100))

# Define your LSTM layers
encoderLSTM = tf.keras.layers.LSTM(50, return_sequences=True, return_state=True)
decoderLSTM = tf.keras.layers.LSTM(50, return_sequences=True, return_state=True)

# Connect your LSTM layers
encoderOutputs, state_h, state_c = encoderLSTM(encoderInputs)
encoderStates = [state_h, state_c]

decoderOutputs, _, _ = decoderLSTM(decoderInputs, initial_state=encoderStates)

# Add attention
attention = tf.keras.layers.Attention()([decoderOutputs, encoderOutputs])
concat = tf.keras.layers.Concatenate()([decoderOutputs, attention])

# Add a dense layer to produce your final output
outputLayer = tf.keras.layers.Dense(5000, activation='softmax')
outputs = outputLayer(concat)

# Create your model
model = tf.keras.Model([encoderInputs, decoderInputs], outputs)
def createTrainingMatrices(databaseName, wList, maxLen):
    # Connect to the SQLite database
    conn = sqlite3.connect(databaseName)
    curs = conn.cursor()

    # Execute a query to get all the data
    curs.execute("SELECT * FROM DiscordData")
    conversationDictionary = curs.fetchall()

    numExamples = len(conversationDictionary)
    xTrain = np.zeros((numExamples, maxLen), dtype='int32')
    yTrain = np.zeros((numExamples, maxLen), dtype='int32')

    for index, (user_id, code, guild_id, channel_id, word, freq, message_id) in enumerate(conversationDictionary):
        # Will store integerized representation of strings here (initialized as padding)
        encoderMessage = np.full((maxLen), wList.index('<pad>'), dtype='int32')
        decoderMessage = np.full((maxLen), wList.index('<pad>'), dtype='int32')

        # Getting all the individual words in the strings
        keySplit = user_id.split()
        valueSplit = code.split()
        keyCount = len(keySplit)
        valueCount = len(valueSplit)

        # Throw out sequences that are too long or are empty
        if (keyCount > (maxLen - 1) or valueCount > (maxLen - 1) or valueCount == 0 or keyCount == 0):
            continue

        # Integerize the encoder string
        for keyIndex, word in enumerate(keySplit):
            try:
                encoderMessage[keyIndex] = wList.index(word)
            except ValueError:
                # TODO: This isnt really the right way to handle this scenario
                encoderMessage[keyIndex] = 0
        encoderMessage[keyIndex + 1] = wList.index('<EOS>')

        # Integerize the decoder string
        for valueIndex, word in enumerate(valueSplit):
            try:
                decoderMessage[valueIndex] = wList.index(word)
            except ValueError:
                decoderMessage[valueIndex] = 0
        decoderMessage[valueIndex + 1] = wList.index('<EOS>')

        xTrain[index] = encoderMessage
        yTrain[index] = decoderMessage

    # Remove rows with all zeros
    yTrain = yTrain[~np.all(yTrain == 0, axis=1)]
    xTrain = xTrain[~np.all(xTrain == 0, axis=1)]
    numExamples = xTrain.shape[0]

    return numExamples, xTrain, yTrain


def getTrainingBatch(databaseName, wList, localBatchSize, maxLen):
    # Connect to the SQLite database
    conn = sqlite3.connect(databaseName)
    curs = conn.cursor()

    # Execute a query to get all the data
    curs.execute("SELECT * FROM DiscordData")
    conversationDictionary = curs.fetchall()

    numTrainingExamples = len(conversationDictionary)
    num = randint(0,numTrainingExamples - localBatchSize - 1)
    arr = conversationDictionary[num:num + localBatchSize]
    labels = conversationDictionary[num:num + localBatchSize]

    # The rest of your function remains the same...

def translateToSentences(inputs, wList, encoder=False):
    EOStokenIndex = wList.index('<EOS>')
    padTokenIndex = wList.index('<pad>')
    numStrings = len(inputs[0])
    numLengthOfStrings = len(inputs)
    listOfStrings = [''] * numStrings
    for mySet in inputs:
        for index,num in enumerate(mySet):
            if (num != EOStokenIndex and num != padTokenIndex):
                if (encoder):
                    # Encodings are in reverse!
                    listOfStrings[index] = wList[num] + " " + listOfStrings[index]
                else:
                    listOfStrings[index] = listOfStrings[index] + " " + wList[num]
    listOfStrings = [string.strip() for string in listOfStrings]
    return listOfStrings

inputMessage = "meow im a cat"

def getTestInput(inputMessage, wList, maxLen):
    encoderMessage = np.full((maxLen), wList.index('<pad>'), dtype='int32')
    inputSplit = inputMessage.lower().split()
    for index,word in enumerate(inputSplit):
        try:
            encoderMessage[index] = wList.index(word)
        except ValueError:
            continue
    encoderMessage[index + 1] = wList.index('<EOS>')
    encoderMessage = encoderMessage[::-1]
    encoderMessageList=[]
    for num in encoderMessage:
        encoderMessageList.append([num])
    return encoderMessageList


def idsToSentence(ids, wList):
    EOStokenIndex = wList.index('<EOS>')
    padTokenIndex = wList.index('<pad>')
    myStr = ""
    listOfResponses=[]
    for num in ids:
        if (num[0] == EOStokenIndex or num[0] == padTokenIndex):
            listOfResponses.append(myStr)
            myStr = ""
        else:
            myStr = myStr + wList[num[0]] + " "
    if myStr:
        listOfResponses.append(myStr)
    listOfResponses = [i for i in listOfResponses if i]
    return listOfResponses

# Hyperparamters
batchSize = 24
maxEncoderLength = 15
maxDecoderLength = maxEncoderLength
lstmUnits = 112
embeddingDim = lstmUnits
numLayersLSTM = 3
numIterations = 500000

# Loading in all the data structures



conn = sqlite3.connect(databaseName)
curs = conn.cursor()
curs.execute("SELECT DISTINCT word FROM DiscordData")
data = curs.fetchall()

wordList = [item[0] for item in data]
vocabSize = len(wordList)

# If you've run the entirety of word2vec.py then these lines will load in
# the embedding matrix.
if (os.path.isfile('embeddingMatrix.npy')):
    wordVectors = np.load('embeddingMatrix.npy')
    wordVecDimensions = wordVectors.shape[1]
else:
    question = 'Since we cant find an embedding matrix, how many dimensions do you want your word vectors to be?: '
    wordVecDimensions = int(input(question))

# Add two entries to the word vector matrix. One to represent padding tokens,
# and one to represent an end of sentence token
padVector = np.zeros((1, wordVecDimensions), dtype='int32')
EOSVector = np.ones((1, wordVecDimensions), dtype='int32')
if (os.path.isfile('embeddingMatrix.npy')):
    wordVectors = np.concatenate((wordVectors,padVector), axis=0)
    wordVectors = np.concatenate((wordVectors,EOSVector), axis=0)

# Need to modify the word list as well
wordList.append('<pad>')
wordList.append('<EOS>')
vocabSize = vocabSize + 2

numTrainingExamples, xTrain, yTrain = createTrainingMatrices(databaseName, wordList, maxEncoderLength)
np.save('Seq2SeqXTrain.npy', xTrain)
np.save('Seq2SeqYTrain.npy', yTrain)
print('Finished creating training matrices')

tf.compat.v1.reset_default_graph()

# Create the placeholders
encoderInputs = tf.keras.Input(shape=(None,))
decoderInputs = tf.keras.Input(shape=(None,))
decoderLabels = [tf.compat.v1.placeholder(tf.int32, shape=(None,)) for i in range(maxDecoderLength)]
feedPrevious = tf.compat.v1.placeholder(tf.bool)


encoderEmbedding = tf.keras.layers.Embedding(input_dim=vocabSize, output_dim=embeddingDim)(encoderInputs)
decoderEmbedding = tf.keras.layers.Embedding(input_dim=vocabSize, output_dim=embeddingDim)(decoderInputs)

# Define your LSTM layers
encoderLSTM = tf.keras.layers.LSTM(lstmUnits, return_sequences=True, return_state=True)
decoderLSTM = tf.keras.layers.LSTM(lstmUnits, return_sequences=True, return_state=True)

# Connect your LSTM layers
encoderOutputs, state_h, state_c = encoderLSTM(encoderEmbedding)
encoderStates = [state_h, state_c]

decoderOutputs, _, _ = decoderLSTM(decoderEmbedding, initial_state=encoderStates)

# Add attention
attention = tf.keras.layers.Attention()([decoderOutputs, encoderOutputs])
concat = tf.keras.layers.Concatenate()([decoderOutputs, attention])

# Add a dense layer to produce your final output
outputLayer = tf.keras.layers.Dense(vocabSize, activation='softmax')
outputs = outputLayer(concat)

# Define your model
model = tf.keras.Model([encoderInputs, decoderInputs], outputs)
sess = tf.compat.v1.Session()

# Uploading results to Tensorboard
loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
optimizer = tf.keras.optimizers.Adam()
decoderPrediction = tf.argmax(outputs, axis=-1)


inputMessage = "some test message"  # replace this with your actual test message
x_test = getTestInput(inputMessage, wordList, maxEncoderLength)

y_pred = model.predict(x_test)
# Assuming `y_true` is your true labels and `y_pred` is your model's predictions
loss_value = loss(yTrain, y_pred)
tf.summary.scalar('Loss', loss_value)

merged = tf.summary.merge_all()
logdir = "tensorboard/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "/"
writer = tf.summary.FileWriter(logdir, sess.graph)

# Some test strings that we'll use as input at intervals during training
encoderTestStrings = ["whats up",
					"hi",
					"hey how are you",
					"what are you up to",
					"that dodgers game was awesome"
					]

zeroVector = np.zeros((1), dtype='int32')

for i in range(numIterations):

    encoderTrain, decoderTargetTrain, decoderInputTrain = getTrainingBatch(xTrain, yTrain, batchSize, maxEncoderLength)
    feedDict = {encoderInputs[t]: encoderTrain[t] for t in range(maxEncoderLength)}
    feedDict.update({decoderLabels[t]: decoderTargetTrain[t] for t in range(maxDecoderLength)})
    feedDict.update({decoderInputs[t]: decoderInputTrain[t] for t in range(maxDecoderLength)})
    feedDict.update({feedPrevious: False})

    curLoss, _, pred = sess.run([loss, optimizer, decoderPrediction], feed_dict=feedDict)

    if (i % 50 == 0):
        print('Current loss:', curLoss, 'at iteration', i)
        summary = sess.run(merged, feed_dict=feedDict)
        writer.add_summary(summary, i)
    if (i % 25 == 0 and i != 0):
        num = randint(0,len(encoderTestStrings) - 1)
        print(encoderTestStrings[num])
        inputVector = getTestInput(encoderTestStrings[num], wordList, maxEncoderLength);
        feedDict = {encoderInputs[t]: inputVector[t] for t in range(maxEncoderLength)}
        feedDict.update({decoderLabels[t]: zeroVector for t in range(maxDecoderLength)})
        feedDict.update({decoderInputs[t]: zeroVector for t in range(maxDecoderLength)})
        feedDict.update({feedPrevious: True})
        ids = (sess.run(decoderPrediction, feed_dict=feedDict))
        print(idsToSentence(ids, wordList))

    if (i % 10000 == 0 and i != 0):
        model.save_weights("models/pretrained_seq2seq.ckpt")"""