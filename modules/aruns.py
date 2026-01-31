from flask import  request,render_template,flash,redirect, url_for
import sys
from . import db
from flask import render_template_string

title = 'Акти пуску'

def aruns_list():
    sql = """select a.num,a.nu
        ,utils.datetostr( a.date_dok) as date_dok
        ,tools.pars_atribute(a.dopoln5,'USER_DOC_DATE') as USER_DOC_DATE
        ,a.cena,sn.name as sklad_name
        ,a.doc_mark_type
        from actvr a
            inner join sklad_names sn on sn.num = a.sklad_id
where a.client_id = 300000174"""
    data = db.data_module(sql,'')
    return render_template("aruns.html",title=title,data=data)