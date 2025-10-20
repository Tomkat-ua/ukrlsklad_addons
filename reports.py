from flask import  request,render_template,render_template_string #,flash,redirect,url_for
import db,json,re #,html
from datetime import date

today = date.today().isoformat()

# reports = [
#      {"ID": 1, "NAME": "Склад"}
# ]

# with open('reports.json', 'r', encoding='utf-8') as f:
#     # reports = json.load(f)
#     con = db.get_connection()
#     cur = con.cursor()
#     cur.execute("SELECT NUM, REP_NAME FROM REPORTS_WEB ")
#     reports = cur.fetchall()
#     con.close()

def reports_list():
    con = db.get_connection()
    cur = con.cursor()
    cur.execute("SELECT NUM, REP_NAME FROM REPORTS_WEB ")
    reports = cur.fetchall()
    con.close()
    return render_template("reports.html",title='Звіти',reports = reports)

def reports_list2(rep_id):


    """Відображення сторінки звіту з параметрами та результатом"""
    con = db.get_connection()
    cur = con.cursor()
    cur.execute("SELECT REP_NAME, QRY, PARAMS, HTML FROM REPORTS_WEB WHERE NUM = ?", (rep_id,))
    row = cur.fetchone()
    con.close()

    if not row:
        return f"❌ Звіт #{rep_id} не знайдено", 404

    rep_name, qry, params_json, html_content = row
    params = json.loads(params_json or "{}")

    # --- Генерація фільтрів ---
    if not params:
        form_html = ""
    else:
        form_html = ""
        values = {}
        con = db.get_connection()
        cur = con.cursor()
        for p in params.get("params", []):
            name = p["name"]
            val = request.form.get(name, "")
            values[name] = val
            if p["type"] == "select":
                cur.execute(p["sql"])
                options = "".join(
                    f'<option value="{r[0]}" {"selected" if str(r[0]) == val else ""}>{r[1]}</option>'
                    for r in cur.fetchall()
                )
                default_val=p["default"]
                form_html += f"""
                <div class="mb-2 d-flex align-items-center">
                    <label class="me-2 mb-0" style="min-width: 120px;">{p['label']}:</label>
                    <select class="form-select-sm" style="width: 400px;" value="{default_val}" name="{name}">
                        {options}
                    </select>
                </div>
                """
            elif p["type"] == "date":
                print(p["default"])
                form_html += f"""
                    <div class="mb-3">
                        <label>{p['label']}</label>
                        <input type="date" class="form-control-sm" name="{name}" value="{today}">
                    </div>
                """
            elif p["type"] == "number":
                form_html += f"""
                    <div class="mb-3">
                        <label>{p['label']}</label>
                        <input type="number" class="form-control-sm" name="{name}" value=0 style="width: 112px;" placeholder="Введіть число">
                    </div>
                """
            elif p["type"] == "boolean":
                form_html += f"""
                    <div class="mb-3">
                        <label>{p['label']}</label>
                        <input class="form-check-input-sm" type="checkbox" name="{name}" value="{val}" id="flexCheckDefault">
                    </div>
                """
            else:
                form_html += f"""
                    <div class="mb-3">
                        <label>{p['label']}</label>
                        <input type="text" class="form-control-sm" name="{name}" value="{val}">
                    </div>
                """

    # --- Якщо форма відправлена, підставляємо параметри ---
    result_html = ""
    if request.method == "POST":
        q = qry
        for k, v in values.items():
            q = q.replace(f":{k}", f"'{v}'")

        print(q)
        cur.execute(q)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]

        result_html = ("<table id='tList' class='table table-striped table-bordered align-middle' >"
                       "<thead class='table-dark' ><tr>"
                       + "".join(f"<th>{c}</th>" for c in cols)
                       + "</tr></thead><tbody style='line-height: 1; padding: 0.25rem;'>")


        for r in rows:
            result_html += "<tr>" + "".join(f"<td>{v}</td>" for v in r) + "</tr>"
        result_html += ("</tbody>  "
                          "<tfoot style='font-weight: bold;'>"
                           "<tr> "
                            "<td>Всього:</td> <td id='total'></td>"
                           "</tr>"
                          "</tfoot>"
                        "</table>")

    con.close()

    # --- Збірка сторінки ---
    html_template = f"""
    {{% extends "base_tmp.html" %}}
    {{% block content %}}
    <h5>{rep_name}</h5>
    <form method="POST">
        {form_html}
        <button type="submit" class="btn btn-sm btn-primary" onclick="loadReport()">Згенерувати</button>
        <button type="button" class="btn btn-sm btn-primary" onclick="copyTable()">📋 Копіювати таблицю</button>
        <button type="button" class="btn btn-sm btn-primary" onclick="downloadTableAsCSV('{rep_name}')">Зберегти як CSV</button>
        <button type="button" class="btn btn-sm btn-primary" onclick="downloadTableAsXLSX('{rep_name}')">Зберегти як XLSX</button>      
    </form>
    <hr>
    {result_html}
    {{% endblock %}}
    """

    return render_template_string(html_template)


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

