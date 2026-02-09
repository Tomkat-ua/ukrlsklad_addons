from flask import  request,render_template
from . import db
import sys

title = 'Приход майна'

doc_data = ''

def get_data_list(function_name,search = '%'):
    sql = """select p.num as doc_id 
            ,p.nu
            ,p.date_dok
            ,p.client 
            ,p.p_nu
            ,utils.datetostr( p.p_date_dok)  as p_date_dok
            ,pd.pid
            ,pd.tovar_id
            ,pd.tov_name
            ,cast (pd.tov_kolvo as int) as   tov_kolvo
            ,pd.tov_cena
            ,tn.kod as tov_code
            ,p.article_id
            ,a.a_name
            from pnakl_ pd
                inner join pnakl p on p.num = pd.pid
                inner join tovar_name tn on tn.num = pd.tovar_id
                inner join article_types a on a.num = p.article_id
            where pd.tov_name like ?
            order by p.num desc  """
    return db.data_module(sql, [search], function_name)

def get_data_header(doc_id):
    sql = 'select * from pnakl p where p.num = ? '
    return db.data_module(sql,[doc_id])

def get_data_details(doc_id):
    sql = ("""select *
            from pnakl_ p where p.pid = ? """)
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
    sql = """select * from print_docs.dot_list_by_doc(?) where blob_id in ( 3,4) order by 2"""
    doc_list = db.data_module(sql,[doc_id])
    data_header = get_data_header(doc_id)
    data_details = get_data_details(doc_id)

    doc_tree = build_tree(doc_list)

    return render_template("pnakl_docs.html",
                           title= 'Документи по приходу',
                           doc_tree = doc_tree,doc_id = doc_id,
                           data_header = data_header[0],
                           data_details = data_details,
                           doc_list=doc_list)

