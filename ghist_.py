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
        cur.execute(" select * from usadd_web.ghist_list (?) ",[search_str.strip()])
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
    cur.execute("select * from usadd_web.ghist_det_movies (?)", [search_str])
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)
    df_display = df.fillna('')
    data_movies = df_display.to_dict(orient='records')
    cur.close()

    ##### details ########
    # cur.execute( 'select * from usa_v_ghist_details where serial_id = ?',[search_str])
    cur.execute('select * from usadd_web.ghist_det_header (?)', [search_str])
    rows_det = cur.fetchall()
    columns_det = [desc[0] for desc in cur.description]
    df_det = pd.DataFrame(rows_det, columns=columns_det)
    df_display_det = df_det.fillna('')
    data_datail = df_display_det.to_dict(orient='records')
    con.close()
    return render_template('ghist_det.html',title=title,rows = data_movies,row=data_datail[0] )
    # print(f"details {row_id}")

