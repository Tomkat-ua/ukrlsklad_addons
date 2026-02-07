from flask import send_file
from . import db
from docxtpl import DocxTemplate
import io,math
from docx import Document
from datetime import datetime

now = datetime.now()

def format_currency(value):
    if value is None:
        return "0,00"
    # Форматуємо: 2 знаки після коми, замінюємо крапку на кому
    return "{:.2f}".format(float(value)).replace('.', ',')

def get_blob(dot_id):
    sql = " select t.tmpl_blob ,t.name  from doc_print_tmpl t where t.id = ? "
    data_raw = db.data_module(sql,[dot_id])
    return data_raw

def get_header(doc_id):
    sql = "select * from print_docs.pnakl_doc_header(?) "
    data = db.data_module(sql, [doc_id])
    return data

def get_datails(doc_id):
    sql ="select * from print_docs.pnakl_doc_details(?)"
    data = db.data_module(sql, [doc_id])
    return data

def get_serials(doc_id,tovar_id):
    sql = "select ts.tovar_ser_num  as serial from tovar_serials ts where ts.doc_id  = ? and  ts.tovar_id = ? "
    data = db.data_module(sql, [doc_id,tovar_id])
    return data


def get_template_tags(blob_template):
    # Завантажуємо файл у пам'ять
    doc = Document(io.BytesIO(blob_template))
    # Отримуємо стандартні властивості
    props = doc.core_properties
    # props.keywords — це і є ваше поле "Теги"
    tags = props.keywords if props.keywords else ""
    return tags

#### основна процедура звіту #########################################
def print_full_report(dot_id,doc_id):
    blob_data = get_blob(dot_id)
    blob_template = blob_data[0]['TMPL_BLOB']
    blob_name = blob_data[0]['NAME']
    template_tags = get_template_tags(blob_template)
    data_header = get_header(doc_id)
    data_list =  get_datails(doc_id)
    header_info = data_header[0]
    #------------------------------------------------------------------
    print(blob_name)
    # Визначаємо, чи не  додаток з серійниками це раптом ? ------------
    if "MODE_APPEND" in template_tags:
        print("Це додаток !!! ")
        # визначаємо кількісь колонок для списку серійників #
        if "COLS_" in template_tags:
            # Витягуємо число після COLS_
            import re
            match = re.search(r'COLS_(\d+)', template_tags)
            num_cols = int(match.group(1)) if match else 4
        else:
            num_cols = 4  # Стандартно
        print("формуємо додаток з номерами")
        doc = print_appendix(blob_template,doc_id,300000035,num_cols)
        return save_to_browser(doc,doc_id,blob_name)


    for item in data_list:
        # Створюємо нове поле для відображення
        item['TOV_CENA_FMT'] = format_currency(item.get('TOV_CENA'))
        item['TOV_SUMA_FMT'] = format_currency(item.get('TOV_SUMA'))

    TS = sum(float(item.get("TOV_SUMA")  or 0) for item in data_list)
    TC = sum(int(item.get("TOV_KOLVO")   or 0) for item in data_list)

    #  Завантажуємо шаблон
    doc = DocxTemplate(io.BytesIO(blob_template))
    #  Формуємо повний контекст
    context = {
        # Статичні поля заголовка
        "year1": now.year,
        "place": header_info.get("ADR_UR"),
        "firm_name": header_info.get("FIRM_NAME"),
        "date_b": header_info.get("DATE_DOK"),
        "date_e": header_info.get("DATE_DOK"),
        "client": header_info.get("CLIENT"),
        "cl_dd": header_info.get("CL_DATE_DOK"),
        "cl_nu": header_info.get("CL_NU"),
        "doc_type": header_info.get("DOC_TYPE"),

        # ДИНАМІЧНИЙ СПИСОК (той самий 'items', що в циклі {% for %})
        "items": data_list,

        # ПІДСУМОК (рахуємо суму всіх TOV_SUMA у списку)
        # "TC": len(data_list),
        # "TC": sum(int(item.get("TOV_KOLVO")  or 0) for item in data_list),
        # "GT": sum(float(item.get("TOV_SUMA") or 0) for item in data_list)
        "TC": TC,
        "GT": format_currency(TS)
    }

    # 4. Магія рендерингу
    doc.render(context)
    return save_to_browser(doc,doc_id,blob_name)

def chunker_vertical(data_list, cols, field_name):
    total = len(data_list)
    # 1. Рахуємо кількість необхідних рядків
    rows = math.ceil(total / cols)

    # 2. Створюємо список об'єктів з індексами
    indexed_list = [
        {"idx": i + 1, "val": item.get(field_name, '')}
        for i, item in enumerate(data_list)
    ]

    # 3. Дозаповнюємо список пустими елементами до повної матриці
    target_total = rows * cols
    indexed_list.extend([{"idx": "", "val": ""}] * (target_total - total))

    # 4. Формуємо матрицю так, щоб індекси йшли вниз по колонках
    final_matrix = []
    for r in range(rows):
        new_row = []
        for c in range(cols):
            # Вибираємо елемент, який має бути в цьому рядку r і колонці c
            new_row.append(indexed_list[r + c * rows])
        final_matrix.append(new_row)

    return final_matrix



# Припустимо, змінна 'doc' — це об'єкт DocxTemplate, який ми вже заповнили (render)
def save_to_browser(doc, doc_id,doc_name):
    # 1. Створюємо буфер у пам'яті
    buffer = io.BytesIO()

    # 2. Зберігаємо документ у цей буфер
    doc.save(buffer)

    # 3. Перемотуємо буфер на початок (важливо!)
    buffer.seek(0)

    # 4. Відправляємо клієнту
    custom_filename = f"{doc_name}_{doc_id}.docx"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=custom_filename, # Браузер підставить це ім'я в вікно збереження
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )


def print_appendix(blob_template ,doc_id , tovar_id ,num_cols ):
    serials = get_serials(doc_id,tovar_id)
    doc = DocxTemplate(io.BytesIO(blob_template))
    context= { 'sn_rows': chunker_vertical(serials, num_cols,'SERIAL') }
    doc.render(context)
    return doc

#
# def chunker(data_list, size, field_name):
#     # 1. Витягуємо тільки значення потрібного поля
#     # Якщо поля немає, ставимо порожній рядок
#     flat_list = [item.get(field_name, '') for item in data_list]
#
#     # 2. Розбиваємо на групи (чанки)
#     chunks = [flat_list[pos:pos + size] for pos in range(0, len(flat_list), size)]
#
#     # 3. Дозаповнюємо останній рядок порожніми клітинками для симетрії таблиці
#     if chunks and len(chunks[-1]) < size:
#         chunks[-1].extend([''] * (size - len(chunks[-1])))
#
#     return chunks

# def chunker_with_index(data_list, size, field_name):
#     # 1. Створюємо список об'єктів з індексами: [{"idx": 1, "val": "SN001"}, ...]
#     indexed_list = [
#         {"idx": i + 1, "val": item.get(field_name, '')}
#         for i, item in enumerate(data_list)
#     ]
#
#     # 2. Розбиваємо на чанки по 4
#     chunks = [indexed_list[pos:pos + size] for pos in range(0, len(indexed_list), size)]
#
#     # 3. Дозаповнюємо останній рядок порожніми елементами
#     if chunks and len(chunks[-1]) < size:
#         chunks[-1].extend([{"idx": "", "val": ""}] * (size - len(chunks[-1])))
#
#     return chunks