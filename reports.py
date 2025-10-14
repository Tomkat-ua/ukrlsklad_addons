from flask import  request,render_template,flash,redirect,url_for
import db,json,re


# reports = [
#      {"ID": 1, "NAME": "Склад"}
# ]

with open('reports.json', 'r', encoding='utf-8') as f:
    reports = json.load(f)


def reports_list():
    return render_template("reports.html",title='Звіти',reports = reports)
#
# def export():
#     columns, rows = get_data()
#
#     df = pd.DataFrame(rows, columns=columns)
#
#     # 🔹 Формуємо назву файлу
#     filename = f"cars_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
#     filepath = os.path.join(EXPORT_DIR, filename)
#
#     # 🔹 Зберігаємо файл на диск
#     df.to_excel(filepath, index=False)
#
#     # 🔹 Повертаємо файл користувачу для завантаження
#     return send_file(filepath, as_attachment=True)

def report(id):
    record = next((item for item in reports if item["ID"] == id), None)
    qry_id = record['QRY_ID']
    repname = record['NAME']

    con = db.get_connection()
    cur = con.cursor()
    cur.execute( 'select qry from QUERYS where num = ? ',[qry_id])
    row = cur.fetchone()
    clean_sql=''
    if row:  # row — це кортеж
        sql_text = row[0]  # беремо перше поле
        clean_sql = re.sub(r'\s+', ' ', sql_text).strip()

    cur.execute(clean_sql)
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    con.close()

    return render_template('report.html', columns=columns, rows=rows,repname=repname)

