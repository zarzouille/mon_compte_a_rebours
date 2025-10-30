import os
import json
import sys
from datetime import datetime, timedelta
from io import BytesIO
from flask import Flask, send_file, request, render_template, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
from json import JSONDecodeError

# ============================
# Configuration par défaut
# ============================
DEFAULT_CONFIG = {
    "width": 600,
    "height": 200,
    "background_color": "#F5F5F5",
    "text_color": "#222222",
    "font_path": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "font_size": 40,
    "message_prefix": "Temps restant : ",
    "target_date": "2025-12-31T23:59:59",
    "loop_duration": 40
}

CONFIG_PATH = "config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        if not isinstance(cfg, dict):
            raise ValueError
        return {**DEFAULT_CONFIG, **cfg}
    except (FileNotFoundError, JSONDecodeError, ValueError):
        print("⚠️ Erreur config.json, utilisation de la config par défaut.", file=sys.stderr)
        return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

CONFIG = load_config()

# ============================
# App Flask
# ============================
app = Flask(__name__)

@app.route("/")
def home():
    return (
        "<h2>🕒 Countdown Generator</h2>"
        "<p><a href='/settings'>Configurer le design</a></p>"
        "<p><img src='/countdown.gif' alt='Countdown GIF'></p>"
    )

@app.route("/settings", methods=["GET", "POST"])
def settings():
    global CONFIG
    if request.method == "POST":
        CONFIG["target_date"] = request.form.get("target_date", CONFIG["target_date"])
        CONFIG["background_color"] = request.form.get("background_color", CONFIG["background_color"])
        CONFIG["text_color"] = request.form.get("text_color", CONFIG["text_color"])
        CONFIG["font_size"] = int(request.form.get("font_size", CONFIG["font_size"]))
        CONFIG["message_prefix"] = request.form.get("message_prefix", CONFIG["message_prefix"])
        save_config(CONFIG)
        return redirect(url_for("home"))
    return render_template("settings.html", config=CONFIG)

@app.route("/countdown.gif")
def countdown_gif():
    cfg = load_config()
    loop_duration = cfg.get("loop_duration", 40)
    try:
        end_time = datetime.fromisoformat(cfg["target_date"])
    except ValueError:
        return "Date invalide dans config.json", 400

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
            text = f"{cfg['message_prefix']}{days}j {hours:02}:{minutes:02}:{seconds:02}"

        img = Image.new("RGB", (cfg["width"], cfg["height"]), cfg["background_color"])
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(cfg["font_path"], cfg["font_size"])
        except:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (cfg["width"] - text_width) // 2
        y = (cfg["height"] - text_height) // 2
        draw.text((x, y), text, font=font, fill=cfg["text_color"])

        frames.append(img)

    buf = BytesIO()
    frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], loop=0, duration=1000)
    buf.seek(0)
    return send_file(buf, mimetype="image/gif")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
