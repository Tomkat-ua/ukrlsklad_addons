import db,os
from flask import  request, redirect, flash,render_template



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
    sql = (' SELECT SDOC_ID,SDOC_NUM,SDOC_DATE,SERIAL,TOV_NAME,UNIT_NAME,action_date,action_place,ACTION_RESON,ACTION_BR '
           ' FROM monitoring.get_losses where se = \'Літальний_апарат\' ') + where + ' order by 1 desc  '+ limit
    losses =db.get_data(sql,[offset + 1, offset + per_page])
    # losses = config.fetchall_as_dict(losses)
    # total_records = len(losses)
    return render_template('losses.html',losses = losses ,title = 'Втрати майна',
                           page=page,total_pages=total_pages,total_records=total_records[0],serch_result=serial,records = len(losses))

def loss_add():
    if request.method == "POST":
        con = db.get_connection()
        cur = con.cursor()
        try:
            cur.callproc('import.i_snakl',[None,
                request.form["SERIAL"],
                request.form["BAT_ORDER"],
                request.form["ACTION_DATE"],
                request.form["ACTION_PLACE"],
                request.form["ACTION_COORD"],
                request.form["ACTION_REASON"]
            ])
            response = cur.fetchone()
            if response:
                o_result = response[0]
                if 'ERROR' in o_result.upper():
                    # flash(f"❌ {response[0]}", "danger")
                    # можна кинути виняток або обробити як завгодно
                    raise Exception(f"Procedure error: {o_result}")
                else:
                    flash(f"✅ Успішно: {response[0]}", "info")
            # flash(f"✅ {response[0]}", "info")
            #raise ValueError("Помилка обробки форми")
        except Exception as e:
            flash(f"❌ {str(e)}", "danger")  # 'danger' = Bootstrap-клас для червоного
        con.commit()
        return redirect("/losses")
    return render_template("lost_add.html")

