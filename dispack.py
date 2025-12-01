from flask import  request,render_template,flash
import db
import pandas as pd



def dispack_list():
    print(request.method)
    sql = """ select a.nu, ad.tov_name,ts.tovar_ser_num
                from  actvr a
                    inner join actvr_ ad on ad.pid = a.num
                    inner join tovar_serials ts on ts.doc_type_id = 6
                     and ts.tovar_id = ad.tovar_id
                     and ts.doc_id = a.num
                where a.client_id = 300000203 order by a.nu desc """
    try:
        con = db.get_connection()
        cur = con.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=columns)
        df_display = df.fillna('')
        data = df_display.to_dict(orient='records')
        con.close()
        print(data)
        if request.method == "GET":
            return  render_template("dispack_list.html", title = 'Розкомплектація',data = data)
    except Exception as e:
        flash(f"❌ {str(e)}", "danger")
        flash(f"❗️ {sql}", "warning")
        return render_template("dispack_list.html", title='Розкомплектація')

