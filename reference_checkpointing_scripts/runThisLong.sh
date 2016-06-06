#!/bin/bash -login
#PBS -l nodes=1:ppn=1,walltime=03:45:00,mem=8gb,feature=gbe
#PBS -j oe

#we need the follwoing three lines and I only know what the last two do...
shopt -s expand_aliases
cd $PBS_O_WORKDIR
module load powertools

#mabe might require this, comment if you don't need it:
module swap GNU GNU/4.8.3

# 4 hours * 60 minutes * 6 seconds - 60 seconds * 5 minutes
#export BLCR_WAIT_SEC=$(( 4 * 60 * 60 - 60 * 5 ))
#just so you know 12600 seconds is 3.5 hours
#I adjusted the wall time to 3:45 I think that should give you a little bit of an edge
#against 4h jobs
#12600 is 3.5 hours of runtime

export BLCR_WAIT_SEC=$(( 12600 ))
export PBS_JOBSCRIPT="$0"
echo "Waiting ${BLCR_WAIT_SEC} seconds to run ${PBS_JOBSCRIPT}"

#lets define a couple of variables
#test is the executable filename I used
EXECUTABLE=MSG
#the name of the config file you want to use
#MABE uses these three
CONFIGFILEA=settings.cfg
CONFIGFILEB=settings_world.cfg
CONFIGFILEC=settings_organism.cfg
#the command line parameters you want MABE to have
COMMANDLINEOPTIONS="-f settings.cfg settings_organism.cfg settings_world.cfg -p GLOBAL-updates 20000 WORLD_SG-doHammer $localR WORLD_SG-randomizeFood $localF WORLD_SG-randomizeHome $localH WORLD_SG-pathFileName path.csv ARCHIVIST_LODWAP-dataFileName data.csv ARCHIVIST_LODWAP-genomeFileName genome.csv"


if [ ! -f checkfile.blcr ]
then
	#Make a subdirectory - this makes snapshotting easier!
	#ICER recommends running this on scratch, I don't know why, here I copy everything into a subfolder
	WORK=subDir_${localR}${localF}${localH}_${localN}
	#${PBS_JOBID}
	mkdir $WORK

	#we copy MABE and all config files in this subfolder
	cp $EXECUTABLE $WORK/
	cp $CONFIGFILEA $WORK/
	cp $CONFIGFILEB $WORK/
	cp $CONFIGFILEC $WORK/

  cd $WORK

fi
#Run main simulation program
longjob ./$EXECUTABLE $COMMANDLINEOPTIONS


#I have no idea what the two lines below actually do ...
ret=$?
qstat -f ${PBS_JOBID}

exit $ret
