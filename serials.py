from flask import  request,render_template,flash,redirect,url_for
import db


def serials_search():
    result = []
    # search_term = ''
    sql = """select sn.num as id, sn.name from sklad_names sn
                where  sn.visible =1 and sn.num >=? order by 2"""
    sklads = db.data_module(sql, [300000001])
    if request.method == 'POST':
        sql = "select * from usadd_web.get_serials_by_tov_sklad(?,?)"
        tov_id = request.form.get('search_tovar', '').strip()
        sklad_id = request.form.get('sklad_id', '').strip() or None
        if sklad_id == "None":
            sklad_id = None
        result=db.data_module(sql,[tov_id,sklad_id])
        total = len(result)
        sql = "select tn.name from tovar_name tn where tn.num = ?"
        tov_name = db.data_module(sql, [tov_id])
        sql = "select sn.name from sklad_names sn where sn.num = ?"
        sklad_name = db.data_module(sql, [sklad_id])
        if result:
            return render_template('serials.html'
                                   ,result=result if result else ''
                                   ,sklads=sklads
                                   ,search_tovar=tov_id
                                   ,title = 'Пошук номерів'
                                   ,total=total
                                   ,sklad_name=sklad_name[0]['NAME'] if sklad_name else ''
                                   ,sklad_search = sklad_name
                                   ,tov_name=tov_name[0]['NAME'] if tov_name else ''
                                   ,sklad_id = sklad_id
                                   )
        else:
            flash("Запис не знайдено!", "danger")  # повідомлення + категорія (danger, success...)
            return redirect(url_for("serials_search"))
    return render_template('serials.html', sklads=sklads,result=result, title='Пошук номерів', total=None, tov_name=None)



