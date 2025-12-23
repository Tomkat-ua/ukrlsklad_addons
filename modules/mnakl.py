from flask import  request,render_template#,flash,redirect, url_for
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