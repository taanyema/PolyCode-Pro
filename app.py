from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")  # sert ton HTML

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Réponse simple pour tester
    bot_reply = f"Bot a reçu : {user_message}"

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)  # Replit aime le port 3000 
from flask import Flask, request, jsonify
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/image", methods=["POST"])
def image():
    image = request.files.get("image")

    if not image:
        return jsonify({"reply": "Aucune image reçue ❌"})

    path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(path)

    return jsonify({"reply": "Image reçue avec succès ✅"})