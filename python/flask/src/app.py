from requests.exceptions import ConnectionError
from services.openAI import OpenAI
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS

# ------------------ SETUP ------------------

load_dotenv()

app = Flask(__name__)

# this will need to be reconfigured before taking the app to production
cors = CORS(app)

# ------------------ EXCEPTION HANDLERS ------------------

# Sends response back to Deep Chat using the Response format:
# https://deepchat.dev/docs/connect/#Response
@app.errorhandler(Exception)
def handle_exception(e):
    print(e)
    return {"error": str(e)}, 500

@app.errorhandler(ConnectionError)
def handle_exception(e):
    print(e)
    return {"error": "Internal service error :( )"}, 500

# ------------------ OPENAI API ------------------

open_ai = OpenAI()

@app.route("/openai-chat", methods=["POST"])
def openai_chat():
    body = request.json
    return open_ai.chat(body)

@app.route("/openai-chat-stream", methods=["POST"])
def openai_chat_stream():
    body = request.json
    return open_ai.chat_stream(body)

@app.route("/openai-image", methods=["POST"])
def openai_image():
    files = request.files.getlist("files")
    return open_ai.image_variation(files)

# ------------------ START SERVER ------------------

if __name__ == "__main__":
    app.run(port=8080)
