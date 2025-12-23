import os
from dotenv import load_dotenv

load_dotenv()

server_port = 3001
api_key =  os.getenv('API_KEY')
env = os.getenv('ENV','DEV')
app_version = os.getenv('APP_VERSION')
db_server = os.getenv("DB_HOST")
db_port = int(os.getenv("DB_PORT"))
db_path = os.getenv("DB_PATH")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
local_ip = os.getenv('LOCAL_IP')
debug_mode = int(os.getenv('DEBUG_MODE',1))