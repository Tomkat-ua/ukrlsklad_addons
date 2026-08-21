from flask import  request,render_template,jsonify
from datetime import datetime,timedelta
from  . import db

DEF_FROM_DATE = '2022-02-24'

def sklad_list():
    sql = """ select sn.num as sklad_id , sn.name
                from sklad_names sn
                where sn.visible = 1
                order by sn.name """
    return db.data_module(sql, [])

def parse_dates(from_date_str, to_date_str):
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else DEF_FROM_DATE
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else datetime.now().date()
    return from_date, to_date


def uv_sklad(sklad_id=None, from_date_str=None, to_date_str=None):
    data = ''

    # Якщо sklad_id не передано (перший заход), беремо з GET або дефолтний 300000001
    if not sklad_id:
        sklad_id = request.args.get('sklad_id', 300000001)

    # Дати
    today = datetime.now().date()
    default_from = today - timedelta(days=30)
    from_date = from_date_str if from_date_str else default_from.strftime('%Y-%m-%d')
    to_date = to_date_str if to_date_str else today.strftime('%Y-%m-%d')

    sklads = sklad_list()

    if request.args:
        from_date, to_date = parse_dates(from_date_str, to_date_str)
        sql = 'select * from general_roll.uv_sklad (?,?,?)'
        data = db.data_module(sql, [sklad_id, from_date, to_date])
        print(data)
    return render_template('gen-roll-uv.html',
                           data=data,
                           title='Узагальнююча відомість',
                           from_date=from_date,
                           to_date=to_date,
                           sklads=sklads,
                           sklad_id_select=int(sklad_id) if sklad_id else 300000001
                           )


def gen_roll_uv_tovid(sklad_id,tov_kod,to_date):
    # Робиш SQL-запит у БД конкретно для цього товару
    print('to_date',to_date)
    sql = """ SELECT
          t.name   as tov_name,
          t.num    as tovar_id,
          t.kod    as tov_kod,
          t.ed_izm as ei,
          t.cena   as tov_cena,
          SUM(s.z_kolvo + s.to_kolvo - s.from_kolvo ) as  tov_kol
        FROM     sklad_view_1( ? ,? ,?  ) s, tovar_name t
        WHERE    s.num = t.num AND     t.visible = 1 and t.kod = ? 
        GROUP BY t.name, t.kod, t.num, t.ed_izm, t.cena
        HAVING   (SUM(s.z_kolvo) > 0 OR SUM(s.to_kolvo) > 0 OR SUM(s.from_kolvo) >0) """
    data = db.data_module(sql,[sklad_id,to_date,to_date,tov_kod])
    print('data',data)
    # Повертаєш окремий маленький шаблон-фрагмент
    return jsonify(data)


def traffic_sklad(sklad_id, from_date_str=None, to_date_str=None,tov_id=None,tov_kod=None):
    data = ''
    if not sklad_id:
        sklad_id = request.args.get('sklad_id', 300000001)

    disable_tov_filter = request.args.get('disable_tov_filter', 0)
    print("disable_tov_filter:",disable_tov_filter)
    # Дати
    today = datetime.now().date()
    default_from = today - timedelta(days=30)
    from_date = from_date_str if from_date_str else default_from.strftime('%Y-%m-%d')
    to_date = to_date_str if to_date_str else today.strftime('%Y-%m-%d')

    sklads = sklad_list()

    if request.args:
        if disable_tov_filter == 1:
            tov_id = None
            tov_kod = None
            # print(tov_id, tov_kod)
        sql = 'select * from general_roll.traffic_sklad(?,?,?,?,?)'
        data = db.data_module(sql, [int(sklad_id), from_date, to_date,tov_id,tov_kod])
    return render_template('gen-roll-traffic.html',
                           data=data,
                           title='Рух майна по підрозділу',
                           from_date=from_date,
                           to_date=to_date,
                           sklads=sklads,
                           tov_id=tov_id,
                           tov_kod=tov_kod,
                           sklad_id_select=int(sklad_id) if sklad_id else 300000001
                           )