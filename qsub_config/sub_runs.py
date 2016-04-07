import json, os, errno, subprocess

'''
Script functionality:
 * Automate running analysis on evolved genomes from evo-foraging-exp
'''

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

if __name__ == "__main__":
    qsub_repo = "./"
    subs = [sname for sname in os.listdir(qsub_repo) if sname.split(".")[-1] == "qsub"]
    print "Submitting %d jobs..." % len(subs)
    for sub in subs:
        print "Submitting %s" % sub
        cmd = "qsub ./%s" % sub
        # Spawn process for command; wait for it to come back
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, err = process.communicate()
        print output
    print ("DONE")
