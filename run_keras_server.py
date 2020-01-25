import prediction
import numpy as np
import tensorflow as tf
import flask
import io

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)
model = None


def load_model():
    # load the pre-trained Keras model (here we are using a model
    # pre-trained on ImageNet and provided by Keras, but you can
    # substitute in your own networks just as easily)
    global model
    model = tf.keras.models.load_model('./model/my_model.h5')
    model.summary()


@app.route("/predict", methods=["GET","POST"])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}

    # ensure an image was properly uploaded to our endpoint
    # if flask.request.method == "POST":
    #     # if flask.request.data.get("startstring"):
    #     if flask.request.data:
    #         startstring = flask.request.data["startstring"].read()
    #         results = generate_text(model, startstring)
    #         data["predictions"] = results
    #         # indicate that the request was a success
    #         data["success"] = True

    # get the request parameters
    params = flask.request.json
    if (params == None):
        params = flask.request.args

    # if parameters are found, echo the specific parameter
    if (params != None):
        data["response"] = prediction.generate_text(model, params.get("startstring"))
        data["success"] = True
    # return the data dictionary as a JSON response
    return flask.jsonify(data)


# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
           "please wait until server has fully started"))
    load_model()
    app.run()


