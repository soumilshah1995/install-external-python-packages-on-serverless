from flask import Flask, request
import json
import base64

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def hello_world():
    try:
        data = json.loads(request.data)
        for item in data.get("records"):
            data = json.loads(base64.b64decode(item.get("data")))
            print(data)
    except Exception as e:pass

    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run(debug=True)