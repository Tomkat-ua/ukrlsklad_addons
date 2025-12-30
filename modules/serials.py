from flask import  request,render_template,flash,redirect,url_for,session
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
                cur.execute("""select tn.num  --0
                                     ,tn.kod  --1
                                     ,ts.tovar_ser_num  --2
                                     ,tn.name  --3
                                     , (select status_txt from usadd_web.serial_status( ts.tovar_ser_num)  ) as status --4
                                    -- , (select SKLAD_NAME from utils.FIND_TOVAR_BY_SERIAL(ts.tovar_ser_num)) as sklad_name --5
                                from tovar_serials ts
                                    inner join tovar_name tn on tn.num = ts.tovar_id
                                where (ts.doc_type_id = 9  or ts.doc_type_id = 8)
                                and ts.tovar_ser_num = ?
                                rows 1
                """, [sn])

                row = cur.fetchone()
                status = f"{row[0]}|{row[1]}|{row[3]}|{row[4]} " \
                    if row else "Не знайдено"

                results.append({'sn': sn, 'status': status})
                total = total + 1
                if status == 'Не знайдено':
                    total_err = total_err + 1
            except Exception as e:
                results.append({'sn': sn, 'status': f"Помилка: {str(e)}"})
        conn.close()
    except Exception as e:
        return f"Помилка підключення до БД: {str(e)}"
    formatted_serials = ", ".join([f"'{s}'" for s in serial_list])

    sql_g = f""" select  ts.tovar_id,tn.kod ,tn.name,count(*) as count_
                    from tovar_serials ts
                     inner join tovar_name tn on tn.num = ts.tovar_id
                    where (ts.doc_type_id = 8 or ts.doc_type_id = 9 )
                    and ts.tovar_ser_num in ({formatted_serials})
                    group by 1 ,2 ,3  order by 3"""
    if not serial_list:
        data_g = []  # або повернути порожній DataFrame
    else:
        data_g = db.data_module(sql_g,'')
        session['last_data'] = data_g
    return render_template('serial_check.html', results=results,raw_data=raw_text,
                           total=total,total_err=total_err,data_g=data_g)


def run_db_process():
    # Дістаємо дані з сесії
    data_to_process = session.get('last_data', [])

    if not data_to_process:
        return "Помилка: Немає даних для обробки. Спочатку запустіть перевірку."

    processed_count = 0
    for row in data_to_process:
        # Припустимо, ваша процедура приймає TOVAR_ID
        tovar_id = row.get('TOVAR_ID')
        doc_id   = 300000639
        req_data = request.get_json()
        doc_id = req_data.get('doc_id')
        count_   = row.get('COUNT_')
        # Виклик процедури в БД
        con = db.get_connection()
        cur = con.cursor()
        cur.callproc('import.i_actvr_det',[doc_id,tovar_id,count_])
        con.commit()
        con.close()
        processed_count += 1
    flash(f"Успішно передано {processed_count} записів",'info')
    # return redirect(url_for('serial_scheck'))
    return {"status": "ok", "message": f"Оброблено {processed_count} записів"}
    # return f"Успішно оброблено {processed_count} записів у БД!"

