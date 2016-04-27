import json, os, copy, errno

'''
Script functionality:
 1) generate .cfg files each treatment configuration specified in settings file.
 2) generate run_list file to run experiments on HPCC
'''

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def read_cfg(cfg_fp):
    '''
    Return configuration settings from path to .cfg file.
    Format: {"setting": value,...}
    '''
    configuration = {}
    with open(cfg_fp) as fp:
        for line in fp:
            line = line.split("#")[0].strip()
            if line == "": continue
            setting = line.split("=")
            configuration[setting[0].strip()] = setting[1].strip()
    return configuration

def write_cfg(cfg_dict, out_loc, fname):
    content = ""
    for k in cfg_dict:
        line = "%s = %s\n" % (k, cfg_dict[k])
        content += line
    mkdir_p(out_loc) # make sure out location exists
    with open(os.path.join(out_loc, fname), "w") as fp:
        fp.write(content)

if __name__ == "__main__":
    settings_fp = "param/settings.json"

    # Load settings
    with open(settings_fp) as fp:
        settings = json.load(fp)

    exp_data_dump = settings["exp_data_dump_partial_path"].strip("/")
    # Load template (default settings)
    template_settings = read_cfg(settings["settings_template"])

    # Build all possible treatments from experiment config settings
    cfgs = {}
    for var in settings["experiment_config"]:
        del template_settings[var]
        vals = settings["experiment_config"][var]["values"]
        uid = settings["experiment_config"][var]["uid"]
        # if a list wasn't provided, turn it into a list
        if (not isinstance(vals, list)) or isinstance(vals, basestring): vals = [vals]
        if len(cfgs) == 0:
            cfgs = {"%s-%s" % (uid, str(v)):{var: str(v)} for v in vals}
            continue
        new = {}
        for val in vals:
            def update(d, k, v):
                d[k] = v
                return d
            new.update({"%s_%s-%s" % (cfg_key, uid, str(val)): update(copy.deepcopy(cfgs[cfg_key]), var, val) for cfg_key in cfgs})
        # update current configs with newly made configs
        cfgs = new

    # Write config files out
    for treatment in cfgs:
        cfgs[treatment].update(template_settings)
        write_cfg(cfgs[treatment], settings["config_output"], "%s.cfg" % treatment)

    if settings["generate_run_list"]:
        # Build a run list flie for this
        with open(settings["run_list_template"]) as fp:
            rl_content = fp.read() + "\n\n"
        for treatment in cfgs:
            reps = "%s..%s" % (settings["run_list_config"]["rep_start"], settings["run_list_config"]["rep_end"])
            name ="%s_rep" % treatment
            config_name = "%s.cfg" % treatment
            cmd = "%s %s mkdir output && mkdir config && cp %s config && rm ./*.cfg && module swap GNU GNU/4.8.3 && ./MABE configFileName ./config/%s outputDirectory ./output/ randomSeed $seed" % (reps, name, config_name, config_name)
            rl_content += "%s\n\n" % cmd
        with open(os.path.join("config", "run_list"), "w") as fp:
            fp.write(rl_content)

    if settings["generate_qsub_files"]:
        for treatment in cfgs:
            qsub_content = '''#!/bin/bash --login

### Define Resources needed:
#PBS -l walltime=144:00:00
#PBS -l mem=8gb
#PBS -l nodes=1:ppn=1
#PBS -l feature=intel14
### Name job
#PBS -N %s
### Email stuff
#PBS -M lalejini@msu.edu
#PBS -m ae
### Setup multiple replicates
#PBS -t 1-10
### Combine and redirect output/error logs
#PBS -j oe

TREATMENT_NAME=%s
DATA_DIR=${HOME}/%s
REP_DIR=${DATA_DIR}/${TREATMENT_NAME}/rep_${PBS_ARRAYID}

cd ${PBS_O_WORKDIR}
mkdir -p ${REP_DIR}
mkdir -p ${REP_DIR}/output

cp ../config/${TREATMENT_NAME}.cfg ${REP_DIR}
cp ../config/MABE ${REP_DIR}

cd ${REP_DIR}
./MABE configFileName ./${TREATMENT_NAME}.cfg outputDirectory ./output/ randomSeed ${PBS_ARRAYID} > ${REP_DIR}/log 2>&1

qstat -f ${PBS_JOBID}
''' % (treatment, treatment, exp_data_dump)
            with open("qsub_config/%s.qsub" % treatment, "w") as fp:
                fp.write(qsub_content)
