from flask import  request,render_template
from . import db
import sys

title = 'Приход майна'

doc_data = ''

def get_data_list(function_name,search = '%'):
    sql = """select * from usadd_web.pnakl (?) order by DATE_DOK desc, nu desc """
    return db.data_module(sql, [search], function_name)

def get_data_header(doc_id):
    sql = """select * from pnakl p where p.num = ? """
    return db.data_module(sql,[doc_id])

def get_data_details(doc_id):
    sql = ("""select * from pnakl_ p where p.pid = ? """)
    return db.data_module(sql,[doc_id])

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

def pnakl_docs(doc_id):
    # sql = ("""select t.id,t.PARENT_ID,t.name , t.tmpl_type
    #           from doc_print_tmpl t where t.doc_type = 8  """)
    sql = """select * from print_docs.dot_list_by_doc(?) where blob_id in ( 3,4,8,9) order by 2"""
    doc_list = db.data_module(sql,[doc_id])
    # for doc in doc_list:
    #     print(doc)

    data_header = get_data_header(doc_id)
    data_details = get_data_details(doc_id)

    doc_tree = build_tree(doc_list)

    return render_template("pnakl_docs.html",
                           title= 'Документи по приходу',
                           doc_tree = doc_tree,doc_id = doc_id,
                           data_header = data_header[0],
                           data_details = data_details,
                           doc_list=doc_list)

def incoming_page():
    # Отримуємо дані (вони мають бути впорядковані за NU!)
    from itertools import groupby
    search = '%'
    if request.method == 'POST':
        search = request.form.get('search')
    raw_data = get_data_list('incoming_page',search)

    # Групуємо за полем 'NU'
    # groupby повертає (ключ, ітератор_групи)
    # gr = groupby(raw_data, lambda x: x['NU'])
    # print(gr[0])
    # for g, items in gr:
    #     print ('group:',g)
    #     print(list(items))
        # for item in items:
        #     print(item['DOC_ID'])

    grouped = [(nu, list(items)) for nu, items in groupby(raw_data, lambda x: x['NU'])]

    grouped2 = []
    for nu, items_iter in groupby(raw_data, lambda x: x['NU']):
        items = list(items_iter)

        # Створюємо словник унікальних товарів: {ID: сам_запис}
        # Це залишить лише один (останній) запис для кожного TOVAR_ID
        unique_items_dict = {item['DOC_ID']: item for item in items}
        unique_items_list = list(unique_items_dict.values())

        # Передаємо: номер, всі записи, кількість унікальних, список унікальних об'єктів
        grouped2.append((nu, items, len(unique_items_list), unique_items_list))

    for a,b,c,d in grouped2:
        print(d)
        # print(list(id['DOC_ID'] for id in d))
        # for id in d:
        #     print(id['DOC_ID'])

    return render_template('incoming.html', grouped_data=grouped,search=search)

#
# def incoming_page():
#     from itertools import groupby
#     search = '%'
#     if request.method == 'POST':
#         search = request.form.get('search')
#
#     raw_data = get_data_list('incoming_page', search)
#
#     # Додаємо обчислення унікальних ID прямо тут
#     grouped = [
#         (nu, list(items), len({item['DOC_ID'] for item in items}))
#         for nu, items in groupby(raw_data, lambda x: x['NU'])
#     ]
#
#     return render_template('incoming.html', grouped_data=grouped, search=search)