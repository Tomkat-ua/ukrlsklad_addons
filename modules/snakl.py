from flask import render_template,request
from . import db

# menu = ['Списання']
title = 'Єдиний акт списання'

def snakl_list():
    if request.method == 'GET':
        sql = 'select * from usadd_web.snakl'
        data = db.data_module(sql, '')
        return render_template('snakl_list.html',title=title,data = data)
    if request.method == 'POST':
        search_str = request.form['search']
        sql = 'select * from usadd_web.snakl where serial like ?'
        data = db.data_module(sql, [search_str])
        return render_template('snakl_list.html', title=title, data=data,search=search_str)


def snakl_det(id):
    title = 'Списання/Деталі'
    # menu.append('Деталі')

    sql_h = """ select s.num,s.nu,s.date_dok
                ,sn.name as sklad_name from snakl s
                 inner  join sklad_names sn on sn.num = s.sklad_id
                where s.num = ? """
    data_h = db.data_module(sql_h, [id])
    sql = """select sd.tovar_id
            ,sd.tov_name
            ,cast( sd.tov_kolvo as int ) as tov_kolvo
            ,sd.tov_cena
            ,ts.tovar_ser_num as serial
             from snakl_ sd
                left join tovar_serials ts on ts.doc_id = sd.pid
                    and ts.tovar_id = sd.tovar_id and ts.doc_type_id = 11
            where sd.pid = ?
 """
    data = db.data_module(sql, [id])
    total = 0
    for row in data:
        total=total + row['TOV_KOLVO'] * row['TOV_CENA']
    return render_template('snakl_det.html',title=title,data_h=data_h,data = data,total=total)