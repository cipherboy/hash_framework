from os.path import expanduser
from multiprocessing import cpu_count


class config:
    base_path = expanduser("~")
    threads = cpu_count()

    results_dir = base_path + "/results"

    # Change during deploy
    psql_host = "localhost"
    psql_user = "hf"
    psql_password = "hash_framework"
    psql_database = "hash_framework"

    job_count = 1
    manager_uri = "http://10.1.30.250:8000"
    scheduler_uri = "http://10.1.30.250:8001"
    gatherer_uri = "http://192.168.1.18:8002"
