from __future__ import absolute_import, division, print_function
import tensorflow as tf
import numpy as np

tf.enable_eager_execution()

"""
Definitions
"""

path_to_file = tf.keras.utils.get_file('shakespeare.txt',
'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')


# Read, then decode for py2 compat.
text = open(path_to_file, 'rb').read().decode(encoding='utf-8')

# The unique characters in the file
vocab = sorted(set(text))

char2idx = {u:i for i, u in enumerate(vocab)}

idx2char = np.array(vocab)

"""
Generate text
"""

# Recreate the exact same model, including weights and optimizer.
new_model = tf.keras.models.load_model('./model/my_model.h5')
new_model.summary()

# saved_model method
# new_model = tf.contrib.saved_model.load_keras_model(b'./saved_models\\1552141268')
# new_model.summary()

"""
The prediction loop
"""
# The following code block generates the text:
# It Starts by choosing a start string, initializing the RNN state and setting the number of characters to generate.
# Get the prediction distribution of the next character using the start string and the RNN state.
# Then, use a multinomial distribution to calculate the index of the predicted character.
# Use this predicted character as our next input to the model.
# The RNN state returned by the model is fed back into the model so that it now has more context,
# instead than only one word.
# After predicting the next word, the modified RNN states are again fed back into the model,
# which is how it learns as it gets more context from the previously predicted words.
# Looking at the generated text, you'll see the model knows when to capitalize, make paragraphs,
# and imitates a Shakespeare-like writing vocabulary. With the small number of training epochs,
# it has not yet learned to form coherent sentences.
# The easiest thing you can do to improve the results it to train it for longer (try EPOCHS=30).
# You can also experiment with a different start string, or try adding another RNN layer to
# improve the model's accuracy, or adjusting the temperature parameter to generate more or less random predictions.


def generate_text(model, start_string):
    # Evaluation step (generating text using the learned model)

    # Number of characters to generate
    num_generate = 1000

    # Converting our start string to numbers (vectorizing)
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)

    # Empty string to store our results
    text_generated = []

    # Low temperatures results in more predictable text.
    # Higher temperatures results in more surprising text.
    # Experiment to find the best setting.
    temperature = 1.0

    # Here batch size == 1
    model.reset_states()
    for i in range(num_generate):
        predictions = model(input_eval)
        # remove the batch dimension
        predictions = tf.squeeze(predictions, 0)

        # using a multinomial distribution to predict the word returned by the model
        predictions = predictions / temperature
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1, 0].numpy()

        # We pass the predicted word as the next input to the model
        # along with the previous hidden state
        input_eval = tf.expand_dims([predicted_id], 0)

        text_generated.append(idx2char[predicted_id])

    return start_string + ''.join(text_generated)

# print(generate_text(new_model, start_string=u"ROMEO:\nThe "))
