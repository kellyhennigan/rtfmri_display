import os
import sys

# function to load in a "DUMP" file created by the engine and return those values
#######################################################################################
# STUDY PARAMETERS

logfile='/Users/kelly/neurofeedback/rt/data/subj007/dumpFile_RUN01.txt'

file=open(logfile,'r')
vol=[]
base1=[]
base2=[]
roi1mean=[]
roi2mean=[]
fbval1=[]
fbval2=[]

for line in file:
	fields=line.split(';')
	vol.append(fields[0])
	base1.append(fields[1])
	base2.append(fields[2])
	roi1mean.append(fields[3])
	roi2mean.append(fields[4])
	fbval1.append(fields[5])
	fbval2.append(fields[6])