import  fdb,platform
import config

def get_connection():
    if platform.system() == 'Windows':
        return fdb.connect(
            # dsn='192.168.10.9/3053:D:/data/database1.fdb',
            # dsn = '192.168.10.5/3053:sklad_dev',
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

def get_data(sql,params,mode=1):
    con = get_connection()
    cur = con.cursor()
    cur.execute(sql,params)
    result  = ''
    try:
        if mode == 1:
            result = cur.fetchall()
        if mode == 2:
            result = cur.fetchone()
    except Exception as e:
        print(str(e))
    con.close()
    return result
