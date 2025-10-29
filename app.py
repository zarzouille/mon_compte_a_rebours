from flask import Flask, request, send_file
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json, os

app = Flask(__name__)

# Charger la configuration depuis le fichier JSON
with open("config.json", "r") as f:
    CONFIG = json.load(f)

@app.route("/countdown.png")
def countdown():
    try:
        end_str = request.args.get("to")
        end_time = datetime.fromisoformat(end_str)
        now = datetime.utcnow()
        delta = end_time - now

        if delta.total_seconds() < 0:
            text = "⏰ Terminé !"
        else:
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            text = f"{CONFIG['message_prefix']}{days}j {hours:02}:{minutes:02}:{seconds:02}"

        # Créer l’image
        img = Image.new("RGB", (CONFIG["width"], CONFIG["height"]), CONFIG["background_color"])
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(CONFIG["font_path"], CONFIG["font_size"])
        except:
            font = ImageFont.load_default()

        draw.text(tuple(CONFIG["position"]), text, fill=CONFIG["text_color"], font=font)

    except Exception as e:
        # En cas d’erreur, afficher un message rouge
        img = Image.new("RGB", (CONFIG["width"], CONFIG["height"]), CONFIG["background_color"])
        draw = ImageDraw.Draw(img)
        draw.text((20, 25), f"Erreur: {str(e)}", fill=CONFIG["error_color"])

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
