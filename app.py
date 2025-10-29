from flask import Flask, request, send_file
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json, os

app = Flask(__name__)

# Charger la configuration
with open("config.json", "r") as f:
    CONFIG = json.load(f)

@app.route("/countdown.png")
def countdown():
    try:
        # Récupérer la date cible (depuis URL ou config)
        end_str = request.args.get("to", CONFIG.get("target_date"))
        end_time = datetime.fromisoformat(end_str)
        now = datetime.utcnow()
        
        # Calcul complet des secondes restantes
        remaining = int((end_time - now).total_seconds())
        
        if remaining <= 0:
            text = "⏰ Terminé !"
        else:
        days, remainder = divmod(remaining, 86400)  # 86400 secondes dans un jour
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        text = f"{CONFIG['message_prefix']}{days}j {hours:02}:{minutes:02}:{seconds:02}"


        # Créer l’image
        img = Image.new("RGB", (CONFIG["width"], CONFIG["height"]), CONFIG["background_color"])
        draw = ImageDraw.Draw(img)

        # Charger la police
        try:
            font = ImageFont.truetype(CONFIG["font_path"], CONFIG["font_size"])
        except:
            font = ImageFont.load_default()

        # Calculer la taille du texte
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calcul horizontal (text_align)
        if CONFIG.get("text_align", "left") == "center":
            x = (CONFIG["width"] - text_width) // 2
        elif CONFIG["text_align"] == "right":
            x = CONFIG["width"] - text_width - 10
        else:  # left
            x = 10

        # Calcul vertical (vertical_align)
        if CONFIG.get("vertical_align", "top") == "middle":
            y = (CONFIG["height"] - text_height) // 2
        elif CONFIG["vertical_align"] == "bottom":
            y = CONFIG["height"] - text_height - 10
        else:  # top
            y = 10

        # Dessiner le texte
        draw.text((x, y), text, fill=CONFIG["text_color"], font=font)

    except Exception as e:
        img = Image.new("RGB", (CONFIG["width"], CONFIG["height"]), CONFIG["background_color"])
        draw = ImageDraw.Draw(img)
        draw.text((10, 40), f"Erreur: {e}", fill="#FF0000")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
