from flask import render_template,request
from . import db

# menu = ['Списання']
title = 'Єдиний акт списання'

def snakl_list():
    # sql_l2 = """   select  ts.tovar_ser_num,sd.tov_name,s.nu,s.date_dok
    #        ,tools.pars_atribute(s.dopoln5,'USER_DOC_DATE') as USER_DOC_DATE
    #        ,sn.name
    #         from tovar_serials ts
    #             inner join snakl_ sd on sd.pid = ts.doc_id and sd.tovar_id = ts.tovar_id
    #             inner join snakl s on s.num = sd.pid
    #             inner join sklad_names sn on sn.num = sd.sklad_id
    #        where ts.doc_type_id = 11 and ts.tovar_ser_num like ? """
    sql_l2 = """select s.num,s.nu,s.date_dok,sd.tov_name,sd.tov_kolvo,sd.tov_cena
                ,tools.pars_atribute(s.dopoln5,'USER_DOC_DATE') as USER_DOC_DATE
                ,sn.name as sklad_name
                ,(select first 1 ts.tovar_ser_num from tovar_serials ts
                    where ts.doc_id = s.num ) as serial
                from snakl  s
                  inner join snakl_ sd on sd.pid = s.num
                  inner join sklad_names sn on sn.num = sd.sklad_id
                where s.num in  (select ts.doc_id from tovar_serials ts
                                where ts.doc_id = s.num and ts.doc_type_id =11
                                and ts.tovar_ser_num like ? )"""

    if request.method == 'GET':
        sql = 'select * from usadd_web.snakl'
        data = db.data_module(sql, '')
        data_l2 = db.data_module(sql_l2, ['%'])
        return render_template('snakl_list.html',title=title,data = data,data2 = data_l2)
    if request.method == 'POST':
        search_str = request.form['search']
        sql = 'select * from usadd_web.snakl where serial like ?'
        data = db.data_module(sql, [search_str])
        data_l2 = db.data_module(sql_l2, [search_str])
        return render_template('snakl_list.html', title=title, data=data,search=search_str,data2 = data_l2)


def snakl_det(id):
    title = 'Списання/Деталі'
    # menu.append('Деталі')

    # sql_h = """ select s.num,s.nu,s.date_dok
    #             ,sn.name as sklad_name from snakl s
    #              inner  join sklad_names sn on sn.num = s.sklad_id
    #             where s.num = ? """
    sql_h = """ select
s.num,s.nu, cast(USER_DOC_DATE as date) as date_dok
,s.sklad_NAME
from usadd_web.snakl  (?) s """
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