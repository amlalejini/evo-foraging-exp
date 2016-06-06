
## Directory/Script descriptions
 * config/
  * Treatment configs for expriment
 * test_envs/
  * These are environments (defined by MABE settings files) to test genomes within when running 'run_analysis.py'
 * qsub_config/
  * qsub files for hpcc submission
 * group_script/
  * Original scripts written by group members
 * md_vids.py
  * Given frame dump from processing (in expected directory structure), this script will automatically make videos
 * run_metrics.py
  * Given analysis data (from 'run_analysis.py'), run metrics written by group members. Also, generate convenient csv files for group member analysis
 * cp_configs/
   * Holds template 4 hour checkpointing job submission scripts used for generating treatment-specific submission scripts. 
