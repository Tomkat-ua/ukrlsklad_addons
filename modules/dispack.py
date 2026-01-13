from flask import  request,render_template,flash,redirect, url_for
import sys
from . import db

title = 'Розкомплектація'

def dispack_list():
    function_name = sys._getframe(0).f_code.co_name
    sql = ' select  * from usadd_web.DISPACK_LIST (?,?,?) order by num desc '
    try:
        data = db.data_module(sql, [0, None, None], function_name)
        if request.method == "GET":
            return  render_template("dispack_list.html", title = 'Розкомплектація',data = data)
        if request.method == "POST":
            serial = request.form['search']
            data = db.data_module(sql, [2, None, serial], function_name)
            return render_template("dispack_list.html", title='Розкомплектація', data=data,search = serial)
    except Exception as e:
        flash(f"❌ {str(e)}", "danger")
        flash(f"❗️ {sql}", "warning")
        return render_template("dispack_list.html", title='Розкомплектація')

def doc(doc_id,dt):
    function_name = sys._getframe(0).f_code.co_name
    znakl_l_id = 0
    # COMMON HEAD
    sql_h = """ select  *    from usadd_web.DISPACK_LIST (?,?,?)"""
    data_h = db.data_module(sql_h, [1, doc_id, None], function_name + '_header')
    # print(data_h)
    #ACT VR
    if dt == 1:
        sql_d = 'select * from usadd_web.dispack_doc_d(?)'
        data_d = db.data_module(sql_d, [doc_id], function_name + ' _dt=1')
        return render_template("dispack_doc1.html", title=title, dt=dt, data_h=data_h[0]
                               , data_d=data_d,znakl_l_id=znakl_l_id
                               ,docname = 'Акт Виконаних Робіт')

    #INS ZNAKL
    if dt == 2:
        # LEFT SIDE
        sql_dl = 'select * from usadd_web.dispack_doc_dl(?)'
        data_dl = db.data_module(sql_dl, [doc_id], function_name + '_dt=2 _dl')
        total_l = 0
        if data_dl:
            znakl_l_id = data_dl[0]['NUM']
        print('znakl_l_id:',znakl_l_id)
        for item in data_dl:
            total_l += item['TOV_SUMA']

        # RIGHT SIDE
        sql_dr = 'select * from usadd_web.dispack_doc_dr(?)'
        data_dr = db.data_module(sql_dr, [doc_id], function_name + '_dt=2 _dr')
        total_r = 0
        for item in data_dr:
            total_r += item['TOV_SUMA']



        return render_template("dispack_doc1.html", title=title, dt=dt, data_dr=data_dr,data_dl=data_dl
                               ,total_l=total_l,total_r=total_r,data_h = data_h[0],znakl_l_id=znakl_l_id
                               ,docname = 'Акт зміни якісного стану')


def add():
    try:
        nu = request.form.get('nu')
        nd = request.form.get('nd')
        serial = request.form.get('serial')
        price = request.form.get('price')
        # sql = """ execute procedure import.dispacking(?,?,?,?) """
        # logs = db.data_module('select * from import.dispacking(?,?,?,?)', [serial, nu, nd, price])
        con = db.get_connection()
        cur = con.cursor()
        logs = cur.callproc('import.dispacking', [serial, nu, nd, price])
        print(logs)
        con.commit()
        flash("✅ Документ успішно створено!", "success")
        cur.close()
        con.close()
        return redirect(url_for('dispack_list'))
    except Exception as e:
        print(str(e))
        flash("❌ Помилка!", "danger")
        flash(f"⚠️ {str(e)}", "warning")
        return redirect(url_for('dispack_list'))

def process_disacc(id):
    try:
        # Отримуємо дані з форми модального вікна
        doc_num  = request.form.get('nua')
        doc_date = request.form.get('nda')
        user_doc_date = request.form.get('unda')
        actvr_id = request.form.get('data_h_NUM')
        unidocum_id = 0
        use_k = request.form.get('use_k') == '1'
        print('actvr_id',actvr_id)

        logs = db.data_module(' select * from import.i_snakl (?,?,?,?,?,?,?) ',
                              [doc_num, doc_date, id,user_doc_date,actvr_id,unidocum_id,use_k])

        # 3. Повідомлення про успіх (за бажанням)
        flash(f'Списано за документом  {id} успішно !', 'success')
        # flash(log for log in logs )
    except Exception as e:
        flash(f' Помилка списання за документом {id} : {str(e)} ', 'danger')
        # 4. Перенаправлення на ту саму сторінку після обробки POST (PRG pattern)
    return redirect(url_for('dispack_list'))