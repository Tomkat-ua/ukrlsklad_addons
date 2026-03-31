from . import db
from flask import  request, redirect, flash,render_template,url_for,jsonify#,render_template_string
#import pandas as pd

def get_list():
    # sql_master = """ select NUM,NAME from sklad_parents"""
    # sql_datail = """ select sn.num,sn.visible,sn.name  as sklad_name,pd.parent_id,sp.name as parent_name
    #                 from sklad_parents_det pd
    #                     inner join sklad_names sn on sn.num = pd.sklad_id
    #                         and sn.firma_id = 170
    #                     inner join sklad_parents sp on sp.num = pd.parent_id
    #                      """
    sql = """ select
        sn.num,sn.name as sklad_name,sn.visible
        ,sp.name as parent,spd.parent_id
        from sklad_names sn
            left join sklad_parents_det spd on spd.sklad_id = sn.num
            left join sklad_parents sp on sp.num = spd.parent_id
        where sn.firma_id = 170
        order by sn.name """
    sql_parents  = "select NUM,NAME from sklad_parents "
    data_parents = db.data_module(sql_parents,[])
    data = db.data_module(sql,[])
    return  render_template("sklads_.html"
                            ,data=data
                            ,data_parents=data_parents
                            ,title = 'Довідник складів (підрозділів)')


def sklad_save():
    # Отримуємо дані з форми
    sklad_id = request.form.get('sklad_id')
    sklad_name = request.form.get('sklad_name')
    parent_id = request.form.get('parent_id')
    is_visible = 1 if request.form.get('is_visible') else 0
    p_id_to_db = int(parent_id) if parent_id and parent_id.isdigit() else None
    if not sklad_id:
        # ЛОГІКА ВСТАВКИ (Твій новий блок)
        sql = """
            execute block (
                p_id tnum = ?,
                s_name varchar(50) = ?,
                is_vis int = ?
            ) as 
            declare variable new_id tnum;
            begin
                new_id = gen_id(gen_sklad_names_id, 1);

                insert into sklad_names (num, name, visible, firma_id)
                values (:new_id, :s_name, :is_vis, 170);

                if (:p_id is not null) then
                    insert into sklad_parents_det (sklad_id, parent_id)
                    values (:new_id, :p_id);
            end
            """
        params = (p_id_to_db, sklad_name, is_visible)
    else:
    # SQL Блок: імена в дужках і в тілі МАЮТЬ збігатися
        sql = """
        execute block (
            sid tnum = ?,
            pid tnum = ?,
            sname varchar(50) = ?,
            vis int = ?
        ) as begin
            -- Використовуємо :sid, :sname, :vis (ті ж імена, що в дужках вище)
            update sklad_names s set
                s.name = :sname,
                s.visible = :vis
            where s.num = :sid;
    
            -- Оновлюємо підрозділ
            delete from sklad_parents_det where sklad_id = :sid;
    
            if (:pid is not null ) then
                insert into sklad_parents_det (sklad_id, parent_id)
                values (:sid, :pid);
        end
        """

        # Важливо: порядок у кортежі має точно відповідати порядку знаків '?' у блоці
        params = (
            sklad_id,  # піде в sid
            parent_id if parent_id else None,  # піде в pid
            sklad_name,  # піде в sname
            is_visible  # піде в vis
        )

    try:
        con = db.get_connection()
        cur = con.cursor()
        cur.execute(sql, params)
        con.commit()
        return redirect(url_for('sklad_list'))
    except Exception as e:
        con.rollback()
        return f"Помилка при збереженні: {str(e)}", 500