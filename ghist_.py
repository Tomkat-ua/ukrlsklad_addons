from flask import  request,render_template,flash,redirect,url_for
import db
import pandas as pd

title = 'Інформація по номеру'

def fetch_named(cursor):
    """Генерує записи як словники з іменами полів."""
    columns = [desc[0].lower() for desc in cursor.description]  # або без .lower()
    for row in cursor:
        yield dict(zip(columns, row))

def data_for_module(param,mod):
    if mod == 'list':
        sql = "select * from usadd_web.ghist_list (?,?) "
    elif mod == 'header':
        sql = "select * from usadd_web.GHIST_DET_HEADER (?)"
    elif mod == 'movies':
        sql = "select * from usadd_web.ghist_det_movies (?)"
    else:
        sql = '*'
    print('mod=',mod,'sql=',sql)
    con = db.get_connection()
    cur = con.cursor()
    param = [p if p != '' else None for p in param]
    print(param)
    cur.execute(sql, param)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)
    df_display = df.fillna('')
    data = df_display.to_dict(orient='records')
    con.close()
    return data

def index():
    ######### LIST #######################
    if request.method == "POST":
        # search_str = request.form.get('tov_serial')
        tov_serial = request.form['tov_serial']
        tov_name   = request.form['tov_name']
        print('tov_serial=',tov_serial)
        print('tov_name=', tov_name)
        # data = data_for_list(search_str)
        data = data_for_module([tov_serial,tov_name],'list')
        if data:
            return render_template('ghist_.html', title=title,rows = data,search_value=tov_serial.strip())
        # else:
        #     flash("Запис не знайдено!", "danger")  # повідомлення + категорія (danger, success...)
        #     return redirect(url_for("ghist"))
        else:
            # 🛑 Невдача: НЕ робимо redirect, а відображаємо помилку на тій же сторінці
            flash("Запис не знайдено!", "danger")

            # 🌟 Повторно відображаємо шаблон, але передаємо введене значення!
            return render_template('ghist_.html',
                                   title=title,
                                   search_value=tov_serial,  # ⬅️ ЗНАЧЕННЯ ЗБЕРЕЖЕНО
                                   rows=[])  # Переконайтесь, що rows порожній
    return render_template('ghist_.html',title=title)

######## DETAILS ######################################
def datails(search_str):
    print('search_str',search_str)
    search_str = int(search_str)

##### movies #########
    data_movies = data_for_module([search_str],'movies')
##### details ########
    data_header = data_for_module([search_str],'header')
    # print(data_header[0])
    # con.close()
    return render_template('ghist_det.html',title=title,rows = data_movies,row=data_header[0] )
    # print(f"details {row_id}")

