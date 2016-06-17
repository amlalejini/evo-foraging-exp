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
    analysis_dump = settings["analysis"]["analysis_dump"]
    test_envs_loc = settings["analysis"]["test_envs_loc"]
    # Grab list of treatments in data location
    runs = [tname for tname in os.listdir(data_loc) if os.path.isdir(os.path.join(data_loc, tname)) and "__rep_" in tname]
    # Analyze treatment by treatment
    for run in runs:
        print "Analyzing: " + run
        run_loc = os.path.join(data_loc, run)
        # Grab the genome file we want to analyze
        genome_file_to_analyze = os.path.join(run_loc, "output", settings["analysis"]["genomeFileToAnalyze"])
        # Grab all of the test environments to run genome through
        test_envs = [ename for ename in os.listdir(test_envs_loc) if ".cfg" in ename]
        for env in test_envs:
            print "\tTesting in env: " + env
            env_cfg = os.path.join(test_envs_loc, env)
            bl_cfg = os.path.join(settings["config_output"], "settings_baseline.cfg")
            env_analyze_dump = os.path.join(analysis_dump, run, "env__" + env.replace(".cfg", "")) + "/"
            log = os.path.join(env_analyze_dump, "analysis_log")
            # Make a dump directory for this run
            mkdir_p(env_analyze_dump)
            # Build the analysis run command
            cmd = "./exp_configs/MABE -f %s %s -p GLOBAL-mode test GLOBAL-analysisDirectory %s GLOBAL_ANALYZE_MODE-analyzePopulationFile %s ARCHIVIST_DEFAULT-realtimeFilesInterval 1 ARCHIVIST_DEFAULT-snapshotDataInterval 1 ARCHIVIST_DEFAULT-snapshotGenomeInterval 1 WORLD-repeats %s" % (bl_cfg, env_cfg, env_analyze_dump, genome_file_to_analyze, str(settings["analysis"]["genome_trials"]))
            # Call cmd
            rc = subprocess.call(cmd, shell = True)
            print "\t" + cmd
            
    print "DONE"

    #         repeats = str(settings["analysis"]["genome_trials"])
    #         # Analyze genome in each test environment
    #         test_envs = [ename for ename in os.listdir(test_envs_loc) if ".cfg" in ename]
    #         for env in test_envs:
    #             print "ENV: " + str(env)
    #             configFileName = os.path.join(test_envs_loc, env)
    #             analyzeOutputDirectory = os.path.join(analysis_dump, treatment, rep, "env__" + env.replace(".cfg","")) + "/"
    #             log = os.path.join(analyzeOutputDirectory, "analysis_log")
    #             mkdir_p(analyzeOutputDirectory)
    #             # Build command to run
    #             cmd = "./config/MABE configFileName %s analyzeMode 1 analyzeOutputDirectory %s repeats %s MAIN_genomeFileToAnalyze %s > %s" % (configFileName, analyzeOutputDirectory, repeats, genomeFileToAnalyze, log)
    #             # Spawn process for command; wait for it to come back
    #             process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    #             output, err = process.communicate()
    # print ("DONE")
