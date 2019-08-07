#!/bin/bash

# get the timestamp for file creation times for dicom slice files


# path to folder that contains dicom files 
msg='enter path to dicom file dir (e.g., /cnimr/images/p1166/e2539/s26115):' 
echo $msg
read indir
echo you entered: $indir

# out file path
outdir=/home/cniuser/rt/scannerConverter/output_scans
msg='enter raw data folder (e.g., serie03):' 
echo $msg
read seriesnum
echo you entered: $seriesnum


################################################################################
################################################################################

#outdir=$(dirname "${outpath}") 	 # directory for out file 

# create outdir if it doesnt already exist
if [ ! -d "$outdir" ]; then
	mkdir $outdir
fi 

outfile=${seriesnum}_dicom_times # outfile name
outpath=${outdir}/${outfile}

# create the out & temp files
touch $outpath
touch ${outdir}/temp

# go to data folder 
cd $indir

# get the number of dicom files
datafiles=*MRDC*
nfiles=$(echo $datafiles | wc -w)


for f in $(seq 1 $nfiles)
do 
	stat *MRDC.${f} | grep -w "Modify:" >> ${outdir}/temp
done

cd $outdir
awk '{print $2 "\t" $3}' temp > $outfile
rm temp






