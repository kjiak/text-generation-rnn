from __future__ import absolute_import, division, print_function
import tensorflow as tf
import numpy as np
import os
import time

tf.enable_eager_execution()

path_to_file = tf.keras.utils.get_file('shakespeare.txt',
'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')

""" 
Download data 
"""

# Read, then decode for py2 compat.
text = open(path_to_file, 'rb').read().decode(encoding='utf-8')
# length of text is the number of characters in it
print('Length of text: {} characters'.format(len(text)))
# Take a look at the first 250 characters in text
print(text[:250])
# The unique characters in the file
vocab = sorted(set(text))
print('{} unique characters'.format(len(vocab)))

""" 
Vectorize the text 
"""
# Before training, we need to map strings to a numerical representation.
# Create two lookup tables: one mapping characters to numbers, and another for numbers to characters.

# Creating a mapping from unique characters to indices
char2idx = {u:i for i, u in enumerate(vocab)}
idx2char = np.array(vocab)

text_as_int = np.array([char2idx[c] for c in text])

print('{')
for char,_ in zip(char2idx, range(20)):
    print('  {:4s}: {:3d},'.format(repr(char), char2idx[char]))
print('  ...\n}')

# Show how the first 13 characters from the text are mapped to integers
print ('{} ---- characters mapped to int ---- > {}'.format(repr(text[:13]), text_as_int[:13]))

""" 
The prediction task
"""
# Given a character, or a sequence of characters, what is the most probable next character?
# This is the task we're training the model to perform.
# The input to the model will be a sequence of characters,
# and we train the model to predict the output—the following character at each time step.

# Since RNNs maintain an internal state that depends on the previously seen elements,
# given all the characters computed until this moment, what is the next character?


# Next divide the text into example sequences. Each input sequence will contain seq_length characters from the text.
# For each input sequence, the corresponding targets contain the same length of text,
# except shifted one character to the right.
# So break the text into chunks of seq_length+1.

# The maximum length sentence we want for a single input in characters
seq_length = 100
examples_per_epoch = len(text)//seq_length

# Create training examples / targets
char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)

for i in char_dataset.take(5):
  print(idx2char[i.numpy()])

# The batch method lets us easily convert these individual characters to sequences of the desired size.
sequences = char_dataset.batch(seq_length+1, drop_remainder=True)


for item in sequences.take(5):
  print(repr(''.join(idx2char[item.numpy()])))

# For each sequence, duplicate and shift it to form the input and target text by using the map method
# to apply a simple function to each batch:


def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text


dataset = sequences.map(split_input_target)


for input_example, target_example in  dataset.take(1):
  print ('Input data: ', repr(''.join(idx2char[input_example.numpy()])))
  print ('Target data:', repr(''.join(idx2char[target_example.numpy()])))

# Each index of these vectors are processed as one time step.
# For the input at time step 0, the model receives the index for "F" and trys to predict the index for "i"
# as the next character. At the next timestep, it does the same thing but the RNN considers the previous step context
# in addition to the current input character.

for i, (input_idx, target_idx) in enumerate(zip(input_example[:5], target_example[:5])):
    print("Step {:4d}".format(i))
    print("  input: {} ({:s})".format(input_idx, repr(idx2char[input_idx])))
    print("  expected output: {} ({:s})".format(target_idx, repr(idx2char[target_idx])))

# We used tf.data to split the text into manageable sequences.
# But before feeding this data into the model, we need to shuffle the data and pack it into batches

# Batch size
BATCH_SIZE = 64
steps_per_epoch = examples_per_epoch//BATCH_SIZE

# Buffer size to shuffle the dataset
# (TF data is designed to work with possibly infinite sequences,
# so it doesn't attempt to shuffle the entire sequence in memory. Instead,
# it maintains a buffer in which it shuffles elements).
BUFFER_SIZE = 10000

dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

"""
Build the Model
"""

# Use tf.keras.Sequential to define the model. For this simple example three layers are used to define our model:
# tf.keras.layers.Embedding: The input layer. A trainable lookup table that will map the numbers of each character
# to a vector with embedding_dim dimensions;
# tf.keras.layers.GRU: A type of RNN with size units=rnn_units (You can also use a LSTM layer here.)
# tf.keras.layers.Dense: The output layer, with vocab_size outputs.

# Length of the vocabulary in chars
vocab_size = len(vocab)

# The embedding dimension
embedding_dim = 256

# Number of RNN units
rnn_units = 1024


# for GPU
# if tf.test.is_gpu_available():
# rnn = tf.keras.layers.CuDNNGRU
# else:
import functools
rnn = functools.partial(
tf.keras.layers.GRU, recurrent_activation='sigmoid')


def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
  model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim,
                              batch_input_shape=[batch_size, None]),
    rnn(rnn_units,
        return_sequences=True,
        recurrent_initializer='glorot_uniform',
        stateful=True),
    tf.keras.layers.Dense(vocab_size)
  ])
  return model


model = build_model(
  vocab_size = len(vocab),
  embedding_dim=embedding_dim,
  rnn_units=rnn_units,
  batch_size=BATCH_SIZE)

# For each character the model looks up the embedding, runs the GRU one timestep with the embedding as input,
# and applies the dense layer to generate logits predicting the log-liklihood of the next character.

"""
Try the Model
"""

# First check the shape of the output:
for input_example_batch, target_example_batch in dataset.take(1):
    example_batch_predictions = model(input_example_batch)
    print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")

model.summary()

# To get actual predictions from the model we need to sample from the output distribution,
# to get actual character indices. This distribution is defined by the logits over the character vocabulary.

# Try it for the first example in the batch:
# Decode these to see the text predicted by this untrained model

sampled_indices = tf.random.categorical(example_batch_predictions[0], num_samples=1)
sampled_indices = tf.squeeze(sampled_indices,axis=-1).numpy()

print("Input: \n", repr("".join(idx2char[input_example_batch[0]])))
print()
print("Next Char Predictions: \n", repr("".join(idx2char[sampled_indices])))

"""
Train the Model
"""
# At this point the problem can be treated as a standard classification problem. Given the previous RNN state,
# and the input this time step, predict the class of the next character.

# Attach an optimizer, and a loss function
# The standard tf.keras.losses.sparse_softmax_crossentropy loss function works in this case because
# it is applied across the last dimension of the predictions.
# Because our model returns logits, we need to set the from_logits flag.


def loss(labels, logits):
  return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)


example_batch_loss  = loss(target_example_batch, example_batch_predictions)
print("Prediction shape: ", example_batch_predictions.shape, " # (batch_size, sequence_length, vocab_size)")
print("scalar_loss:      ", example_batch_loss.numpy().mean())

model.compile(
    optimizer = tf.train.AdamOptimizer(),
    loss = loss)

# Configure checkpoints
# Use a tf.keras.callbacks.ModelCheckpoint to ensure that checkpoints are saved during training

# Directory where the checkpoints will be saved
checkpoint_dir = './training_checkpoints'
# Name of the checkpoint files
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True)

# Execute the training
# To keep training time reasonable, use 3 epochs to train the model.
# In Colab, set the runtime to GPU for faster training.

EPOCHS=3
history = model.fit(dataset.repeat(), epochs=EPOCHS, steps_per_epoch=steps_per_epoch, callbacks=[checkpoint_callback])

# Restore the latest checkpoint
# To keep this prediction step simple, use a batch size of 1.
# Because of the way the RNN state is passed from timestep to timestep,
# the model only accepts a fixed batch size once built.
# To run the model with a different batch_size, we need to rebuild the model
# and restore the weights from the checkpoint.

tf.train.latest_checkpoint(checkpoint_dir)
model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)
model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
model.build(tf.TensorShape([1, None]))
model.summary()

# save entire model (keras format)
# You can save a model built with the Functional API into a single file.
# You can later recreate the same model from this file,
# even if you no longer have access to the code that created the model.

# This file includes:
# 1. The model's architecture
# 2. The model's weight values (which were learned during training)
# 3. The model's training config (what you passed to compile), if any
# 4. The optimizer and its state, if any(this enables you to restart training where you left off)

model.save('./model/my_model.h5')

# saved_model method (tensorflow format)
# You can also export a whole model to the TensorFlow SavedModel format.
# SavedModel is a standalone serialization format for Tensorflow objects,
# supported by TensorFlow serving as well as TensorFlow implementations other than Python.

# saved_model_path = tf.contrib.saved_model.save_keras_model(model, "./saved_models")
