from flask import  request,render_template,flash,redirect, url_for
from . import db


def catalog_list(search_name,mode):
    # 1. Отримуємо довідник усіх тегів для майбутнього вибору
    sql = "SELECT TT.NUM AS TAG_ID, TT.VALUE_ FROM TOVAR_TAGS TT ORDER BY TT.VALUE_"
    con = db.get_connection()
    cur = con.cursor()
    cur.execute(sql)
    all_tags = [dict(zip([col[0] for col in cur.description], row)) for row in cur.fetchall()]

    selected_tag_ids_raw = request.args.get('tags', '')
    selected_tag_ids = [int(tid) for tid in selected_tag_ids_raw.split(',') if tid.isdigit()]
    if selected_tag_ids:
        placeholders = ', '.join(['?'] * len(selected_tag_ids))
        query = f"""
                    WITH MATCHED_TOVARS AS (
                        SELECT TL.TOVAR_ID
                        FROM TOVAR_TAGS_LINK TL
                        WHERE TL.TAG_ID IN ({placeholders}) 
                        GROUP BY TL.TOVAR_ID
                        HAVING COUNT(DISTINCT TL.TAG_ID) = ?
                    )
                    select TN.NUM, coalesce(TN.KOD,'-') as KOD,     TN.NAME as NAME_US,
                           coalesce(M.NAME_SHORT  ,'-- не визначено --')    as SLID_SHORT_NAME,
                           coalesce(M.NAME_LONG   ,'-- не визначено --')    as SLID_LONG_NAME, TN.ED_IZM, TN.CENA,
                           z.kolvo  as zal_kolvo  ,cast( list(t.value_,',') as varchar(255))as tag_list
                    from MATCHED_TOVARS mt
                        inner join TOVAR_NAME tn on tn.num = mt.TOVAR_ID
                        left  join SLID_MATERIALS M on M.MATERIAL = TN.KOD
                        inner join tovar_zal z on z.tovar_id = tn.num  and z.sklad_id = 300000001
                        left  join tovar_tags_link l on l.tovar_id = tn.num
                        left  join tovar_tags      t on t.num = l.tag_id
                    where tn.visible = 1
                    --and (:TN_NAME is null or (TN.NAME like :TN_NAME) or ( TN.kod  like :TN_name ))
                    group by NUM,KOD,NAME_US,SLID_SHORT_NAME,SLID_LONG_NAME,ED_IZM,
                             CENA,ZAL_KOLVO
                    order by TN.NAME
                """

        params = selected_tag_ids + [len(selected_tag_ids)]
        cur.execute(query, params)
    else:
        query = """   select TN.NUM, coalesce(TN.KOD, '-') as KOD, TN.NAME as NAME_US,
                       coalesce(M.NAME_SHORT, '-- не визначено --') as SLID_SHORT_NAME,
                       coalesce(M.NAME_LONG,  '-- не визначено --') as SLID_LONG_NAME, 
                       TN.ED_IZM, TN.CENA,z.kolvo  as zal_kolvo
                       ,cast( list(t.value_,',') as varchar(1000) ) as tag_list
                from TOVAR_NAME TN
                    left join SLID_MATERIALS M on M.MATERIAL = TN.KOD
                    inner join tovar_zal z on z.tovar_id = tn.num  and z.sklad_id = 300000001
                    left join tovar_tags_link l on l.tovar_id = tn.num
                    left join tovar_tags      t on t.num = l.tag_id
                where tn.visible = 1
                    --and (? is null or (TN.NAME like ?) or ( TN.kod  like ? ))
                group by NUM,KOD,NAME_US,SLID_SHORT_NAME,SLID_LONG_NAME,ED_IZM,CENA,ZAL_KOLVO    
                order by TN.NAME
          """
        cur.execute(query)
    columns = [col[0] for col in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    con.close()
    #------------------------------------------
    if mode == 'web':
        return render_template(
            'catalog.html',
            ROWS=rows,
            ALL_TAGS=all_tags,
            SELECTED_TAG_IDS=selected_tag_ids,
            title='Каталог товарів'
        )
    if mode == 'api':
        return rows
    else:
        return 'Mode ERROR'
