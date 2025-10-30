from flask import Flask, send_file, request
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json

# Charger la configuration
with open("config.json", "r") as f:
    CONFIG = json.load(f)

# Créer l'application Flask
app = Flask(__name__)

@app.route("/")
def home():
    return (
        "<h2>🕒 Countdown Generator</h2>"
        "<p>Utilise ce format d'URL :</p>"
        "<pre>/countdown.gif?to=2025-12-31T23:59:59</pre>"
    )

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

        # Charger la police
        try:
            font = ImageFont.truetype(CONFIG["font_path"], CONFIG["font_size"])
        except:
            font = ImageFont.load_default()

        # Calcul du centrage du texte
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (CONFIG["width"] - text_width) // 2
        y = (CONFIG["height"] - text_height) // 2
        draw.text((x, y), text, fill=CONFIG["text_color"], font=font)
        frames.append(img)

    # Créer le GIF animé (Sendtric-style)
    buf = BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=1000,  # 1 image par seconde
        loop=0
    )
    buf.seek(0)
    return send_file(buf, mimetype="image/gif")

# Configuration Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
