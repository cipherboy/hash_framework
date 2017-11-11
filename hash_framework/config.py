from os.path import expanduser

class config:
    base_path = expanduser("~")
    threads = 4

    tools = base_path + "/tools"

    cms_bin = tools + "/cryptominisat5"
    cms_args = []

    bc2cnf_bin = tools + "/bc2cnf"
    bc2cnf_args = ["-nots", "-nocoi", "-nosimplify"]

    model_dir = base_path + "/models"
    cache_dir = base_path + "/kernel_cache"
    sat_dir = base_path + "/sats"

    def update_basepath(base_path):
        config.base_path = base_path
        config.tools = base_path + "/tools"
        cms_bin = tools + "/cryptominisat5"
        bc_bin = tools + "/bc2cnf"
        model_dir = base_path + "/tmpmodels"
