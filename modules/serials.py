from flask import  request,render_template,flash,redirect,url_for,session,jsonify
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
        total_sap = 0
        total_acc = 0
        for sn in serial_list:
            try:
                # Виклик процедури (залежно від того, як вона написана у вас)
                # Якщо процедура повертає значення (selectable):
                cur.execute("""select tn.num  --0
                                     ,tn.kod  --1
                                     ,ts.tovar_ser_num  --2
                                     ,tn.name  --3
                                     , (select status_txt from usadd_web.serial_status( ts.tovar_ser_num)  ) as status --4
                                     , usadd_web.SERIAL_IS_PLACE(ts.TOVAR_SER_NUM) AS SKLAD_NAME --5
                                from tovar_serials ts
                                    inner join tovar_name tn on tn.num = ts.tovar_id
                                where (ts.doc_type_id = 9  or ts.doc_type_id = 8)
                                and ts.tovar_ser_num = ?
                                rows 1
                """, [sn])

                row = cur.fetchone()
                if row:
                    status = f"{row[0]} | {row[1]} | {row[3]} | {row[4]} | {row[5]} "
                    # if row else "Не знайдено" total_err = total_err + 1
                    state_raw = row[4]
                    state = state_raw.strip()
                    if state == 'На обліку':
                        total_acc = total_acc + 1
                    if state == 'Списано (акт пуску)':
                        total_sap = total_sap + 1
                else:
                    status = "Не знайдено"
                    total_err = total_err + 1

                results.append({'sn': sn, 'status': status})
                total = total + 1

            except Exception as e:
                results.append({'sn': sn, 'status': f"Помилка: {str(e)}"})
        conn.close()
    except Exception as e:
        return f"Помилка підключення до БД: {str(e)}"
    formatted_serials = ", ".join([f"'{s}'" for s in serial_list])

    sql_g = f"""
                select * from (
                 select ts.tovar_id   ,tn.kod   ,tn.name
                 ,usadd_web.serial_status_code(ts.tovar_ser_num) as status_code
                 ,usadd_web.serial_is_place(ts.tovar_ser_num)  as sklad_name
                 ,count(*) as count_
                from tovar_serials ts
                 inner join tovar_name tn on tn.num = ts.tovar_id
                where (ts.doc_type_id = 8 or ts.doc_type_id = 9 )
                and ts.tovar_ser_num in  ({formatted_serials} )
                group by 1 ,2 ,3,4,5) where status_code = 0
                order by 3
"""
    is_multi_sklad=''
    main_sklad=''
    if not serial_list:
        data_g = []  # або повернути порожній DataFrame
    else:
        data_g = db.data_module(sql_g,'')
        session['data_g'] = data_g
        session['formatted_serials'] = formatted_serials

        # Збираємо всі унікальні назви складів
        unique_sklads = set(row['SKLAD_NAME'] for row in data_g if row.get('SKLAD_NAME'))
        # Передаємо цей список або прапорець у шаблон
        is_multi_sklad = len(unique_sklads) > 1
        main_sklad = list(unique_sklads)[0] if unique_sklads else None
    print('is_multi_sklad',is_multi_sklad)
    print('main_sklad',main_sklad)
    return render_template('serial_check.html', results=results,
                           raw_data=raw_text,
                           total=total,
                           total_err=total_err,
                           data_g=data_g,
                           total_sap=total_sap,
                           total_acc=total_acc,
                           is_multi_sklad=is_multi_sklad,
                           main_sklad=main_sklad)


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
        # req_data = request.get_json()
        # doc_id   = req_data.get('doc_id')
        count_   = row.get('COUNT_')
        try:
            cur.callproc('import.i_actvr_det',[doc_id,tovar_id,count_])
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
    sql = f""" execute block
as
    declare variable tovar_id tnum ;
    declare variable serial   tsm_kod;
    declare variable doc_id   tnum ;
    declare variable sklad_id tnum;
begin
 select a.sklad_id from actvr a where a.num = {doc_id} into sklad_id;
  if ( sklad_id is null) then
  begin
   exception ex_common_error using ('[ERROR-00100: SKLAD_ID is NULL]');
   exit;
  end
 for
    select
     ts.tovar_id,ts.tovar_ser_num
    from tovar_serials ts
    where (ts.doc_type_id = 8 or ts.doc_type_id = 9 )
    and usadd_web.serial_status_code(ts.tovar_ser_num)  = 0
    and ts.tovar_ser_num in({serials})
     into tovar_id, serial
    do
        execute procedure import.i_serial(:tovar_id,:serial,{doc_id},:sklad_id,-1);
end """
    print(sql)
    try:
        con = db.get_connection()
        cur = con.cursor()
        cur.execute(sql,'')
        con.commit()
        con.close()
    except Exception as e:
        error_full_text = str(e.args[0]) if hasattr(e, 'args') and e.args else str(e)
        return jsonify({
            "status": "error",
            "message": error_full_text
        }), 500
    return {"status": "ok", "message": f"OK"}
