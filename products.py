from flask import  request,render_template,flash,send_file,current_app,send_from_directory,jsonify
import db,os,io,fdb
from dispack import title

title = 'Каталог продукції'

def products_tab():
    sql = 'select   * from usadd_web.products_list'
    data = db.data_module(sql,'')

    return render_template ('products_tab.html',products = data,title=title)

def products_img(tovar_id):
    sql = '   select i.tov_image as  IMAGE_BLOB, i.tov_image_type as  IMAGE_MIMETYPE from tovar_images i where i.tovar_id  =?'
    try:
        con = db.get_connection()
        cur = con.cursor()
        cur.execute(sql,[tovar_id])
        data = cur.fetchone()


        if not data or data[0] is None:
            static_dir = os.path.join(current_app.root_path, 'static', 'images')
            return send_from_directory(static_dir, 'placeholder.png')
            # Повернути заглушку, якщо немає зображення
            # return current_app.send_static_file('static/images/placeholder.png')

        image_data, mimetype = data
        mimetype = f'image/{mimetype}'
        # print(type(image_blob_reader))
        # 3. Використання send_file
        image_io = io.BytesIO(image_data)

        return send_file(image_io, mimetype=mimetype, as_attachment=False, max_age=86400 )

    except Exception as e:
        current_app.logger.error(f"Error fetching image: {e}")
        return current_app.send_static_file('static/images/placeholder.png'), 500

    finally:
        if con:
            con.close()


def upload_image(tovar_id):
    try:
        file = request.files.get('image')
        if not file:
            return jsonify(success=False, error="Файл не отримано")

        # Читаємо файл у бінарний режим (це дає нам тип bytes)
        img_data = file.read()

        # Визначаємо тип для поля IMG_TYPE
        filename = file.filename.lower()
        ext = 'webp'
        if filename.endswith('.jpg') or filename.endswith('.jpeg'):
            ext = 'jpg'
        elif filename.endswith('.png'):
            ext = 'png'

        conn = db.get_connection()
        cur = conn.cursor()
        print('img_data',type(img_data))
        print('ext',ext)
        print('tovar_id',tovar_id)
        # Передаємо img_data (bytes) як є. fdb сам зробить все інше.
        cur.execute("""  UPDATE OR INSERT INTO TOVAR_IMAGES (TOVAR_ID, TOV_IMAGE, TOV_IMAGE_TYPE,ISORT, DOC_TYPE)
                            VALUES (?, ?, ?,0, 102)
                            MATCHING (TOVAR_ID)   """
                    , [tovar_id, img_data, ext])

        conn.commit()
        return jsonify(success=True)

    except Exception as e:
        print(f"Помилка бази: {e}")
        return jsonify(success=False, error=str(e))


def delete_image(tovar_id):
    conn = db.get_connection()
    cur = conn.cursor()
    # Очищуємо поле
    cur.execute("""  UPDATE TOVAR_IMAGES SET   TOV_IMAGE_TYPE = null, TOV_IMAGE = null WHERE NUM = ?  """,[tovar_id])

    conn.commit()
    return jsonify(success=True)