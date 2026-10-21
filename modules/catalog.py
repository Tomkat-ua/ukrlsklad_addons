from flask import  request,render_template,flash,redirect, url_for
from . import db


def catalog_list(search_name,mode):
    sql = """ select TN.NUM, coalesce(TN.KOD, '-') as KOD, TN.NAME as NAME_US,
                       coalesce(M.NAME_SHORT, '-- не визначено --') as SLID_SHORT_NAME,
                       coalesce(M.NAME_LONG,  '-- не визначено --') as SLID_LONG_NAME, 
                       TN.ED_IZM, TN.CENA,z.kolvo  as zal_kolvo
                from TOVAR_NAME TN
                    left join SLID_MATERIALS M on M.MATERIAL = TN.KOD
                    inner join tovar_zal z on z.tovar_id = tn.num  and z.sklad_id = 300000001
                where tn.visible = 1
                and (? is null or (TN.NAME like ?) or ( TN.kod  like ? ))
                order by TN.NAME
                    """
    if search_name:
        search_name = '%'+search_name+'%'
    data = db.data_module(sql,[search_name,search_name,search_name])
    if mode == 'web':
        return render_template('catalog.html'
                           ,ROWS=data
                           ,title='Каталог товарів')
    if mode == 'api':
        return data
    else:
        return 'Mode ERROR'
