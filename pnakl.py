from flask import  request,render_template,flash,redirect, url_for
import sys,db
import config

title = 'Приход майна'

def pnakl_list():
    function_name = sys._getframe(0).f_code.co_name
    data =''
    if request.method == 'GET':
        search = ''
    else:
        search = request.form.get('search')
        sql = """ select p.nu,p.date_dok,p.client ,p.p_nu
                    ,utils.datetostr( p.p_date_dok)  as p_date_dok
                    ,pd.pid, pd.tov_name
                    ,cast ( pd.tov_kolvo as int) as tov_kolvo
                    ,pd.tov_cena 
                    ,tn.kod as tov_code
                    from pnakl_ pd
                        inner join pnakl p on p.num = pd.pid
                        inner join tovar_name tn on tn.num = pd.tovar_id
                    where pd.tov_name like ?
                    order by p.date_dok
                    """
        data = db.data_module(sql,[search],function_name)
    return  render_template("pnakl_list.html", title='Приход майна',data= data,search=search)