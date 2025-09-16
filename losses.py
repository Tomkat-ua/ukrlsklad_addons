import db,os
from flask import  request, redirect, flash,render_template,url_for
import pandas as pd

def data_for_module(param,sql):
    print('sql=',sql,param)
    con = db.get_connection()
    cur = con.cursor()
    cur.execute(sql, [param])
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)
    # df['ACTION_DATE_TIME_STR'] = df['ACTION_DATE_TIME'].apply(
    #     lambda x: x.strftime('%d.%m.%Y %H:%M') if pd.notna(x) else '-' )
    df_display = df.fillna('')
    data = df_display.to_dict(orient='records')
    con.close()
    return data


def losses_list():
    page = int(request.args.get('page', 1))
    per_page = int(os.getenv("PAGE_ROWS", 5))
    offset = (page - 1) * per_page
    where = ''
    limit = 'ROWS ? TO ?'
    # 🔸 Підрахунок загальної кількості
    total_records = db.get_data("SELECT COUNT(*) FROM monitoring.get_losses where 1=1 ",None,2)
    total_pages = (total_records[0] + per_page - 1) // per_page
    serial = request.form.get('tov_serial', '').strip()
    # 🔸 Пагінований запит

    if len(serial) > 0:
        where = ' and SERIAL like \'%s\' ' % serial
        page = 0
        total_pages = 0
        limit =''
    sql = (' SELECT SDOC_ID,SDOC_NUM,SDOC_DATE,SERIAL,TOV_NAME,UNIT_NAME,action_date,action_place,ACTION_RESON,ACTION_BR,TEAM_NAME '
           ' FROM monitoring.get_losses where se = \'Літальний_апарат\' ') + where + ' order by 1 desc  '+ limit
    losses =db.get_data(sql,[offset + 1, offset + per_page])
    return render_template('losses.html',losses = losses ,title = 'Втрати майна',
                           page=page,total_pages=total_pages,total_records=total_records[0],serch_result=serial,records = len(losses))


def loss_add():
    if request.method == "POST":
        con = db.get_connection()
        cur = con.cursor()
        try:
            cur.callproc('import.i_lost',[None,
                request.form["SERIAL"],
                request.form["BAT_ORDER"],
                request.form["ACTION_DATE"],
                request.form["ACTION_PLACE"],
                request.form["ACTION_COORD"],
                request.form["ACTION_REASON"],
                request.form["TEAM_NAME"]
            ])
            response = cur.fetchone()
            if response:
                o_result = response[0]
                if 'ERROR' in o_result.upper():
                    # можна кинути виняток або обробити як завгодно
                    raise Exception(f"Procedure error: {o_result}")
                else:
                    flash(f"✅ Успішно: {response[0]}", "info")
        except Exception as e:
            flash(f"❌ {str(e)}", "danger")  # 'danger' = Bootstrap-клас для червоного
        con.commit()
        # визначаємо куди вертатись
        next_page = request.form.get("next") or url_for("index")
        return redirect(next_page)
        # return redirect("/losses")
    sn = request.args.get("sn", "")
    next_page = request.args.get("next") or url_for("index")
    return render_template("lost_add.html", next=next_page,sn=sn)

###################################33

def loss_list():
    if request.method == "POST":
        # search_str = request.form.get('tov_serial')
        search_str = request.form['tov_serial']
        print('search_str',search_str)
        sql = "select * from usadd_web.losses_list (?) order by UDOC_DATE desc ,action_date_time desc "
        data = data_for_module(search_str,sql)
        if data:
            return render_template('losses2.html', losses=data, title='Втрати майна',search=search_str)
        else:
            flash("Запис не знайдено!", "danger")  # повідомлення + категорія (danger, success...)
            return redirect(url_for("losses_list"))
    return render_template('losses2.html', losses='', title='Втрати майна' ,search=''   )

def loss_edit(id):
    print('search_str', id)
    sql = "select * from usadd.get_losses where UDOC_ID = ?"
    data = data_for_module(id, sql)
    # sql = " select num as id, name from sklad_names sn where sn.visible = ? and sn.firma_id =170  order by 2 "
    # sklads = data_for_module(1, sql)
    # sql = "select c.num as id,  c.fio as name  from client c where c.tip = ? order by 2"
    # teams = data_for_module(300000127, sql)
    return render_template('loss_edit.html', losses='', title='Втрати майна',data=data[0],sklads='',teams='')