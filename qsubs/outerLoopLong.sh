#!/bin/bash
#we simply itterate over a shit ton of parameters (R H F) and use N and M as a counter to generate folders later
for R in {1..50}
do
	qsub -v repN=$R SL-81_LS-1296_P-0_G-9_WS-81_long.qsub
	qsub -v repN=$R SL-81_LS-1296_P-1.0_G-27_WS-81_long.qsub
	qsub -v repN=$R SL-81_LS-1296_P-1.0_G-9_WS-81_long.qsub
	qsub -v repN=$R SL-81_LS-1296_P-1.0_G-3_WS-81_long.qsub
	qsub -v repN=$R SL-81_LS-1296_P-0_G-27_WS-81_long.qsub
	qsub -v repN=$R SL-81_LS-1296_P-1.0_G-1_WS-81_long.qsub
	qsub -v repN=$R SL-81_LS-1296_P-0_G-1_WS-81_long.qsub
	qsub -v repN=$R SL-81_LS-1296_P-0_G-3_WS-81_long.qsub
done
