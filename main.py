import platform
from version import __version__
from flask import Flask, render_template,request
from gevent.pywsgi import WSGIServer
from modules import serials,  mnakl, losses_nn, ghist_, pnakl, reports, snakl, config, products, packs, losses, dispack
from modules import aruns
#from modules import aruns,doc_tmpl,orders_od,sklads
#from modules import pivot,export,stat
from modules import db
app = Flask(__name__)

local_ip         = config.local_ip

app.secret_key = config.api_key  # потрібен для flash-повідомлень


# Глобальна змінна (завантажується один раз при старті сервера)

GLOBAL_MENU = db.data_module("SELECT * FROM WEB_MENU where env containing ? ORDER BY ORD", [config.env])
# config.env

@app.context_processor
def inject_menu():
    return dict(sidebar_menu=get_menu_tree())


def get_menu_tree():
    # 1. Отримуємо всі пункти з БД
    raw_menu = GLOBAL_MENU#db.data_module("SELECT ID, PARENT_ID, NAME, URL, ICON, ORD FROM WEB_MENU ORDER BY ORD", [])

    menu_tree = []
    # Створюємо допоміжний словник для швидкого пошуку за ID
    nodes = {item['ID']: {**item, 'children': []} for item in raw_menu}

    for item in raw_menu:
        node = nodes[item['ID']]
        parent_id = item['PARENT_ID']

        if parent_id is None or parent_id == '' or parent_id == 0:
            # Це корінь (пункт першого рівня)
            menu_tree.append(node)
        else:
            # Це підпункт — додаємо його в 'children' відповідного батька
            if parent_id in nodes:
                nodes[parent_id]['children'].append(node)

    return menu_tree


@app.errorhandler(404)
def page_not_found(e):
    # Можна повернути шаблон render_template('404.html')
    return "<h3>Ой! Такої сторінки не існує (404)</h3>", 404


@app.errorhandler(500)
def internal_server_error(e):
    # 1. Спробуємо отримати оригінальну помилку Python
    # Якщо це сталось через код, там буде об'єкт Exception
    original_err = getattr(e, "original_exception", None)

    if original_err:
        error_text = f"{type(original_err).__name__}: {original_err}"
    else:
        # Якщо Flask просто видав 500 без Exception (наприклад, через abort(500))
        error_text = str(e)

    # 2. Формуємо відповідь
    return f"""
    <div style="background-color: #fff5f5; color: #c53030; padding: 20px; border: 2px solid #feb2b2; border-radius: 8px; font-family: sans-serif;">
        <h2 style="margin-top: 0;">❌ На сервері щось зламалось</h2>
        <p style="font-size: 1.1em;"><strong>Текст помилки:</strong></p>
        <div style="background: white; padding: 10px; border: 1px solid #fed7d7; font-family: monospace; font-size: 14px; margin-bottom: 20px;">
            {error_text}
        </div>
        <p><strong>URL:</strong> {request.url}</p>
        <hr style="border: 0; border-top: 1px solid #feb2b2;">
        <p><em>Ми вже ремонтуємо !!! (Або просто подивіться рядок коду вище ☝️)</em></p>
    </div>
    """, 500


@app.template_filter('currency_format_ua')
def format_currency_ua(value, decimal_places=2):
    """
    Форматує число:
    1. Використовує крапку для тисяч, крапку для десятих (стандарт f-рядок).
    2. Замінює роздільник тисяч (,) на пробіл ( ).
    3. Замінює десятковий роздільник (.) на кому (,).
    """
    try:
        # 1. Форматування Python: 12,608.33
        # Використовуємо :,.{decimal_places}f
        formatted_str = f"{value:,.{decimal_places}f}"
        # 2. 🌟 Заміна роздільника тисяч (,) на пробіл
        thousand_separated = formatted_str.replace(",", " ")
        #thousand_separated = formatted_str.replace(",", "")
        # 3. 🌟 Заміна десяткового роздільника (.) на кому
        return thousand_separated.replace(".", ",")
    except Exception:
        return value  # Повернути вихідне значення у разі помилки


@app.context_processor
def inject_global_vars():
    # Цей словник тепер буде доступний у ВСІХ шаблонах автоматично
    return dict(
        mark_colors={
            1: 'table-success',
            6: 'table-warning',
            3: 'table-danger',
            4: 'table-info'
        }
    )

########## MAIN ####################
@app.context_processor
def inject_globals():
    dsn = str(config.db_server) + '/' + str(config.db_port) + ':' + str(config.db_path)
    return {
        'version': __version__,
        'appname': 'UkrSklad Addons App',
        'dsn': dsn,
        'env': config.env
    }

@app.route('/')
def index():
    return render_template('index.html',title= "Головна")

############# LOSSES ######################################
@app.route('/losses', methods=['GET', 'POST'])
def losses_list():
    return losses.loss_list()

@app.route("/lost_add", methods=["GET", "POST"])
def loss_add():
    return losses.loss_add()

@app.route("/loss_edit/<int:id>", methods=["GET", "POST"])
def loss_edit(id):
    return losses.loss_edit(id)

@app.route("/losses-nn",methods=['GET', 'POST'])
def losses_list_nn():
    return losses_nn.losses_list()

############ EXPORT ########################################
# @app.route("/export")
# def export_csv():
#     return export.export_csv()

########### SERIAL#############################################
@app.route("/serials",methods=['GET', 'POST'])
def serials_search():
    return serials.serials_search()

########### G_HIST ############################################
@app.route("/ghist",methods =['GET','POST'])
def ghist_list():
    return ghist_.index()

@app.route("/ghist_details/<row_id>",methods =['GET','POST'])
def ghist_details(row_id):
    return ghist_.datails(row_id)
# @app.route("/edit/<int:row_id>")

########### SKLADS ###########################
@app.route("/sklads",methods = ['GET','POST'])
def sklad_list():
    return sklads.get_list()

@app.route('/sklad_save', methods=['POST'])
def sklad_save():
    return sklads.sklad_save()
#
# @app.route("/sklad/<int:sklad_id>")
# def sklad_details(sklad_id):
#     return sklads.sklad_details(sklad_id)
#
# @app.route("/sklad/save", methods=["POST"])
# def sklad_save():
#     return sklads.sklad_save()
#
# @app.route("/sklad/update", methods=["POST"])
# def sklad_update():
#     return

############ REPORTS #########################
@app.route("/reports",methods = ['GET','POST'])
def reports_list():
    return reports.reports_list()
# @app.route("/reports/<int:report_id>",methods = ['GET','POST'])
# def report(report_id):
#     return reports.report(report_id)

@app.route('/reports2/<int:rep_id>', methods=['GET','POST'])
def reports_list2(rep_id):
    return reports.reports_list2(rep_id)

########### DISPAKING ########################
@app.route('/dispack', methods=['GET','POST'])
def dispack_list():
    return dispack.dispack_list()
@app.route('/dispack/doc1/<int:doc_id>', methods=['GET','POST'])
def dispack_doc1(doc_id):
    return dispack.doc(doc_id, 1)
@app.route('/dispack/doc2/<int:doc_id>', methods=['GET','POST'])
def dispack_doc2(doc_id):
    return dispack.doc(doc_id, 2)
@app.route('/dispack/add', methods=['GET','POST'])
def dispack_add():
    return dispack.add()
@app.route('/process_disacc/<int:id>', methods=['POST'])
def dispack_disacc(id):
    return dispack.process_disacc(id)

########### ORDERS_OD ########################
@app.route('/orders-od')
def order_od_list():
    return orders_od.orders_list()
########### ARUNS ############################
@app.route('/aruns')
def aruns_l():
    return aruns.aruns_list()
########### PNAKL ############################
@app.route('/pnakl',methods = ['GET','POST'])
def pnakl_list():
    return pnakl.pnakl_list()

#друк документи по приходу - list
@app.route('/pnakl/docs')
def print_pnakl_docs():
    list_id = request.args.get('list_id')
    return pnakl.pnakl_docs(list_id)

#друк документи по приходу - single
@app.route('/docs/<int:dot_id>/<int:docs_id>/<int:tovar_id>')
def print_docs(dot_id,docs_id,tovar_id):
    name = request.args.get('name')
    return doc_tmpl.print_full_report(dot_id,docs_id,tovar_id,name)
########### MNAKL ############################
@app.route('/mnakl',methods = ['GET','POST'])
def mnakl_list():
    return mnakl.mnakl_list()

########### SNAKL ############################
@app.route('/snakl',methods = ['GET','POST'])
def snakl_list():
    return snakl.snakl_list()
@app.route('/snakl/<int:id>',methods = ['GET','POST'])
def snakl_det(id):
    return snakl.snakl_det(id)

########### PACKS ############################
@app.route('/packs',methods=['GET', 'POST'])
def packs_list():
    print(request.method)
    if request.method == 'GET':
        return packs.packs_get()
    if request.method == 'POST':
        return packs.packs_post()
@app.route('/packs_details/<int:master_id>')
def packs_det(master_id):
    return packs.get_details(master_id)

########### SERIALS CHECK ####################
@app.route('/scheck',methods=['GET','POST'])
def serial_scheck():
    return serials.serials_check()

@app.route('/add-to-actvr', methods=['POST'])
def run_1():
    return serials.add_to_actv()
#############################################################################################
########### TEST #############################
from itertools import groupby


@app.route('/incoming',methods = ['GET','POST'])
def incoming():
    return pnakl.incoming_page()


@app.route('/get_serials')
def get_serials():
    return pnakl.get_serials()



@app.route('/products',methods = ['GET','POST'])
def products_list():
    return products.products_tab()
@app.route('/product_img/<int:tovar_id>',methods = ['GET','POST'])
def product_img(tovar_id):
    return products.products_img(tovar_id)
@app.route('/product_img_upload/<int:tovar_id>', methods=['POST'])
def product_upload_image(tovar_id):
    return products.upload_image(tovar_id)
@app.route('/product_img_delete/<int:tovar_id>', methods=['POST'])
def product_delete_image(tovar_id):
    return products.delete_image(tovar_id)

########### MAIN ##############################################
if __name__ == "__main__":
    if platform.system() == 'Windows':
        http_server = WSGIServer((local_ip, config.server_port), app)
        print(f"Running HTTP-SERVER on port - http://" + local_ip + ':' + str(config.server_port))
    else:
        http_server = WSGIServer(('', int(config.server_port)), app)
        print(f"Running HTTP-SERVER on port :" + str(config.server_port))
    http_server.serve_forever()
