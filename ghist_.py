from flask import  request,render_template
import db
import pandas as pd


title = 'Інформація по номеру'

def fetch_named(cursor):
    """Генерує записи як словники з іменами полів."""
    columns = [desc[0].lower() for desc in cursor.description]  # або без .lower()
    for row in cursor:
        yield dict(zip(columns, row))




def index():
    ######### LIST #######################
    if request.method == "POST":
        # search_str = request.form.get('tov_serial')
        search_str = request.form['tov_serial']
        print('search_str',search_str)
        con = db.get_connection()
        cur = con.cursor()
        cur.execute(""" select distinct ts.num as serial_id, ts.tovar_id,ts.tovar_ser_num,tn.kod,tn.name as tov_name
                        ,case when tss.num is not null  then 'Втрачено' else 'На обліку' end as status
                        from tovar_serials ts
                        inner join tovar_name tn on tn.num = ts.tovar_id
                        left join tovar_serials tss on tss.tovar_ser_num = ts.tovar_ser_num and tss.doc_type_id =11
                        where ts.tovar_ser_num like ?
                        and ts.doc_type_id in( 8,9) """,[search_str.strip()])
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=columns)
        df_display = df.fillna('')
        data = df_display.to_dict(orient='records')
        con.close()
        return render_template('ghist_.html', title=title,rows = data,search_value=search_str.strip())
    return render_template('ghist_.html',title=title)

######## DETAILS ######################################
def datails(search_str):
    print('search_str',search_str)
    search_str = int(search_str)
    con = db.get_connection()
    cur = con.cursor()
    ##### movies #########
    cur.execute(""" SELECT vd.doc_type,dt.name AS doc_name,vd.num,vd.nu,vd.date_dok,sn.num as  sklad_id,sn.name AS sklad_name,
                           case  when ts.tovar_ser_kolvo  >0 then '+' else '-' end as oper_type                       
                    FROM   tovar_name tn
                      inner join tovar_serials ts on ts.tovar_id = tn.num
                        and ts.tovar_ser_num = (select t.tovar_ser_num from tovar_serials t where t.num = ?)  
                        and ts.ser_type_id = 0  and ts.doc_type_id <> 8
                      inner JOIN doc_types dt ON (ts.doc_type_id = dt.num)
                      inner JOIN sklad_names sn ON (ts.sklad_id = sn.num)
                      inner join view_alldocs vd on vd.doc_type =  ts.doc_type_id
                       and vd.num= ts.doc_id   AND vd.firma_id = 170 and vd.is_move = 1   
                    ORDER BY VD.DATE_DOK ,vd.num ,ts.tovar_ser_kolvo  """, [search_str])
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)
    df_display = df.fillna('')
    data_movies = df_display.to_dict(orient='records')
    cur.close()

    ##### details ########
    cur.execute( 'select * from usa_v_ghist_details where serial_id = ?',[search_str])

    rows_det = cur.fetchall()
    columns_det = [desc[0] for desc in cur.description]
    df_det = pd.DataFrame(rows_det, columns=columns_det)
    df_display_det = df_det.fillna('')
    data_datail = df_display_det.to_dict(orient='records')
    con.close()
    return render_template('ghist_det.html',title=title,rows = data_movies,row=data_datail[0] )
    # print(f"details {row_id}")

