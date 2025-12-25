from . import db
from flask import  request, flash,render_template

title = 'Втрати неномерного майна'

def losses_list():
    if request.method == "POST":
        # search_str = request.form.get('tov_serial')
        search_str = request.form['search']
        print('search_str', search_str)
        sql = "select * from usadd_web.losses_list (?,2) order by UDOC_DATE desc ,action_date_time desc "
        # data = data_for_module(search_str, sql)
        data = db.data_module(sql, [search_str])
        if data:
            return render_template('losses_nn_list.html', losses=data, title=title, search=search_str)
        else:
            flash("Запис не знайдено!", "danger")  # повідомлення + категорія (danger, success...)
            return render_template('losses_nn_list.html', losses='', title = title, search=search_str)
    return render_template('losses_nn_list.html' ,title = title)