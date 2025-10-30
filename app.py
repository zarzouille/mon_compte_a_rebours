@app.route("/countdown.gif")
def countdown_gif():
    loop_duration = 20  # secondes d’animation
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
        text_height = text_bbox[3] - text_bbox[1]
        x = (CONFIG["width"] - text_width) // 2
        y = (CONFIG["height"] - text_height) // 2
        draw.text((x, y), text, fill=CONFIG["text_color"], font=font)
        frames.append(img)

    buf = BytesIO()
    frames[0].save(
        buf, format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=1000,  # 1 image par seconde
        loop=0
    )
    buf.seek(0)
    return send_file(buf, mimetype="image/gif")
