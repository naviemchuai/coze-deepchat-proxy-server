from flask import Response
import requests
import json
import os

# Make sure to set the OPENAI_API_KEY environment variable in a .env file (create if does not exist) - see .env.example

class OpenAI:
    @staticmethod
    def create_chat_body(body, botID, stream=False):
        # Text messages are stored inside request body using the Deep Chat JSON format:
        # https://deepchat.dev/docs/connect
        chat_body = {
            "chat_history": [
                {
                    "role": "assistant" if message["role"] == "ai" else message["role"],
                    "content": message["text"],
                    "content_type": "text",
                    **({"type": "answer"} if message["role"] == "ai" else {})
                } for message in body["messages"][:-1]  # Exclude the last element
            ],
            #"conversation_id": "demo-0",
            "bot_id": botID,
            "user": "demo-user",
            "query": body["messages"][-1]["text"] if body["messages"] else ""  # Use the last element as the query
        }
        if stream:
            chat_body["stream"] = True
        return chat_body

    def chat(self, body, botID):
        headers = {
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY"),
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "api.coze.com",
            "Connection": "keep-alive"

        }
        chat_body = self.create_chat_body(body, botID)
        print("chat_body", chat_body)
        response = requests.post(
            "https://api.coze.com/open_api/v2/chat", json=chat_body, headers=headers)
        json_response = response.json()
        if "error" in json_response:
            raise Exception(json_response["error"]["message"])
        messages = json_response["messages"]
        for message in messages:
            if message["type"] == "answer":
                result = message["content"]
                break
        print(json_response)
        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response
        return {"text": result}

    def chat_stream(self, body):
        headers = {
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY"),
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "api.coze.com",
            "Connection": "keep-alive"
        }
        chat_body = self.create_chat_body(body, stream=True)
        print("headers", headers)
        print("chat_body", chat_body)
        response = requests.post(
            "https://api.coze.com/open_api/v2/chat", json=chat_body, headers=headers, stream=True)

        def generate():
            # increase chunk size if getting errors for long messages
            for chunk in response.iter_content(chunk_size=2048):
                if chunk:
                    if not(chunk.decode().strip().startswith("data")):
                        errorMessage = json.loads(chunk.decode())["error"]["message"]
                        print("Error in the retrieved stream chunk:", errorMessage)
                        # this exception is not caught, however it signals to the user that there was an error
                        raise Exception(errorMessage)
                    lines = chunk.decode().split("\n")
                    filtered_lines = list(
                        filter(lambda line: line.strip(), lines))
                    for line in filtered_lines:
                        data = line.replace("data:", "").replace(
                            "[DONE]", "").replace("data: [DONE]", "").strip()
                        if data:
                            try:
                                result = ""
                                for line in response.iter_lines():
                                    if not line:
                                        break
                                    line = line.decode('utf-8')
                                    if line.startswith("data:"):
                                        data = json.loads(line[5:])
                                        message = data.get("message", {})
                                        if message.get("type") == "answer" and not data.get("is_finish", False):
                                            result += message.get("content", "")
                                yield "data: {}\n\n".format(json.dumps({"text": result}))
                            except json.JSONDecodeError:
                                # Incomplete JSON string, continue accumulating lines
                                pass
        return Response(generate(), mimetype="text/event-stream")

    # By default - the OpenAI API will accept 1024x1024 png images, however other dimensions/formats can sometimes work by default
    # You can use an example image here: https://github.com/OvidijusParsiunas/deep-chat/blob/main/example-servers/ui/assets/example-image.png
    def image_variation(self, files):
        url = "https://api.coze.com/open_api/v2/chat"
        headers = {
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY"),
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "api.coze.com",
            "Connection": "keep-alive"
        }
        # Files are stored inside a files object
        # https://deepchat.dev/docs/connect
        image_file = files[0]
        form = {
            "image": (image_file.filename, image_file.read(), image_file.mimetype)
        }
        response = requests.post(url, files=form, headers=headers)
        json_response = response.json()
        if "error" in json_response:
            raise Exception(json_response["error"]["message"])
        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response
        return {"files": [{"type": "image", "src": json_response["data"][0]["url"]}]}
