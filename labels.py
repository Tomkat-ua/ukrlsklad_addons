import qrcode
from io import BytesIO
import base64
from flask import  render_template


def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # конвертуємо в base64 для вставки в HTML
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def label(sn):
    # Тут можна передати ще інші дані
    item_name = "Назва товару"  # або отримати з БД за SN
    date_str = "2025-08-18"

    qr_img = generate_qr(sn)
    return render_template("label.html", sn=sn, qr_img=qr_img, item_name=item_name, date_str=date_str)