from flask import  request,render_template,flash,redirect,url_for
from . import db


def serials_search():
    result = []
    # search_term = ''
    sql = """select sn.num as id, sn.name from sklad_names sn
                where  sn.visible =1 and sn.num >=? order by 2"""
    sklads = db.data_module(sql, [300000001])
    if request.method == 'POST':
        sql = "select * from usadd_web.get_serials_by_tov_sklad(?,?)"
        tov_id = request.form.get('search_tovar', '').strip()
        sklad_id = request.form.get('sklad_id', '').strip() or None
        if sklad_id == "None":
            sklad_id = None
        result= db.data_module(sql, [tov_id, sklad_id])
        total = len(result)
        sql = "select tn.name from tovar_name tn where tn.num = ?"
        tov_name = db.data_module(sql, [tov_id])
        sql = "select sn.name from sklad_names sn where sn.num = ?"
        sklad_name = db.data_module(sql, [sklad_id])
        if result:
            return render_template('serials.html'
                                   ,result=result if result else ''
                                   ,sklads=sklads
                                   ,search_tovar=tov_id
                                   ,title = 'Пошук номерів'
                                   ,total=total
                                   ,sklad_name=sklad_name[0]['NAME'] if sklad_name else ''
                                   ,sklad_search = sklad_name
                                   ,tov_name=tov_name[0]['NAME'] if tov_name else ''
                                   ,sklad_id = sklad_id
                                   )
        else:
            flash("Запис не знайдено!", "danger")  # повідомлення + категорія (danger, success...)
            return redirect(url_for("serials_search"))
    return render_template('serials.html', sklads=sklads,result=result, title='Пошук номерів', total=None, tov_name=None)


def serials_check():

    # @app.route('/process', methods=['POST'])
    raw_data = request.form.get('serials', '')
    # Розбиваємо текст на рядки та видаляємо зайві пробіли
    serial_list = [line.strip() for line in raw_data.split('\n') if line.strip()]
    raw_text = request.form.get('serials', '')
    results = []

    try:
        conn = db.get_connection()
        cur = conn.cursor()
        total = 0
        total_err = 0
        for sn in serial_list:
            try:
                # Виклик процедури (залежно від того, як вона написана у вас)
                # Якщо процедура повертає значення (selectable):
                cur.execute("""select ts.num,tn.kod,ts.tovar_ser_num ,tn.name
                                from tovar_serials ts
                                    inner join tovar_name tn on tn.num = ts.tovar_id
                                where (ts.doc_type_id = 9  or ts.doc_type_id = 8)
                                and ts.tovar_ser_num = ?
                                rows 1
                """, (sn,))


                row = cur.fetchone()
                status = f"{row[1]} {row[2]} {row[3]} " \
                    if row else "Не знайдено"

                # Або якщо це Executable Procedure:
                # status = cur.callproc('MY_PROCEDURE', (sn,))[0]

                results.append({'sn': sn, 'status': status})
                total = total + 1
                if status == 'Не знайдено':
                    total_err = total_err + 1
            except Exception as e:
                results.append({'sn': sn, 'status': f"Помилка: {str(e)}"})

        conn.close()
        print('total',total,'total_err',total_err)
    except Exception as e:
        return f"Помилка підключення до БД: {str(e)}"
    # print(results)
    return render_template('serial_check.html', results=results,raw_data=raw_text,total=total,total_err=total_err)


