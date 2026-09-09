from flask import Flask, send_from_directory
import os

app = Flask(__name__)

FRONTEND_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend"
)


@app.route("/")
def home():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


if __name__ == "__main__":
    app.run(debug=True)