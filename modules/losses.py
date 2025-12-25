from . import db
from flask import  request, redirect, flash,render_template,url_for


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
    sn = request.args.get("sn", "")
    next_page = request.args.get("next") or url_for("index")
    return render_template("lost_add.html", next=next_page,sn=sn)

###################################
def loss_list():
    title = 'Втрати номерного майна'
    if request.method == "POST":
        search_str = request.form['tov_serial']
        sql = "select * from usadd_web.losses_list (?) order by UDOC_DATE desc ,action_date_time desc "
        data = db.data_module(sql, [search_str])
        if data:
            return render_template('losses2.html', losses=data, title = title,search=search_str)
        else:
            flash("Запис не знайдено!", "danger")  # повідомлення + категорія (danger, success...)
            # return redirect(url_for("losses_list"))
            return render_template('losses2.html', losses='', title = title, search=search_str)
    return render_template('losses2.html', losses='', title = title ,search=''   )

def loss_edit(id):
    sql = "select * from usadd.get_losses where UDOC_ID = ?"
    data = db.data_module(sql, [id])
    return render_template('loss_edit.html', losses='', title = title, data=data[0], sklads='', teams='')