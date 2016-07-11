import os, subprocess

if __name__ == "__main__":
    # Grab all local qsub files
    jobs = [j for j in os.listdir(".") if ".qsub" in j]
    for job in jobs:
        print "Submitting: " + job
        jsubcmd = "qsub %s" % job
        rc = subprocess.call(jsubcmd, shell = True)
    print "DONE"
