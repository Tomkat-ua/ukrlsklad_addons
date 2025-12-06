from flask import  request,render_template,flash
import db

def dispack_list():
    print(request.method)
    sql = """ select  * from usadd_web.DISPACK_LIST """
    try:
        data = db.data_module(sql,'')
        if request.method == "GET":
            return  render_template("dispack_list.html", title = 'Розкомплектація',data = data)
        if request.method == "POST":
            search = request.form['tov_serial']
            sql = sql + ' where  TOVAR_SER_NUM like \''+ search +'\''
            data = db.data_module(sql, '')
            print(sql)
            return render_template("dispack_list.html", title='Розкомплектація', data=data,search = search)
    except Exception as e:
        flash(f"❌ {str(e)}", "danger")
        flash(f"❗️ {sql}", "warning")
        return render_template("dispack_list.html", title='Розкомплектація')

def doc(doc_id,dt):
    sql_h = """ select  a.num,a.nu,a.date_dok,a.doc_descr as serial ,a.cena,a.sklad_id,sn.name as sklad_name
                from  actvr a
                    inner join sklad_names sn on sn.num = a.sklad_id
                where a.num =? """
    data_h = db.data_module(sql_h, [doc_id])
    title = 'Розкомплектація'
    if dt == 1:
        sql_d = """ select ad.tov_name,cast(ad.tov_kolvo as int) as tov_kolvo
                    ,ad.tov_cena,ad.tov_suma
                    from actvr_ ad where ad.pid =  ? """
        data_d = db.data_module(sql_d, [doc_id])
        return render_template("dispack_doc1.html", title=title, dt=dt, data_h=data_h[0]
                               , data_d=data_d,docname = 'Акт Виконаних Робіт')

    if dt == 2:
        sql_dr = """ select a.num,a.nu,a.date_dok,a.doc_descr,ad.tov_name,cast(ad.tov_kolvo as int) as tov_kolvo
                    ,ad.tov_cena,ad.tov_suma
                    from  znakl a
                     inner join znakl_ ad on ad.pid = a.num
                     where a.nu = (select b.nu from actvr b where b.num = ?) """

        data_dr = db.data_module(sql_dr,[doc_id])
        sql_dl = """ select a.num,a.nu,a.date_dok,a.doc_descr,ad.tov_name,cast(ad.tov_kolvo as int) as tov_kolvo
        ,ad.tov_cena,ad.tov_suma
                        from  znakl a
                     inner join znakl_ ad on ad.pid = a.num
                    where a.nu = (select b.nu||'_С' from actvr b where b.num = ?) """

        data_dl = db.data_module(sql_dl,[doc_id])
        total_l = 0
        for item in data_dl:
            total_l += item['TOV_SUMA']
        total_r = 0
        for item in data_dr:
            total_r += item['TOV_SUMA']
        return render_template("dispack_doc1.html", title=title, dt=dt, data_dr=data_dr,data_dl=data_dl
                               ,total_l=total_l,total_r=total_r,data_h = data_h[0],docname = 'Введення залишків')


    # try:
    #     return render_template("dispack_doc1.html", title = title ,dt = dt,data_h = data_h[0],data_d = data_d)
    #     # return render_template("dispack_doc1.html", title=title, dt=dt, data_d = data_d)
    # except Exception as e:
    #     return str(e)