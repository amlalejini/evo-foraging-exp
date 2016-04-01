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
    settings_fp = "param/settings.json"
    # Load up 'dem sett'ns
    with open(settings_fp) as fp:
        settings = json.load(fp)
    data_loc = settings["analysis"]["exp_data_location"]
    test_envs_loc = settings["analysis"]["test_envs_loc"]
    analysis_dump = settings["analysis"]["analysis_dump"]
    # Grab list of treatments in data location
    treatments = [tname for tname in os.listdir(data_loc) if os.path.isdir(os.path.join(data_loc, tname))]
    # Analyze treatment by treatment
    for treatment in treatments:
        print treatment
        treatment_loc = os.path.join(data_loc, treatment)
        # Grab number of replicates in treatment
        replicates = [rname for rname in os.listdir(treatment_loc) if os.path.isdir(os.path.join(treatment_loc, rname))]
        # Analyze each replicate
        for rep in replicates:
            print rep
            rep_loc = os.path.join(treatment_loc, rep)
            # Make an analysis directory here
            mkdir_p(os.path.join(rep_loc, "analysis"))
            # Run local MABE using treatment config and some extra cmdline args needed for analysis mode
            #analyzeOutputDirectory = os.path.join(rep_loc, "analysis") + "/"
            genomeFileToAnalyze = os.path.join(rep_loc, "output", settings["analysis"]["genomeFileToAnalyze"])
            repeats = str(settings["analysis"]["genome_trials"])
            # Analyze genome in each test environment
            test_envs = [ename for ename in os.listdir(test_envs_loc) if ".cfg" in ename]
            for env in test_envs:
                configFileName = os.path.join(test_envs_loc, env)
                analyzeOutputDirectory = os.path.join(analysis_dump, treatment, rep, "env__" + env.replace(".cfg","")) + "/"
                log = os.path.join(analyzeOutputDirectory, "analysis_log")
                mkdir_p(analyzeOutputDirectory)
                # Build command to run
                cmd = "./config/MABE configFileName %s analyzeMode 1 analyzeOutputDirectory %s repeats %s MAIN_genomeFileToAnalyze %s > %s" % (configFileName, analyzeOutputDirectory, repeats, genomeFileToAnalyze, log)
                # Spawn process for command; wait for it to come back
                process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
                output, err = process.communicate()
    print ("DONE")
