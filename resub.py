import json, os, copy, errno, subprocess, argparse

resub = ['SL-81_LS-1296_P-0.5_G-27_WS-81__rep_11', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_23', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_29', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_2', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_30', 'SL-81_LS-1296_P-1.0_G-3_WS-81__rep_26', 'SL-81_LS-1296_P-0.0_G-27_WS-81__rep_12', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_5', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_24', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_16', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_27', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_17', 'SL-81_LS-1296_P-1.0_G-3_WS-81__rep_27', 'SL-81_LS-1296_P-0.0_G-3_WS-81__rep_19', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_26', 'SL-81_LS-1296_P-0.5_G-27_WS-81__rep_19']

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

if __name__ == "__main__":
    settings_fp = "param/settings.json"

    # Load settings
    with open(settings_fp) as fp:
        settings = json.load(fp)
    ###################
    # Gen resubs
    ###################
    for job in resub:
        treatment = job.split("__")[0]
        rep_id = job.split("_")[-1]
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
### Combine and redirect output/error logs
#PBS -j oe

REP=%s
TREATMENT_NAME=%s
DATA_DIR=%s_resub
REP_DIR=${DATA_DIR}/${TREATMENT_NAME}__rep_${REP}

module load powertools
module swap GNU GNU/5.2

cd ${PBS_O_WORKDIR}
mkdir -p ${REP_DIR}
mkdir -p ${REP_DIR}/output

cp ../../exp_configs/${TREATMENT_NAME}.cfg ${REP_DIR}
cp ../../exp_configs/settings_baseline.cfg ${REP_DIR}
cp ../../exp_configs/MABE ${REP_DIR}

cd ${REP_DIR}

EXECUTABLE=MABE
COMMANDLINEOPTIONS="-f settings_baseline.cfg ${TREATMENT_NAME}.cfg -p GLOBAL-randomSeed ${REP}"

./$EXECUTABLE $COMMANDLINEOPTIONS > log

qstat -f ${PBS_JOBID}

''' % (settings["job_settings"]["walltime"], settings["job_settings"]["mem"], treatment, settings["job_settings"]["email"], rep_id, treatment, settings["job_settings"]["data_dump_path"])

        # Write out out qsub file
        mkdir_p(os.path.join(settings["qsubs_dump"], "resubs"))
        print os.path.join(settings["qsubs_dump"], "resubs", "%s.qsub" % job)
        with open(os.path.join(settings["qsubs_dump"], "resubs", "%s.qsub" % job), "w") as fp:
            fp.write(qsub_content)
