from flask import  request,render_template
import db


def serials_search():
    result = []
    search_term = ''
    if request.method == 'POST':
        sql = "select * from monitoring.get_serials_by_tov_sklad(?)"
        tov_id = request.form.get('name', '').strip()
        result=db.get_data(sql,[tov_id])
        total = len(result)
        sql = "select tn.name from tovar_name tn where tn.num = ?"
        tov_name = db.get_data(sql, [tov_id],1)
        return render_template('serials.html', result=result, title = 'Пошук номерів',total=total,tov_name=str(tov_name[0]))
    return render_template('serials.html', result=result, title='Пошук номерів', total=None, tov_name=None)



