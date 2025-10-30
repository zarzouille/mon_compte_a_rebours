import os
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
    "width": 600,
    "height": 200,
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
    loop_duration = CONFIG.get("loop_duration", 30)
    # 🗓️ Utiliser la date du config.json par défaut
    end_str = CONFIG.get("target_date", "2025-12-31T23:59:59")
    try:
        end_time = datetime.fromisoformat(end_str)
    except ValueError:
        return "Date invalide. Format attendu : YYYY-MM-DDTHH:MM:SS", 400

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
            # ⚙️ Si la police n’existe pas, on crée une police par défaut avec une taille proche
            print("⚠️ Police non trouvée, utilisation de la police par défaut.", file=sys.stderr)
            font = ImageFont.load_default()
            # Astuce : créer une police bitmap "étirée" pour simuler la taille voulue
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", CONFIG["font_size"])

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (CONFIG["width"] - text_width) // 2
        y = (CONFIG["height"] - text_height) // 2
        draw.text((x, y), text, font=font, fill=CONFIG["text_color"])

        frames.append(img)

    # Créer le GIF en mémoire
    buf = BytesIO()
    frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], loop=0, duration=1000)
    buf.seek(0)
    return send_file(buf, mimetype="image/gif")

# ============================
# Lancer l'application (local)
# ============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
