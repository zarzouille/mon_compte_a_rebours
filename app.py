from flask import Flask, send_file, request
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json, sys
from json import JSONDecodeError

# ============================
# Charger la configuration
# ============================
DEFAULT_CONFIG = {
    "width": 400,
    "height": 100,
    "background_color": "#F5F5F5",
    "text_color": "#222222",
    "font_path": "arial.ttf",
    "font_size": 70,
    "message_prefix": "Temps restant : ",
    "target_date": "2025-12-31T23:59:59",
    "loop_duration": 30
}

try:
    with open("config.json", "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
    if not isinstance(CONFIG, dict):
        raise ValueError("config.json doit contenir un objet JSON valide.")
except (FileNotFoundError, JSONDecodeError, ValueError) as e:
    print("⚠️  Erreur lors du chargement de config.json :", e, file=sys.stderr)
    print("➡️  Utilisation de la configuration par défaut.", file=sys.stderr)
    CONFIG = DEFAULT_CONFIG.copy()

# ============================
# Créer l'application Flask
# ============================
app = Flask(__name__)

@app.route("/")
def home():
    return (
        "<h2>🕒 Countdown Generator</h2>"
        "<p>Utilise ce format d'URL :</p>"
        "<pre>/countdown.gif?to=2025-12-31T23:59:59</pre>"
    )

# ============================
# Génération du GIF
# ============================
@app.route("/countdown.gif")
def countdown_gif():
    loop_duration = CONFIG.get("loop_duration", 20)
    end_str = request.args.get("to", CONFIG.get("target_date"))
    end_time = datetime.fromisoformat(end_str)
    now = datetime.utcnow()

    frames = []

    for i in range(loop_duration):
        current_time = now + timedelta(seconds=i)
        remaining = int((end_time - current_time).total_seconds())

        if remaining <= 0:
            text = "⏰ Terminé !"
        else:
            days, rem = divmod(remaining, 86400)
            hours, rem = divmod(rem, 3600)
            minutes, seconds = divmod(rem, 60)
            text = f"{CONFIG['message_prefix']}{days}j {hours:02}:{minutes:02}:{seconds:02}"

        img = Image.new("RGB", (CONFIG["width"], CONFIG["height"]), CONFIG["background_color"])
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(CONFIG["font_path"], CONFIG["font_size"])
        except:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
