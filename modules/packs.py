from . import db
from flask import  request,render_template,redirect, jsonify,url_for

def packs_get():
    sql_m = """select  p.*,tn.name as tovar_name, tn.KOD
                from packs p
                left join tovar_name tn on tn.num = p.tovar_id """

    data_h = db.data_module(sql_m, '')
    return render_template('packs.html',master_rows=data_h)


def packs_post():
    # 1. Збираємо дані з полів форми (name="...")
    mode = request.form.get('mode')
    idx = request.form.get('id')
    name = request.form.get('name')
    tovar_id = request.form.get('tovarid')

    try:
        conn = db.get_connection()
        cur = conn.cursor()

        if mode == 'edit':
            # Механіка оновлення
            # В Firebird важливо, щоб типи даних збігалися (idx має бути числом)
            sql = "UPDATE packs SET NAME = ?, TOVAR_ID = ? WHERE NUM = ?"
            print(name,tovar_id,idx)
            cur.execute(sql, (name, tovar_id, idx))

        elif mode == 'new':
            # Механіка вставки
            # Якщо NUM генерується тригером у Firebird, ми його не вказуємо
            sql = "INSERT INTO packs (NAME, TOVAR_ID) VALUES (?, ?)"
            cur.execute(sql, (name, tovar_id))

        conn.commit()
        # Можна додати повідомлення для користувача (через flash)
        print(f"Успішно виконано {mode} для ID {idx}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Помилка при збереженні: {e}")
        # Тут можна повернути сторінку з помилкою або flash-повідомленням

    finally:
        if conn:
            conn.close()

    # Після будь-якої дії повертаємо користувача на список документів
    return redirect(url_for('packs_list'))

def get_details(master_id):
    con = db.get_connection()
    cur = con.cursor()
    sql_d = """ select
pd.NUM,
p.NAME as pack_name,
pd.PACK_ID,
pd.TOVAR_ID,
tn.KOD,
pd.TOVAR_QUANT,
pd.BALANCE,
pd.BITPROP,
tn.NAME as tovar_name,
tn.CENA
 from packs_det pd
  inner join packs p on p.num = pd.pack_id
  inner join tovar_name tn on tn.num = pd.tovar_id
where pd.pack_id  = ?  """

    cur.execute(sql_d, [master_id])
    # Формуємо JSON для відповіді
    columns = [column[0] for column in cur.description]
    results = [dict(zip(columns, row)) for row in cur.fetchall()]

    return jsonify(results)