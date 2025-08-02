import platform
from flask import Flask, render_template
from gevent.pywsgi import WSGIServer
import os,losses,export,serials,ghist,db
# from test import gnum

local_ip         = os.getenv('LOCAL_IP','192.168.10.9')
server_port      = os.getenv('SERVER_PORT',3001)
app = Flask(__name__)
app.secret_key = '435343ku4vjjq3eqhdeql3545345ts2cgvfkdc'  # потрібен для flash-повідомлень


########## MAIN ####################
@app.context_processor
def inject_globals():
    dsn = db.db_server + '/' + str(db.db_port) + ':' + db.db_path
    return {
        'version': 'v0.0.2.100',
        'appname': 'UkrSklad Addons App',
        'dsn': dsn
    }

@app.route('/')
def index():
    return render_template('index.html')

############# LOSSES ######################################
@app.route('/losses', methods=['GET', 'POST'])
def losses_list():
    return losses.losses_list()

@app.route("/lost_add", methods=["GET", "POST"])
def loss_add():
    return losses.loss_add()

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
def ghist_search():
    return ghist.main_view()

@app.route("/ghist_find",methods =['GET','POST'])
def ghist_find():
    return ghist.find()

########### MAIN ##############################################
if __name__ == "__main__":
    if platform.system() == 'Windows':
        http_server = WSGIServer((local_ip, int(server_port)), app)
        print(f"Running HTTP-SERVER on port - http://" + local_ip + ':' + str(server_port))
    else:
        http_server = WSGIServer(('', int(server_port)), app)
        print(f"Running HTTP-SERVER on port :" + str(server_port))
    http_server.serve_forever()
