from flask import  request,render_template
import db


def serials_search():
    result = []
    search_term = ''
    if request.method == 'POST':
        sql = "select * from usadd_web.get_serials_by_tov_sklad(?,?)"
        tov_id = request.form.get('search_tovar', '').strip()
        sklad_id = request.form.get('search_sklad', '').strip() or None
        print(tov_id,sklad_id)
        result=db.get_data(sql,[tov_id,sklad_id])
        total = len(result)
        sql = "select tn.name from tovar_name tn where tn.num = ?"
        tov_name = db.get_data(sql, [tov_id],1)
        if sklad_id == None:
            sklad_id = 300000001
        sql = "select sn.name from sklad_names sn where sn.num = ?"
        sklad_name = db.get_data(sql, [sklad_id], 1)
        return render_template('serials.html', result=result, title = 'Пошук номерів',total=total,sklad_name=sklad_name[0],tov_name=str(tov_name[0]))

    sql = """select sn.num as id, sn.name from sklad_names sn
                where sn.num >=? order by 2"""
    sklads = db.get_data(sql, [300000001])
    return render_template('serials.html', sklads=sklads,result=result, title='Пошук номерів', total=None, tov_name=None)



