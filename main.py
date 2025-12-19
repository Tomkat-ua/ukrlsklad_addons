import platform
from flask import Flask, render_template
from gevent.pywsgi import WSGIServer
import losses,export,serials,ghist_,config,reports,dispack,losses_nn,pnakl,mnakl,snakl,products

app = Flask(__name__)

local_ip         = config.local_ip

app.secret_key = config.api_key  # потрібен для flash-повідомлень

@app.errorhandler(404)
def page_not_found(e):
    # Можна повернути шаблон render_template('404.html')
    return "<h3>Ой! Такої сторінки не існує (404)</h3>", 404

@app.errorhandler(500)
def internal_server_error(e):
    return "<h3>На сервері щось зламалось. Ми вже чинимо! (500)</h3>", 500


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
        # 3. 🌟 Заміна десяткового роздільника (.) на кому
        return thousand_separated.replace(".", ",")

    except Exception:
        return value  # Повернути вихідне значення у разі помилки

########## MAIN ####################
@app.context_processor
def inject_globals():
    dsn =  str(config.db_server) + '/' + str(config.db_port)+ ':' + str(config.db_path)
    return {
        'version': config.app_version,
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
@app.route("/export")
def export_csv():
    return export.export_csv()

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
# @app.route("/sklad",methods = ['GET','POST'])
# def sklad_list():
#     return sklads.get_list()
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
    return dispack.doc(doc_id,1)
@app.route('/dispack/doc2/<int:doc_id>', methods=['GET','POST'])
def dispack_doc2(doc_id):
    return dispack.doc(doc_id,2)
@app.route('/dispack/add', methods=['GET','POST'])
def dispack_add():
    return dispack.add()
@app.route('/process_disacc/<int:id>', methods=['POST'])
def dispack_disacc(id):
    return dispack.process_disacc(id)

########### PNAKL ############################
@app.route('/pnakl',methods = ['GET','POST'])
def pnakl_list():
    return pnakl.pnakl_list()

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
########### TEST #############################
@app.route("/test")
def test():
    return render_template('test.html')

# @app.route('/pdf')
# def generate_pdf():
#     return to_pdf.generate_pdf()

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
        http_server = WSGIServer((local_ip,config.server_port), app)
        print(f"Running HTTP-SERVER on port - http://" + local_ip + ':' + str(config.server_port))
    else:
        http_server = WSGIServer(('', int(config.server_port)), app)
        print(f"Running HTTP-SERVER on port :" + str(config.server_port))
    http_server.serve_forever()
