from flask import  request,render_template,flash
from  . import db

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
    param = [p if p != '' else None for p in param]
    data = db.data_module(sql, param)
    return data

def index():
    ######### LIST #######################
    if request.method == "POST":
        tov_serial = request.form['tov_serial']
        tov_name   = request.form['tov_name']

        data = data_for_module([tov_serial,tov_name],'list')
        print(data)
        if data:
            return render_template('ghist_.html', title=title,
                                   rows = data,
                                   search_value=tov_serial.strip(),
                                   tov_name=tov_name,
                                   )
        else:
            # 🛑 Невдача: НЕ робимо redirect, а відображаємо помилку на тій же сторінці
            flash("Запис не знайдено!", "danger")

            # 🌟 Повторно відображаємо шаблон, але передаємо введене значення!

            return render_template('ghist_.html',
                                   title=title,
                                   search_value=tov_serial,  # ⬅️ ЗНАЧЕННЯ ЗБЕРЕЖЕНО
                                   tov_name = tov_name,
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
    return render_template('ghist_det.html',title=title,rows = data_movies,row=data_header[0] )


