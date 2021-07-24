from database.db import Database
from k8s.k8s import Kube
from server.server import *
import os

server_config = {
    "host": "localhost",
    "port": 8080
}

db_config = {
    "host": "localhost",
    "db_name": "ulti",
    "user": "postgres",
    "password": f"{os.environ['db_pass']}"
}

kube = Kube()
db_client = Database(db_config, kube.apis_api)
db_client.check_conn()
db_client.create_tables()

namespace_list = kube.get_namespaces()

db_client.insert_namespace(namespace_list)
db_client.insert_deployments(namespace_list)

conn = db_client.db_connect()

run_server(conn, server_config.get('port'), server_config.get('host'))


