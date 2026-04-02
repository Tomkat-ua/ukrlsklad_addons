from flask import  request,render_template,jsonify #,flash,redirect, url_for
import sys
from . import db
# import config


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
                where m.is_move = 1 
                order by m.num desc
                """
    search = ''
    data = db.data_module(sql,'')
    return render_template('mnakl_list2.html'
                           ,title = 'Накладні на переміщення'
                           ,master_data = data
                           ,search = search
                           )

def get_details(doc_id):
    sql = ("""select
                md.PID as doc_id ,md.TOVAR_ID
                ,md.TOV_NAME     ,md.TOV_CENA
                ,md.TOV_KOLVO    ,md.TOV_ED  ,tn.kod
                from mnakl_ md
                    inner join tovar_name tn on tn.num = md.tovar_id
                where md.pid = ?""")
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