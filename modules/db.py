import  fdb,platform,pandas as pd
from . import config

def get_connection():
    if platform.system() == 'Windows':
        return fdb.connect(
            host=config.db_server,
            port=config.db_port,
            database=config.db_path,
            user=config.db_user,
            password=config.db_password,
            fb_library_name="C:/sklad/x64/fbclient.dll",
            charset="utf-8"
        )
    else:
        return fdb.connect(
            host=config.db_server,
            port=config.db_port,
            database=config.db_path,
            user=config.db_user,
            password=config.db_password,
            charset="utf-8"
        )

def data_module(sql,params,des = None):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=columns)
        df_display = df.fillna('')
        data = df_display.to_dict(orient='records')
        con.commit()
        con.close()
        if config.debug_mode > 0:
            print('⚠️Debug mode ON⚠️')
            print('🔼sql:', sql)
            print('⏺️params:',params)
            if config.debug_mode > 1:
                print('⏬data:', data)
            if des:
                print('🔤description:',des)
        return data
    except Exception as e:
        print(f'ERROR - {str(e)}')
        print(sql)
        print(params)
        return "Internal Server Error", 500

# def get_data(sql,params,mode=1):
#     con = get_connection()
#     cur = con.cursor()
#     cur.execute(sql,params)
#     result  = ''
#     try:
#         if mode == 1:
#             result = cur.fetchall()
#         if mode == 2:
#             result = cur.fetchone()
#     except Exception as e:
#         print(str(e))
#     con.close()
#     return result
