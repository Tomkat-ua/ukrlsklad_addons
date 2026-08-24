from flask import  request,render_template,jsonify
import sys
import re
from . import db

def api_materials():
    try:
        q = request.args.get('q', '').strip()

        # 1. ЗАХИСТ ВІД %%%: вирізаємо спецсимволи і перевіряємо чи є хоча б 2 реальні літери/цифри
        clean_text = re.sub(r'[%_\s]', '', q)
        if len(clean_text) < 2:
            return jsonify([])

        # 2. ЖОДНОЇ САМОДІЯЛЬНОСТІ: передаємо `q` в SQL точно так, як ввів юзер.
        # Ввів 'акб'   -> шукає ТОЧНО 'акб'
        # Ввів 'акб%'  -> шукає все, що ПОЧИНАЄТЬСЯ на 'акб'
        # Ввів '%акб%' -> шукає все, що МІСТИТЬ 'акб'
        search_param = q

        # 4. Виконуємо запит (ОБОВ'ЯЗКОВО з обмеженням FIRST 50 або FIRST 100)
        sql = """
                SELECT  *
                FROM SLID_MATERIALS
                WHERE 
                    NAME_SHORT LIKE ? OR MATERIAL LIKE ?  or name_long like ?
                ORDER BY ID DESC
            """

        data = db.data_module(sql, [ search_param,search_param,search_param])
        return data

    except Exception as e:
            print(f"❌ Помилка БД: {e}")
            return jsonify({'error': str(e)}), 500

def materials_list():
    return render_template("materials-list.html", title='Довідник матеріалів')

