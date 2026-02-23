from flask import  request,render_template
from . import db
import sys

title = 'Приход майна'

doc_data = ''

def get_data_list(function_name,search = '%'):
    sql = """select * from usadd_web.pnakl (?) order by DATE_DOK desc, nu desc """
    return db.data_module(sql, [search], function_name)

def get_data_header(docs_id):
    sql = "select * from print_docs.pnakl_doc_header(?)"
    # sql = """select * from pnakl p where p.num = ? """
    return db.data_module(sql,[docs_id])

def get_data_details(docs_id):
    # sql = """select * from pnakl_ p where p.pid in (?) """
    sql = "select * from print_docs.pnakl_doc_details (?)"
    return db.data_module(sql,[str(docs_id)])

def pnakl_list():
    function_name = sys._getframe(0).f_code.co_name
    if request.method == 'GET':
        search = '%'
    else:
        search = request.form.get('search')

    doc_data = get_data_list(function_name,search)
    return  render_template("pnakl_list.html", title='Приход майна',data= doc_data,search=search,pname_1 = '/')



def build_tree(rows):
    tree = {}
    nodes = {row['ID']: {**row, 'children': []} for row in rows}

    root_nodes = []
    for node_id, node in nodes.items():
        parent_id = node.get('PARENT_ID')
        if parent_id and parent_id in nodes:
            nodes[parent_id]['children'].append(node)
        else:
            root_nodes.append(node)
    return root_nodes

def pnakl_docs(docs_id):

    # sql = """select * from print_docs.dot_list_by_doc(?) where blob_id in ( 3,4,8,9) order by 2"""
    # doc_list = db.data_module(sql,[doc_id])
    data_header = get_data_header(docs_id)
    data_details = get_data_details(docs_id)
    # doc_tree = build_tree(doc_list)
    print(data_details)
    return render_template("pnakl_docs.html",
                           title= 'Документи по приходу',
                           # doc_tree = doc_tree,doc_id = doc_id,
                           data_header = data_header[0],
                           data_details = data_details,
                           # doc_list=doc_list
                           )

def get_serials():
    tovar_id = request.args.get('tovar_id')
    doc_id = request.args.get('doc_id')
    #
    # # Робимо точковий запит до БД
    sql = """select ts.tovar_ser_num,ts.tovar_ser_descr
from tovar_serials ts
where ts.doc_type_id = 8
and ts.doc_id =   ?
and ts.tovar_id = ?
"""
    serials = db.data_module(sql, [doc_id, tovar_id])
    return serials


def incoming_page():
    # Отримуємо дані (вони мають бути впорядковані за NU!)
    from itertools import groupby
    search = '%'
    if request.method == 'POST':
        search = request.form.get('search')
    raw_data = get_data_list('incoming_page',search)
    print(raw_data)
    # Групуємо за полем 'NU'
    # groupby повертає (ключ, ітератор_групи)

    # grouped = [(nu, list(items)) for nu, items in groupby(raw_data, lambda x: x['NU'])]

    grouped2 = []
    for nu, items_iter in groupby(raw_data, lambda x: x['NU']):
        items = list(items_iter)

        # Створюємо словник унікальних товарів: {ID: сам_запис}
        # Це залишить лише один (останній) запис для кожного TOVAR_ID
        unique_items_dict = {item['DOC_ID']: item for item in items}
        unique_items_list = list(unique_items_dict.values())

        # Передаємо: номер, всі записи, кількість унікальних, список унікальних об'єктів
        grouped2.append((nu, items, len(unique_items_list), unique_items_list))

    # print(grouped2[0])



    return render_template('incoming.html', grouped_data=grouped2,search=search,list_id='list_id')

