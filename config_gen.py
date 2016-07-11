import json, os, copy, errno, subprocess, argparse

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

    # Build all possible treatments from experiment config settings
    cfgs = {}
    for var in settings["experiment_config"]:
        vals = settings["experiment_config"][var]["values"]
        uid = settings["experiment_config"][var]["uid"]
        # if a list wasn't provided, turn it into a list
        if (not isinstance(vals, list)) or isinstance(vals, basestring): vals = [vals]

        if len(cfgs) == 0:
            # We haven't started building cfgs yet. Make initial treatment dictionaries.
            #  Here, we start with exactly one treatment per variable value.
            cfgs = {"%s-%s" % (uid, str(v)):{var: str(v)} for v in vals}
            continue
        # We must not be doing the first variable. Let's rebuild our configs given new variable values and old treatments.
        new = {}
        for val in vals:
            def update(d, k, v):
                d[k] = v
                return d
            new.update({"%s_%s-%s" % (cfg_key, uid, str(val)): update(copy.deepcopy(cfgs[cfg_key]), var, val) for cfg_key in cfgs})
        # update current configs with newly made configs
        cfgs = new

    # Write out each of our parameter configurations
    for treatment in cfgs:
        write_cfg(cfg_dict = cfgs[treatment], out_loc = settings["config_output"], fname = "%s.cfg" % treatment)

    if (settings["longjob"]):
        ################
        # LONG JOB SUBMISSION GEN
        ################
        # Build out outer loop (handles multiple replicates) for checkpointed job submission
        olc_qsub_cmd = ""
        for treatment in cfgs:
            olc_qsub_cmd += "\tqsub -v repN=$R %s_long.qsub\n" % treatment
        outerlooplong_content = '''#!/bin/bash
#we simply itterate over a shit ton of parameters (R H F) and use N and M as a counter to generate folders later
for R in {1..%d}
do
%s
done
''' % (settings["replicates"], olc_qsub_cmd)
        with open(os.path.join(settings["lognqsubs_dump"], "outerLoopLong.sh"), "w") as fp:
            fp.write(outerlooplong_content)
        # Make the script executable
        rc = subprocess.call("chmod 777 %s" % os.path.join(settings["longqsubs_dump"], "outerLoopLong.sh"), shell = True)

        # Build each of our qsub files.
        for treatment in cfgs:
            qsub_content = '''#!/bin/bash -login
#PBS -l nodes=1:ppn=1,walltime=03:45:00,mem=8gb,feature=gbe
#PBS -j oe

# we need the following three lines
shopt -s expand_aliases
cd ${PBS_O_WORKDIR}
module load powertools

# Define the current treatment name as well as our destination data dump directory
TREATMENT_NAME=%s
DATA_DIR=/mnt/scratch/%s/data/evo-foraging-strats

# mabe might require this, comment if you don't need it:
module swap GNU GNU/5.2

# 4 hours * 60 minutes * 6 seconds - 60 seconds * 5 minutes
# export BLCR_WAIT_SEC=$(( 4 * 60 * 60 - 60 * 5 ))
# just so you know 12600 seconds is 3.5 hours
# I adjusted the wall time to 3:45 I think that should give you a little bit of an edge
# against 4h jobs
# 12600 is 3.5 hours of runtime
export BLCR_WAIT_SEC=$(( 12600 ))
export PBS_JOBSCRIPT="$0"
echo "Waiting ${BLCR_WAIT_SEC} seconds to run ${PBS_JOBSCRIPT}"

# Define MABE executable name and command line options.
EXECUTABLE=MABE
COMMANDLINEOPTIONS="-f settings_baseline.cfg %s -p GLOBAL-randomSeed ${repN}"

WORK=${DATA_DIR}/${TREATMENT_NAME}__rep_${repN}

if [ ! -f checkfile.blcr ]
then
    # Make a subdirectory - this makes snapshotting easier!
    # ICER recommends running this on scratch, I don't know why, here I copy everything into a subfolder
    # Define and make our working directory

    mkdir -p $WORK
    # Copy MABE and relevant config files to working directory
    cp ${EXECUTABLE} ${WORK}/
    cp ../exp_configs/${TREATMENT_NAME}.cfg ${WORK}/
    cp ../exp_configs/settings_baseline.cfg ${WORK}/
    cp ../exp_configs/${EXECUTABLE} ${WORK}/
    mkdir -p ${WORK}/output
fi
cd $WORK
#Run main simulation program
longjob ./$EXECUTABLE $COMMANDLINEOPTIONS

#I have no idea what the two lines below actually do ...
ret=$?
qstat -f ${PBS_JOBID}

exit $ret

''' % (treatment, settings["scratch_user"], treatment + ".cfg")
            # Write out out qsub file
            with open(os.path.join(settings["longqsubs_dump"], "%s_long.qsub" % treatment), "w") as fp:
                fp.write(qsub_content)
            # Make the script executable
            rc = subprocess.call("chmod 777 %s" % os.path.join(settings["longqsubs_dump"], "%s_long.qsub" % treatment), shell = True)
    else:
        ###################
        # NORMAL SUBMISSION SCRIPT GEN
        ###################
        for treatment in cfgs:
            qsub_content = '''#!/bin/bash --login

### Define Resources needed:
#PBS -l walltime=%s
#PBS -l mem=%s
#PBS -l nodes=1:ppn=1
#PBS -l feature=intel14
### Name job
#PBS -N %s
### Email stuff
#PBS -M %s
#PBS -m ae
### Setup multiple replicates
#PBS -t %d-%d
### Combine and redirect output/error logs
#PBS -j oe

TREATMENT_NAME=%s
DATA_DIR=%s
REP_DIR=${DATA_DIR}/${TREATMENT_NAME}__rep_${PBS_ARRAYID}

cd ${PBS_O_WORKDIR}
mkdir -p ${REP_DIR}
mkdir -p ${REP_DIR}/output

cp ../exp_configs/${TREATMENT_NAME}.cfg ${REP_DIR}
cp ../exp_configs/settings_baseline.cfg ${REP_DIR}
cp ../exp_configs/MABE ${REP_DIR}

cd ${REP_DIR}

EXECUTABLE=MABE
COMMANDLINEOPTIONS="-f settings_baseline.cfg ${TREATMENT_NAME}.cfg -p GLOBAL-randomSeed ${PBS_ARRAYID}"

./$EXECUTABLE $COMMANDLINEOPTIONS > log

qstat -f ${PBS_JOBID}

''' % (settings["job_settings"]["walltime"], settings["job_settings"]["mem"], treatment, settings["job_settings"]["email"], 1, settings["replicates"], treatment, settings["job_settings"]["data_dump_path"])

            # Write out out qsub file
            mkdir_p(os.path.join(settings["qsubs_dump"]))
            with open(os.path.join(settings["qsubs_dump"], "%s.qsub" % treatment), "w") as fp:
                fp.write(qsub_content)
