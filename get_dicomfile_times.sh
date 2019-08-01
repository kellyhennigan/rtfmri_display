#!/bin/bash

# get the timestamp for file creation times for dicom slice files


# path to folder that contains dicom files 
msg='enter path to dicom file dir (e.g., /cnimr/images/p1166/e2539/s26115):' 
echo $msg
read indir
echo you entered: $indir

# out file path
msg='enter filepath to save out file times to (e.g., /home/cniuser/rt/scannerConverter/output_scans/serie07_dicom_times):' 
echo $msg
read outpath
echo you entered: $outpath


################################################################################
################################################################################


outfile=$(basename "${outpath}") # filename for out file
outdir=$(dirname "${outpath}") 	 # directory for out file 


# create outdir if it doesnt already exist
if [ ! -d "$outdir" ]; then
	mkdir $outdir
fi 

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






