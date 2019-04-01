#!/bin/bash

# script to get the timestamp of creation time for nifti volumes


# subject id to process
msg='enter subject ID:' 
echo $msg
read subject
echo you entered: $subject

# run number
msg='enter run number:' 
echo $msg
read runnum
echo you entered: $runnum

# raw data folder
msg='enter raw data folder (e.g., serie03):' 
echo $msg
read rawfolder
echo you entered: $rawfolder


################################################################################
################################################################################


# define output files (e.g., 'data/subj009/run1_voltimes')
cd ../data/${subject}
outDir=$(pwd)
tempfile=${outDir}/temp
outfile=${outDir}/run${runnum}_voltimes
touch $tempfile
touch $outfile

# go to raw data folder
cd ../../FriendEngine/Friend_Engine_Sources/Friend_Engine_Sources/Application/output_scans
volfiles=${rawfolder}/vol*

# save out timing info to a temp file
for f in $volfiles
do
	stat $f | grep -w "Modify:" >> $tempfile
done

cd $outDir
awk '{print $2 "\t" $3}' $tempfile > $outfile
rm $tempfile






