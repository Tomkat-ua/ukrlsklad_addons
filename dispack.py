from flask import  request,render_template,flash
import sys,db

def dispack_list():
    function_name = sys._getframe(0).f_code.co_name
    sql = """ select  * from usadd_web.DISPACK_LIST (?,?,?)"""
    try:
        data = db.data_module(sql,[0,None,None],function_name)
        print(data)
        if request.method == "GET":
            return  render_template("dispack_list.html", title = 'Розкомплектація',data = data)
        if request.method == "POST":
            serial = request.form['tov_serial']
            data = db.data_module(sql, [2,None,serial],function_name)
            return render_template("dispack_list.html", title='Розкомплектація', data=data,search = serial)
    except Exception as e:
        flash(f"❌ {str(e)}", "danger")
        flash(f"❗️ {sql}", "warning")
        return render_template("dispack_list.html", title='Розкомплектація')

def doc(doc_id,dt):
    function_name = sys._getframe(0).f_code.co_name
    # COMMON HEAD
    sql_h = """ select  *    from usadd_web.DISPACK_LIST (?,?,?)"""
    data_h = db.data_module(sql_h, [1,doc_id,None],function_name+'_header')
    title = 'Розкомплектація'


    if dt == 1:
        sql_d = """ select ad.tov_name,cast(ad.tov_kolvo as int) as tov_kolvo
                    ,ts.tovar_ser_num ,ts.doc_type_id
                    ,case
                        when ad.tov_cena = 0 then pd.tov_cena
                        else ad.tov_cena
                    end as tov_cena
                    from actvr_ ad
                      inner join tovar_serials ts on ts.doc_id = ad.pid
                       and ts.tovar_id = ad.tovar_id and ts.doc_type_id = 6
                      inner join tovar_serials tsp  on tsp.tovar_ser_num = ts.tovar_ser_num
                       and tsp.doc_type_id = 8
                      inner join pnakl_ pd on pd.pid = tsp.doc_id
                       and pd.tovar_id = ad.tovar_id 
                    where ad.pid =? """
        data_d = db.data_module(sql_d, [doc_id],function_name+' _dt=1')
        return render_template("dispack_doc1.html", title=title, dt=dt, data_h=data_h[0]
                               , data_d=data_d,docname = 'Акт Виконаних Робіт')

    if dt == 2:

        # RIGHT SIDE
        sql_dr = """ select a.num,a.nu,a.date_dok,a.doc_descr,ad.tov_name,cast(ad.tov_kolvo as int) as tov_kolvo
                    ,ad.tov_cena,ad.tov_suma
                    from  znakl a
                     inner join actvr avr on avr.num = ?
                     inner join znakl_ ad on ad.pid = a.num
                     where a.dopoln1  =  cast(? as varchar (15))
                     and ad.sklad_id_to = avr.sklad_id"""
        data_dr = db.data_module(sql_dr,[doc_id,doc_id],function_name+'_dt=2 _dr')

        # LEFT SIDE
        sql_dl = """ select a.num,a.nu,a.date_dok,a.doc_descr,ad.tov_name,cast(ad.tov_kolvo as int) as tov_kolvo
                    ,ad.tov_cena,ad.tov_suma
                    from  znakl a
                     inner join actvr avr on avr.num = ?
                     inner join znakl_ ad on ad.pid = a.num
                     where a.dopoln1  =  cast(? as varchar (15))
                     and ad.sklad_id_to =
                     ( select p.param_value from sklad_params p where p.id_type = 4 and p.sklad_id = avr.sklad_id) """

        data_dl = db.data_module(sql_dl,[doc_id,doc_id],function_name+'_dt=2 _dl')
        total_l = 0

        for item in data_dl:
            total_l += item['TOV_SUMA']
        total_r = 0
        for item in data_dr:
            total_r += item['TOV_SUMA']
        return render_template("dispack_doc1.html", title=title, dt=dt, data_dr=data_dr,data_dl=data_dl
                               ,total_l=total_l,total_r=total_r,data_h = data_h[0]

                               ,docname = 'Акт зміни якісного стану')


    # try:
    #     return render_template("dispack_doc1.html", title = title ,dt = dt,data_h = data_h[0],data_d = data_d)
    #     # return render_template("dispack_doc1.html", title=title, dt=dt, data_d = data_d)
    # except Exception as e:
    #     return str(e)