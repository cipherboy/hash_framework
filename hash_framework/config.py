from os.path import expanduser

class config:
    base_path = expanduser("~")
    threads = 1

    tools = base_path + "/tools"

    cms_bin = tools + "/cryptominisat5"
    cms_args = []

    bc_bin = tools + "/bc2cnf"
    bc_args = ["-nots", "-nocoi", "-nosimplify"]

    model_dir = base_path + "/models"
    cache_dir = base_path + "/kernel_cache"
    sat_dir = base_path + "/sats"

    results_dir = base_path + "/results"

    default_adder = [{"chaining": None, "type": "cla"}]

    # Change during deploy
    psql_host = "localhost"
    psql_user = "hf"
    psql_password = "hash_framework"
    psql_database = "hash_framework"

    job_count = 1
    master_uri = "http://10.1.30.250:5000"

    def update_basepath(base_path):
        config.base_path = base_path
        config.tools = base_path + "/tools"
        cms_bin = tools + "/cryptominisat5"
        bc_bin = tools + "/bc2cnf"
        model_dir = base_path + "/tmpmodels"
