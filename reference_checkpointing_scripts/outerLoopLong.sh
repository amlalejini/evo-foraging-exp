#!/bin/bash
#we simply itterate over a shit ton of parameters (R H F) and use N and M as a counter to generate folders later
for N in 0 1 2 3 4 5 6 7 8 9; do
	for M in 0 1 2 3 4 5 6 7 8 9; do
		for R in 0 1; do
			for H in 0 1; do
				for F in 0 1; do
					qsub -v localN=$N$M,localR=$R,localH=$H,localF=$F runThisLong.sh
				done
			done
		done
	done
done
