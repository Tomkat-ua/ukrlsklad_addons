from flask import  request,render_template
import db,jsonify


def fetch_named(cursor):
    """Генерує записи як словники з іменами полів."""
    columns = [desc[0].lower() for desc in cursor.description]  # або без .lower()
    for row in cursor:
        yield dict(zip(columns, row))



# def index():
#     if request.method == "POST":
#         row_id = int(request.form["ID"])
#         for row in rows:
#             if row["ID"] == row_id:
#                 row["NAME"] = request.form["NAME"]
#                 row["STATUS"] = request.form["STATUS"]
#         return redirect(url_for("index"))

#    return render_template("modal_edit.html", rows=rows)

def find():
    query = request.args.get('q', '').lower()

    conn = db.get_connection()
    cur = conn.cursor()
    sql = ("""select distinct ts.tovar_ser_num ,ts.tovar_id ,tn.name as tov_name ,tn.kod
                from tovar_serials ts
                inner join tovar_name tn on tn.num = ts.tovar_id
            where ts.tovar_ser_num like ?   and ts.doc_type_id = 8""")
    cur.execute(sql, ('%' + query + '%',))

    users = [{'id': row[1], 'name': row[2]} for row in cur.fetchall()]
    conn.close()

    return jsonify(users)


    #####
    # conn = db.get_connection()
    # cur = conn.cursor()
    # result =''
    # # if request.method == 'POST':
    # sql = ("""select distinct ts.tovar_ser_num ,ts.tovar_id ,tn.name as tov_name ,tn.kod
    #             from tovar_serials ts
    #             inner join tovar_name tn on tn.num = ts.tovar_id
    #         where ts.tovar_ser_num like ?   and ts.doc_type_id = 8""")
    # tov_serial = request.form.get('tov_serial', '').strip()
    # cur.execute(sql,[tov_serial])
    #
    # # # 📤 Отримання рядків зі зверненням по імені
    # rows = fetch_named(cur)
    # for row in rows :
    #     rows = (f"ID: {row['tovar_id']}, Serial {row['tovar_ser_num']} ,Бренд: {row['tov_name']}, Код: {row['kod']}")
    # print(rows)
    # # return render_template('ghist-select.html', rows=rows)
    # return render_template("modal_edit.html", rows=rows)

def main_view():
    title = 'title'
    return render_template('ghist.html',title=title,serial="Знайдено дані для ")

def search():
    result = []
    search_term = ''
    print(request.method)
    title = 'Історія товару'
    if request.method == 'POST':
        # user_data = {
        #     "Ім’я": "Олександр",
        #     "Email": "olex@example.com",
        #     "Телефон": "+380 50 123 4567",
        #     "Роль": "Адміністратор"
        # }

        sql = ("""select distinct ts.tovar_ser_num ,ts.tovar_id ,tn.name as tov_name ,tn.kod
                    from tovar_serials ts
                    inner join tovar_name tn on tn.num = ts.tovar_id
                where ts.tovar_ser_num like ?   and ts.doc_type_id = 8""")
        tov_serial = request.form.get('tov_serial', '').strip()
        print('tov_serial',tov_serial)
        records = db.get_data(sql, [tov_serial])
        if records:
            record = records[0]
            print(record)
            fields = {
                "F1": record[0],
                "F2": record[1],
                "F3": record[2]
            }
            print('data',fields)
            return render_template('ghist.html',title=title,data=fields,serial="Знайдено дані для "+ tov_serial)
        else:
            return render_template('ghist.html',title=title,data=None ,serial="НЕ знайдено дані для " + tov_serial)

    return render_template('ghist.html', title=title, tov_name=None, serial=None)

