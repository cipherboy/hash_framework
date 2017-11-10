class compute:
    compute = ["compute-01", "compute-02", "compute-03", "compute-04", "compute-05", "compute-06", "compute-07", "compute-08", "compute-09"]
    personal = ["moselle", "recon7"]
    etg = ["linux-1", "linux-2", "linux-3", "linux-4", "linux-5", "linux-6"]
    known_hosts = compute
    alive_hosts = set()
    last_check = -1
    cms_path = {
        "recon7": "/home/cipherboy/GitHub/cryptominisat/cryptominisat5",
        "moselle": "/home/scheel/cryptominisat5",
        "linux-1": "/home/scheel/cryptominisat5",
        "linux-2": "/home/scheel/cryptominisat5",
        "linux-3": "/home/scheel/cryptominisat5",
        "linux-4": "/home/scheel/cryptominisat5",
        "linux-5": "/home/scheel/cryptominisat5",
        "linux-6": "/home/scheel/cryptominisat5",
        "compute-01": "/home/cipherboy/cryptominisat5",
        "compute-02": "/home/cipherboy/cryptominisat5",
        "compute-03": "/home/cipherboy/cryptominisat5",
        "compute-04": "/home/cipherboy/cryptominisat5",
        "compute-05": "/home/cipherboy/cryptominisat5",
        "compute-06": "/home/cipherboy/cryptominisat5",
        "compute-07": "/home/cipherboy/cryptominisat5",
        "compute-08": "/home/cipherboy/cryptominisat5",
        "compute-09": "/home/cipherboy/cryptominisat5",
    }
    tmp_path = {
        "x1c": "/home/cipherboy/sats",
        "recon7": "/home/cipherboy/sats",
        "moselle": "/home/scheel/sats",
        "linux-1": "/home/scheel/sats",
        "linux-2": "/home/scheel/sats",
        "linux-3": "/home/scheel/sats",
        "linux-4": "/home/scheel/sats",
        "linux-5": "/home/scheel/sats",
        "linux-6": "/home/scheel/sats",
        "compute-01": "/home/cipherboy/sats",
        "compute-02": "/home/cipherboy/sats",
        "compute-03": "/home/cipherboy/sats",
        "compute-04": "/home/cipherboy/sats",
        "compute-05": "/home/cipherboy/sats",
        "compute-06": "/home/cipherboy/sats",
        "compute-07": "/home/cipherboy/sats",
        "compute-08": "/home/cipherboy/sats",
        "compute-09": "/home/cipherboy/sats",
    }
    num_jobs = {
        "x1c": 0,
        "recon7": 4,
        "moselle": 14,
        "linux-1": 4,
        "linux-2": 4,
        "linux-3": 8,
        "linux-4": 8,
        "linux-5": 4,
        "linux-6": 8,
        "compute-01": 8,
        "compute-02": 8,
        "compute-03": 8,
        "compute-04": 8,
        "compute-05": 8,
        "compute-06": 4,
        "compute-07": 4,
        "compute-08": 8,
        "compute-09": 8,
    }
    job_queue = {
        "x1c": [],
        "recon7": [],
        "moselle": [],
        "linux-1": [],
        "linux-2": [],
        "linux-3": [],
        "linux-4": [],
        "linux-5": [],
        "linux-6": [],
        "compute-01": [],
        "compute-02": [],
        "compute-03": [],
        "compute-04": [],
        "compute-05": [],
        "compute-06": [],
        "compute-07": [],
        "compute-08": [],
        "compute-09": [],
    }
    retry_limit = 3

    def run_cmd_sync(host, command, success_ret=[0], out_file=None, err_file=None, timeout=None):
        assert(type(host) == str)
        assert(host in compute.known_hosts)
        assert(type(command) == str)

        success = False
        r_c = -1
        for i in range(0, compute.retry_limit):
            n_p = None
            try:
                if out_file:
                    o_f = open(out_file, 'w')
                    n_p = subprocess.Popen(["ssh", host, command], stdin=subprocess.DEVNULL, stdout=o_f)
                else:
                    n_p = subprocess.Popen(["ssh", host, command], stdin=subprocess.DEVNULL)
                r_c = n_p.wait(timeout)
                if r_c not in success_ret:
                    print("run_cmd (" + str(i) + "): " + str(r_c))
                    time.sleep(1)
                    success = False
                    continue
                else:
                    success = True
                    break
            except:
                if n_p is not None:
                    try:
                        if n_p.poll() is None:
                            n_p.kill()
                            n_p.terminate()
                    except:
                        pass
                continue
        return success, r_c

    def run_cmd_async(host, command, success_ret=[0], out_file=None, err_file=None, timeout=None):
        assert(type(host) == str)
        assert(host in compute.known_hosts)
        assert(type(command) == str)

        n_p = None
        if out_file:
            o_f=open(out_file, 'w')
            n_p = subprocess.Popen(["ssh", host, command], stdin=subprocess.DEVNULL, stdout=o_f)
        else:
            n_p = subprocess.Popen(["ssh", host, command], stdin=subprocess.DEVNULL)
        return n_p

    def run_cmd(host, command, success_ret=[0], out_file=None, err_file=None, timeout=None, no_wait=False):
        if no_wait:
            return compute.run_cmd_async(host, command, success_ret, out_file, err_file, timeout)
        else:
            return compute.run_cmd_sync(host, command, success_ret, out_file, err_file, timeout)

    def scp_file(host, src, dest, no_wait=False):
        assert(type(host) == str)
        assert(host in compute.known_hosts)
        assert(type(src) == str)
        assert(type(dest) == str)

        print("scp " + src + " " + dest)

        if no_wait:
            n_p = subprocess.Popen(['scp', src, dest])
            return n_p

        success = False
        r_c = -1
        for i in range(0, compute.retry_limit):
            n_p = subprocess.Popen(['scp', src, dest])
            r_c = n_p.wait()
            if r_c != 0:
                print("scp_file (" + str(i) + "): " + src + " -> " + dest)
                time.sleep(1)
                success = False
                continue
            else:
                success = True
                break

        return success, r_c

    def build_scp_path(host, name):
        assert(type(host) == str)
        assert(host in compute.known_hosts)
        return host + ':' + compute.tmp_path[host] + "/" + name

    def build_path(host, name):
        assert(type(host) == str)
        assert(host in compute.known_hosts)
        return compute.tmp_path[host] + "/" + name

    def put_file(host, local, remote, no_wait=False):
        remote_file = compute.build_scp_path(host, remote)
        return compute.scp_file(host, local, remote_file, no_wait)

    def get_file(host, remote, local, no_wait=False):
        remote_file = compute.build_scp_path(host, remote)
        return compute.scp_file(host, remote_file, local, no_wait)

    def clean_tmp(host):
        assert(type(host) == str)
        assert(host in compute.known_hosts)
        path = compute.tmp_path[host]
        return compute.run_cmd(host, "rm " + path + "/*.out " + path + "/*.cnf")

    def make_tmp(host):
        assert(type(host) == str)
        assert(host in compute.known_hosts)
        path = compute.tmp_path[host]
        return compute.run_cmd(host, "mkdir -p " + path)

    def test_host(host):
        assert(type(host) == str)
        assert(host in compute.known_hosts)
        path = compute.tmp_path[host]
        return compute.run_cmd(host, "echo hi > /dev/null", timeout=8)

    def check_hosts():
        alive = set()
        for host in compute.known_hosts:
            ret, _ = compute.test_host(host)
            if ret:
                alive.add(host)
        compute.alive_hosts = alive
        return alive

    def assign_work():
        while len(compute.alive_hosts) == 0:
            print("assign_work(): no hosts")
            compute.check_hosts()

        h = list(compute.alive_hosts)
        random.shuffle(h)

        for host in h:
            if len(compute.job_queue[host]) < compute.num_jobs[host]:
                return host

        return None

    def build_cmd(host, r_infile, r_outfile, count, random):
        t_i = compute.build_path(host, r_infile)
        return compute.cms_path[host] + " --maxsol " + str(count) + " --random " + str(random) + " " + t_i

    def assign_sat(host, in_file, out_file, count=1, seed=0, no_wait=False, ident=None):
        r = str(random.randint(10000000000, 99999999999))
        r_input = r + "-" + in_file
        r_output = r + "-" + out_file
        cmd = compute.build_cmd(host, r_input, r_output, count, seed)
        print(cmd)
        compute.put_file(host, in_file, r_input)
        if no_wait:
            r = [compute.run_cmd(host, cmd, success_ret=[10, 20], no_wait=no_wait, out_file=out_file), host, r_input, r_output, out_file, in_file, ident]
            compute.job_queue[host].append(r)
            return r
        r = compute.run_cmd(host, cmd, success_ret=[10, 20], out_file=out_file)
        if r[0] == True:
            if r[1] == 10:
                print("SAT")
            elif r[1] == 20:
                print("UNSAT")
            else:
                print("UNKNOWN: " + str(r[1]))
            compute.get_file(host, r_output, out_file)
            return r[1] == 10
        return r

    def perform_sat(in_file, out_file, count=1, seed=0, no_wait=False, ident=None):
        host = compute.assign_work()
        if host == None:
            return None
        return compute.assign_sat(host, in_file, out_file, count, seed, no_wait, ident)

    def wait_job_hosts(hosts=None, loop_until_found=False):
        if hosts is None:
            hosts = compute.known_hosts.copy()
        while True:
            time.sleep(0.25)
            random.shuffle(hosts)
            for host in hosts:
                if len(compute.job_queue[host]) > 0:
                    i = 0
                    j = len(compute.job_queue[host])
                    while i < j+2:
                        i += 1
                        job = compute.job_queue[host].pop(0)
                        n_p = job[0]
                        r = n_p.poll()
                        if r is None:
                            compute.job_queue[host].append(job)
                            continue
                        else:
                            print("\n\n")
                            if r == 10:
                                print("SAT")
                            elif r == 20:
                                print("UNSAT")
                            else:
                                print("UNKNOWN: " + str(r))
                            return (r == 10, job)
            if not loop_until_found:
                break
        return None
