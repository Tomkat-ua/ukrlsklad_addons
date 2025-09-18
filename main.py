import platform
from flask import Flask, render_template
from gevent.pywsgi import WSGIServer
import losses,export,serials,ghist_,config#,sklads
#from proxy_module import get_arrived_history

app = Flask(__name__)

local_ip         = config.local_ip

app.secret_key = config.api_key  # потрібен для flash-повідомлень


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
def ghist():
    return ghist_.index()

@app.route("/ghist_details/<row_id>",methods =['GET','POST'])
def ghist_details(row_id):
    return ghist_.datails(row_id)
# @app.route("/edit/<int:row_id>")

########### SKLADS ###########################
@app.route("/sklad",methods = ['GET','POST'])
def sklad_list():
    return sklads.get_list()

@app.route("/sklad/<int:sklad_id>")
def sklad_details(sklad_id):
    return sklads.sklad_details(sklad_id)

@app.route("/sklad/save", methods=["POST"])
def sklad_save():
    return sklads.sklad_save()

@app.route("/sklad/update", methods=["POST"])
def sklad_update():
    return

########### TEST #############################
@app.route("/test/<doc_id>")
def proxy_arrived(doc_id):
    return get_arrived_history(doc_id)
########### MAIN ##############################################
if __name__ == "__main__":
    if platform.system() == 'Windows':
        http_server = WSGIServer((local_ip,config.server_port), app)
        print(f"Running HTTP-SERVER on port - http://" + local_ip + ':' + str(config.server_port))
    else:
        http_server = WSGIServer(('', int(config.server_port)), app)
        print(f"Running HTTP-SERVER on port :" + str(config.server_port))
    http_server.serve_forever()
