from flask import  request,render_template,jsonify #,flash,redirect, url_for
import sys
from . import db
# import config

title = 'Видача майна'

def mnakl_list():
    tov_code = request.args.get('tov_code')
    tovar_id =  request.args.get('tovar_id')
    function_name = sys._getframe(0).f_code.co_name
    data =''
    sql = """
select m.num,m.nu,m.date_dok
,sn.name as sklad_name
,md.tovar_id
,tn.kod as tov_code
,md.tov_name
,cast(md.tov_kolvo as int ) as tov_kolvo
,md.tov_cena
from mnakl_ md
    inner join mnakl m on m.num = md.pid
    inner join tovar_name tn on tn.num = md.tovar_id
    inner join sklad_names sn on sn.num = md.sklad_id_to
where (tn.kod = ? or ? is null  )
and   (md.tovar_id = ? or ? is null )
order by m.date_dok
                """
    data = db.data_module(sql, [tov_code, tov_code, tovar_id, tovar_id], function_name)
    return  render_template("mnakl_list.html", title='Видача майна',data= data,search='')

def mnakl_list2():
    sql = """ select m.num as doc_id, m.num,m.nu,m.date_dok ,sn_a.name as sklad_a,sn_b.name as sklad_b
                from mnakl m
                  inner join sklad_names sn_a on sn_a.num = m.sklad_id
                  inner join sklad_names sn_b on sn_b.num = m.to_sklad_id
                where m.is_move = 1 and m.nu like ?
                order by m.num desc
                """
    search = ''
    if request.method == 'POST':
        search = request.form.get('search')
        # sql = """ select m.num,m.nu,m.date_dok ,sn_a.name as sklad_a,sn_b.name as sklad_b
        #             from mnakl m
        #               inner join sklad_names sn_a on sn_a.num = m.sklad_id
        #               inner join sklad_names sn_b on sn_b.num = m.to_sklad_id
        #             where m.is_move = 1 and m.num like ?
        #             order by m.num desc
        #             """
        data = db.data_module(sql, [search])
    else:
        # sql = """ select m.num,m.nu,m.date_dok ,sn_a.name as sklad_a,sn_b.name as sklad_b
        #             from mnakl m
        #               inner join sklad_names sn_a on sn_a.num = m.sklad_id
        #               inner join sklad_names sn_b on sn_b.num = m.to_sklad_id
        #             where m.is_move = 1
        #             order by m.num desc
        #             """
        data = db.data_module(sql,['%'])
    return render_template('mnakl_list2.html'
                           ,title = 'Накладні на переміщення'
                           ,master_data = data
                           ,search = search
                           )

def get_details(doc_id):
    sql = "SELECT PID, TOVAR_ID, TOV_NAME, TOV_KOLVO, TOV_ED , TOV_CENA  FROM mnakl_ WHERE pid = ?"
    data = db.data_module(sql, [doc_id])
    return jsonify(data)


def get_serials(doc_id, tovar_id):
    # Тут твій SQL для L3 з ціною
    sql = """
        SELECT distinct 
            ts.tovar_ser_num, utils.get_price_by_serial(ts.tovar_ser_num) as price
        FROM tovar_serials ts
        WHERE ts.doc_type_id = 10 AND ts.doc_id = ? AND ts.tovar_id = ?
    """
    data = db.data_module(sql, [doc_id, tovar_id])
    return jsonify(data)