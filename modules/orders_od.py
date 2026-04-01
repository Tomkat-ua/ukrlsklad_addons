from flask import render_template, request
from . import db

def orders_list():
    search = ''
    if request.method == 'POST':
        search = request.form.get('search')
        sql = """select * from usadd_web.orders_od where serial like ? """
        data = db.data_module(sql,[search])
    else:
        sql = " select * from usadd_web.orders_od  "
        data = db.data_module(sql,'')
    print(data)
    return render_template('orders_od.html',title = 'Накази ОД',data = data,search = search)