from flask import  request,render_template,flash,redirect, url_for
import sys,db
import config

title = 'Розкомплектація'

def dispack_list():
    function_name = sys._getframe(0).f_code.co_name
    sql = """ select  * from usadd_web.DISPACK_LIST (?,?,?)"""
    try:
        data = db.data_module(sql,[0,None,None],function_name)
        print(data)
        if request.method == "GET":
            return  render_template("dispack_list.html", title = 'Розкомплектація',data = data)
        if request.method == "POST":
            serial = request.form['tov_serial']
            data = db.data_module(sql, [2,None,serial],function_name)
            return render_template("dispack_list.html", title='Розкомплектація', data=data,search = serial)
    except Exception as e:
        flash(f"❌ {str(e)}", "danger")
        flash(f"❗️ {sql}", "warning")
        return render_template("dispack_list.html", title='Розкомплектація')

def doc(doc_id,dt):
    function_name = sys._getframe(0).f_code.co_name

    # COMMON HEAD
    sql_h = """ select  *    from usadd_web.DISPACK_LIST (?,?,?)"""
    data_h = db.data_module(sql_h, [1,doc_id,None],function_name+'_header')
    # print(data_h)
    #ACT VR
    if dt == 1:
        sql_d = 'select * from usadd_web.dispack_doc_d(?)'
        data_d = db.data_module(sql_d, [doc_id],function_name+' _dt=1')
        return render_template("dispack_doc1.html", title=title, dt=dt, data_h=data_h[0]
                               , data_d=data_d,docname = 'Акт Виконаних Робіт')

    #INS ZNAKL
    if dt == 2:
        # LEFT SIDE
        sql_dl = 'select * from usadd_web.dispack_doc_dl(?)'
        data_dl = db.data_module(sql_dl,[doc_id],function_name+'_dt=2 _dl')
        total_l = 0
        #znakl_l_id = data_dl[0]['NUM']
        # print('znakl_l_id:',znakl_l_id)
        for item in data_dl:
            total_l += item['TOV_SUMA']

        # RIGHT SIDE
        sql_dr = 'select * from usadd_web.dispack_doc_dr(?)'
        data_dr = db.data_module(sql_dr,[doc_id],function_name+'_dt=2 _dr')
        total_r = 0
        for item in data_dr:
            total_r += item['TOV_SUMA']



        return render_template("dispack_doc1.html", title=title, dt=dt, data_dr=data_dr,data_dl=data_dl
                               ,total_l=total_l,total_r=total_r,data_h = data_h[0]
                               ,docname = 'Акт зміни якісного стану')


def add():
    # print(request.method)
    # if request.method == 'POST':
    #     try:
    #         nu = request.form.get('nu')
    #         nd = request.form.get('nd')
    #         serial = request.form.get('serial')
    #         price = request.form.get('price')
    #         logs = db.data_module('select * from import.dispacking(?,?,?,?)',[serial,nu,nd,price])
    #         for log in logs:
    #             msg = log['RESULT']
    #             if msg[1:6] == 'ERROR':
    #                 flash(f"❌ {msg}", "danger")
    #             else:
    #                 flash("✅ Документ успішно створено!", "success")
    #                 if config.debug_mode == 1:
    #                     flash(f"{msg}", "success")
    #         return redirect(url_for('dispack_list'))
    #     except Exception as e:
    #         flash("❌ Помилка!", "danger")
    #         flash(f"⚠️ {str(e)}", "warning")
    # else:
    #     return render_template("dispack_add.html", title=title)
    print(request.method)
    try:
        nu = request.form.get('nu')
        nd = request.form.get('nd')
        serial = request.form.get('serial')
        price = request.form.get('price')
        logs = db.data_module('select * from import.dispacking(?,?,?,?)',[serial,nu,nd,price])
        print(logs)
        return redirect(url_for('dispack_list'))
    except Exception as e:
        flash("❌ Помилка!", "danger")
        flash(f"⚠️ {str(e)}", "warning")
        return redirect(url_for('dispack_list'))



def process_disacc():
    # Отримуємо дані з форми модального вікна
    item_name = request.form.get('item_name')
    item_id = request.form.get('item_id')
    item_status = request.form.get('item_status')
    comment = request.form.get('comment')

    # === Ваша логіка обробки даних ===
    # 1. Валідація даних
    if not item_name or not item_status:
        # flash('Необхідно заповнити всі обов\'язкові поля.', 'danger')
        return redirect(url_for('index'))  # Повертаємо на головну сторінку

    # 2. Збереження до бази даних
    # save_to_database(item_name, item_id, item_status, comment)

    # 3. Повідомлення про успіх (за бажанням)
    # flash(f'Предмет "{item_name}" успішно додано!', 'success')

    # 4. Перенаправлення на ту саму сторінку після обробки POST (PRG pattern)
    return redirect(url_for('index'))