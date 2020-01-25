import requests

# test serving with curl
# curl -v -L -X POST -H "Content-Type: application/json" -d "{ \"startstring\":\"Juliet:\nWhere\" }" http://localhost:5000/predict

# initialize the Keras REST API endpoint URL along with the input
KERAS_REST_API_URL = "http://localhost:5000/predict"

# load the param/data/file and construct the payload for the request
startstring = "ROMEO:\nThe "
payload = {"startstring": startstring}

# submit the request
# *params form the query string in the URL, *data is used to fill the body of a request (together with *files).
# GET and HEAD requests have no body.
# r = requests.post(KERAS_REST_API_URL, data=payload).json()
r = requests.post(KERAS_REST_API_URL, params=payload)

# ensure the request was successful
# if r["success"]:
#     print(r["response"])

# otherwise, the request failed
# else:
#     print("Request failed")

