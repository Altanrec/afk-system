from flask import Flask, render_template, request, jsonify
from bot_manager import BotManager
import os
import uuid

app = Flask(__name__)
manager = BotManager()

@app.route("/")
def index():
    return render_template("index.html")

# UptimeRobot için ping endpoint
@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/api/bots", methods=["GET"])
def list_bots():
    return jsonify(manager.get_all())

@app.route("/api/bots", methods=["POST"])
def add_bot():
    data = request.json or {}
    token = data.get("token", "").strip()
    guild_id = data.get("guild_id", "").strip()
    channel_id = data.get("channel_id", "").strip()

    if not all([token, guild_id, channel_id]):
        return jsonify({"error": "Tüm alanlar gerekli"}), 400

    if not guild_id.isdigit() or not channel_id.isdigit():
        return jsonify({"error": "Sunucu ve kanal ID sayı olmalı"}), 400

    bot_id = str(uuid.uuid4())[:8]
    manager.add_bot(bot_id, token, guild_id, channel_id)
    return jsonify({"id": bot_id, "message": "Bot başlatıldı"})

@app.route("/api/bots/<bot_id>", methods=["DELETE"])
def remove_bot(bot_id):
    if manager.remove_bot(bot_id):
        return jsonify({"message": "Bot durduruldu"})
    return jsonify({"error": "Bot bulunamadı"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)