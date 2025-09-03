from flask import  request,render_template
import db
import pandas as pd

title = 'Інформація по номеру'

def fetch_named(cursor):
    """Генерує записи як словники з іменами полів."""
    columns = [desc[0].lower() for desc in cursor.description]  # або без .lower()
    for row in cursor:
        yield dict(zip(columns, row))

def data_for_module(param,module):
    match module:
        case 'list':
            sql = "select * from usadd_web.ghist_list (?) rows 1000"
        case 'header':
            sql = "select * from usadd_web.GHIST_DET_HEADER (?)"
        case 'movies':
            sql = "select * from usadd_web.ghist_det_movies (?)"
        case _:  # optional default case
            sql = '*'
    con = db.get_connection()
    cur = con.cursor()
    cur.execute(sql, [param])
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)
    df_display = df.fillna('')
    data = df_display.to_dict(orient='records')
    con.close()
    return data

def index():
    ######### LIST #######################
    if request.method == "POST":
        # search_str = request.form.get('tov_serial')
        search_str = request.form['tov_serial']
        print('search_str',search_str)
        # data = data_for_list(search_str)
        data = data_for_module(search_str,'list')
        return render_template('ghist_.html', title=title,rows = data,search_value=search_str.strip())
    return render_template('ghist_.html',title=title)

######## DETAILS ######################################
def datails(search_str):
    print('search_str',search_str)
    search_str = int(search_str)

##### movies #########
    data_movies = data_for_module(search_str,'movies')
##### details ########
    data_header = data_for_module(search_str,'header')
    # print(data_header[0])
    # con.close()
    return render_template('ghist_det.html',title=title,rows = data_movies,row=data_header[0] )
    # print(f"details {row_id}")

