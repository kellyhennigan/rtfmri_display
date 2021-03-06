#!/bin/bash

# script to get the timestamp of creation time for nifti volumes


# vol nii folder
msg='enter raw data folder (e.g., serie03):' 
echo $msg
read voldir
echo you entered: $voldir


################################################################################
################################################################################

# go to nii vol data folder 
cd /home/cniuser/rt/scannerConverter/output_scans

# get list of nifti volume files
volfiles=${voldir}/vol*

# define text file to save out vol times 
outDir=$(pwd)
tempfile=${outDir}/temp
outfile=${outDir}/${voldir}_voltimes
touch $tempfile
touch $outfile

# save out timing info to a temp file
for f in $volfiles
do
	stat $f | grep -w "Modify:" >> $tempfile
done

cd $outDir
awk '{print $2 "\t" $3}' $tempfile > $outfile
rm $tempfile






