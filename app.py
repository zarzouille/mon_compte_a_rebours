from flask import Flask, request, send_file
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

@app.route("/countdown.png")
def countdown():
    end_str = request.args.get("to")
    end_time = datetime.fromisoformat(end_str)
    now = datetime.utcnow()
    delta = end_time - now

    days, seconds = delta.days, delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    text = f"{days}j {hours:02}:{minutes:02}:{seconds:02}"

    img = Image.new("RGB", (350, 80), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((20, 25), text, fill=(0, 0, 0))

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)