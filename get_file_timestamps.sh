#!/bin/bash

# get the file creation timestamps for dicom slice files and nifti volume files


# get dcmDirPath (path to dir that contains raw dicoms)
msg='enter path to dicom file dir (e.g., /cnimr/images/p1166/e2539/s26115):' 
echo $msg
read dcmDir
echo you entered: $dcmDir


# get niiDirPath (path to dir that contains nifti volume files)
niiParentDir=/home/cniuser/rt/scannerConverter/output_scans
msg='enter nifti data folder (e.g., serie03):' 
echo $msg
read niiDirName
echo you entered: $niiDir
niiDir=${niiParentDir}/${niiDirName}


# get outDirPath (path to dir to write out timestamp files to)
outParentDir=/home/cniuser/rt/data
msg='enter subject id (e.g., pilot007):' 
echo $msg
read outDirName
echo you entered: $outDirName
outDir=${outParentDir}/${outDirName}

# get runnum 
msg='enter run number (e.g., 2):' 
echo $msg
read runnum
echo you entered: $runnum

# out file names: 
outDcmFile=${outDir}/run${runnum}_dicom_times
outNiiFile=${outDir}/run${runnum}_vol_times

################################################################################
################################################################################

# create outDirPath if it doesnt already exist
if [ ! -d "$outDir" ]; then
	mkdir $outDir
fi 


############ dicom timestamps 

# create dcm timestamp outfile if it doesn't exist 
if [ ! -f "$outDcmFile" ]; then
	touch $outDcmFile
fi 

# write out dicom dir & nifti file dir to file header 
echo dicom dir:${dcmDir} >> $outDcmFile
echo nifti vol dir:${niiDir} >> $outDcmFile


# get the number of dicom files
cd $dcmDir
datafiles=*MRDC*
nfiles=$(echo $datafiles | wc -w)

# loop over files to record their file creation timestamps
for f in $(seq 1 $nfiles)
do 
	# get filename & file creation time stamps as strings
	fname="$(stat *MRDC.${f} | grep -w "File:" | awk '{print $2}')"
	timestamp="$(stat *MRDC.${f} | grep -w "Modify:" | awk '{print $2 "\t" $3}')"

	# write them to out file 
	echo -n $fname >> $outDcmFile
	echo -n '; ' >> $outDcmFile
	echo $timestamp >> $outDcmFile

done


############ nifti timestamps 

# create nifti timestamp outfile if it doesn't exist 
if [ ! -f "$outNiiFile" ]; then
	touch $outNiiFile
fi 

# write out dicom dir & nifti file dir to file header 
echo dicom dir:${dcmDir} >> $outNiiFile
echo nifti vol dir:${niiDir} >> $outNiiFile


# get the number of dicom files
cd $niiDir
volfiles=vol*

# save out timing info to a temp file
for f in $volfiles
do
	# get filename & file creation time stamps as strings
	fname="$(stat $f | grep -w "File:" | awk '{print $2}')"
	timestamp="$(stat $f | grep -w "Modify:" | awk '{print $2 "\t" $3}')"

	# write them to out file 
	echo -n $fname >> $outNiiFile
	echo -n '; ' >> $outNiiFile
	echo $timestamp >> $outNiiFile

done








