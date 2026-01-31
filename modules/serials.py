from flask import  request,render_template,flash,redirect,url_for,session,jsonify
from . import db


def serials_search():
    result = []
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
    return render_template('serials.html', sklads=sklads,result=result, title='Пошук номерів',
                           total=None, tov_name=None)

##========================================================================================================================
def serials_check():

    raw_data = request.form.get('serials', '')
    # Розбиваємо текст на рядки та видаляємо зайві пробіли
    serial_list = [line.strip() for line in raw_data.split('\n') if line.strip()]
    raw_text = request.form.get('serials', '')
    results = []
    formatted_serials = ",".join([str(s).strip() for s in serial_list])
    sql_list = 'select * from usadd_web.GET_SERIALS_LIST(?)'
    data_serials = db.data_module(sql_list,[formatted_serials])
    results = []
    total_acc = 0  # На обліку
    total_sap = 0  # Списано
    total_err = 0  # Не знайдено
    total = len(data_serials)

    for row in data_serials:
        print(row['STATUS_COLOR'])
        sn = row['TOVAR_SER_NUM']
        if row['NAME']:  # Якщо ім'я товару є, значить знайшли в базі
            dup_label = f" [--- ДУБЛЬ: {row['C_EX']} ---]" if row['C_EX'] > 1 else ""
            status_text = f"""{row['NUM']} | {row['KOD']} | {row['NAME']} | {row['STATUS']} 
            | {row['SKLAD_NAME']} {dup_label} | {row['PRICE']}"""
            state = row['STATUS'].strip() if row['STATUS'] else ""
            if state == 'На обліку':
                total_acc += 1
            elif state == 'Списано (акт пуску)':
                total_sap += 1
        else:
            status_text = "Не знайдено"
            total_err += 1
        results.append({'sn': sn, 'status': status_text,'c_ex':row['C_EX'] })


#### GROUP LIST #############3
    sql_g = ' select * from usadd_web.GET_SERIALS_SUMMARY ( ? )'
    is_multi_sklad=''
    main_sklad=''
    if not serial_list:
        data_g = []  # або повернути порожній DataFrame
    else:
        data_g = db.data_module(sql_g,[formatted_serials])
        session['data_g'] = data_g
        session['formatted_serials'] = formatted_serials

        # Збираємо всі унікальні назви складів
        unique_sklads = set(row['SKLAD_NAME'] for row in data_g if row.get('SKLAD_NAME'))
        # Передаємо цей список або прапорець у шаблон
        is_multi_sklad = len(unique_sklads) > 1
        main_sklad = list(unique_sklads)[0] if unique_sklads else None

    return render_template('serial_check.html', results=results,
                           raw_data=raw_text,
                           total=total,
                           total_err=total_err,
                           data_g=data_g,
                           total_sap=total_sap,
                           total_acc=total_acc,
                           is_multi_sklad=is_multi_sklad,
                           main_sklad=main_sklad,
                           column_data=data_serials)

def add_to_actv():
    # Дістаємо дані з сесії
    data_to_process = session.get('data_g', [])
    serials_to_process = session.get('formatted_serials', [])

    req_data = request.get_json()
    doc_id = req_data.get('doc_id')
    if not data_to_process:
        return "Помилка: Немає даних для обробки. Спочатку запустіть перевірку."
    processed_count = 0
    con = db.get_connection()
    cur = con.cursor()
    for row in data_to_process:
        tovar_id = row.get('TOVAR_ID')
        count_   = row.get('COUNT_')
        price    = row.get('PRICE')
        try:
            cur.callproc('import.i_actvr_det',[doc_id,tovar_id,count_,price])
            processed_count += 1
        except Exception as e:
            error_full_text = str(e.args[0]) if hasattr(e, 'args') and e.args else str(e)
            return jsonify({
                "status": "error",
                "message": error_full_text
            }), 500
    con.commit()
    con.close()
    ## add serials
    serials_to_actv(serials_to_process,doc_id)
    ##
    return {"status": "ok", "message": f"Оброблено {processed_count} записів"}

def serials_to_actv(serials,doc_id):
    try:
        con = db.get_connection()
        cur = con.cursor()
        cur.execute("EXECUTE PROCEDURE usadd_web.import_serials_to_avr(?, ?)", (serials, doc_id))
        # print(serials,doc_id)
        con.commit()
        # cur.execute(sql,'')
        con.close()
    except Exception as e:
        error_full_text = str(e.args[0]) if hasattr(e, 'args') and e.args else str(e)
        return jsonify({
            "status": "error",
            "message": error_full_text
        }), 500
    return {"status": "ok", "message": f"OK"}
