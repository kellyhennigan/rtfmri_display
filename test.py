import os
import sys
from visualizers import *


#######################################################################################
# STUDY PARAMETERS

maindir=os.path.abspath(os.path.join(os.getcwd(), os.pardir)) # main study directory

designfilepath=os.path.join(maindir,'exp_display','design181218.txt') # design file 

datadir=os.path.join(maindir,'data')  # data directory

nfuncvolumes = '160' # number of functional vols in the fmri scans

baselinecond = 'REST'  # baseline condition - this needs to be spelled the same way as in the design file

rawdatapath = os.path.join(maindir,'FriendEngine/Friend_Engine_Sources/Friend_Engine_Sources/Application/output_scans/serie10/vol_') # changing the directory of the volumes

activationLevel = '.01' # activation level 

useEngine = True # to use the engine (so thermometer fluctuates based on fmri data)

#dispLogData = True # if true and useEngine=False, this means display data from a log file

dry_run = True  # if dry_run equals True, the scanner will NOT be triggered

obj = Thermometer() # get an instance of thermometer from visualizers library

#######################################################################################



#########  initialize thermometer object
def initDisplayObj():

  #set the baseline condition
  obj.setBaseline(baselinecond)

  # read design file
  obj.readDesignFile(designfilepath)


  # Here we are building an array that maps the condition index to the correct feedback value. 
  # The conditions are sorted in alphabetical order  
  obj.feedbackMapping = []
  obj.feedbackMapping.append(1) # IMAGELEFT
  obj.feedbackMapping.append(2) # IMAGERIGHT
  obj.feedbackMapping.append(1) # LEFT
  obj.feedbackMapping.append(0) # REST
  obj.feedbackMapping.append(2) # RIGHT


# initialization of the engine. Need to be done here to run preproc before the scanning
def initEngine(subjid,runnum):

   obj.useEngine = useEngine
   obj.dry_run = dry_run     
   obj.dispLogData = dispLogData
   print('Connecting to the engine\n')
   obj.connectEngine()
   print('Configuring the Engine\n')
   obj.configureEngine()
   study_params(subjid,runnum) 
   print('Starting initial processes\n')
   obj.startEngine()


############ code to run during feedback
def run_loop():
  
    runExit = False
	   # stat the scanning. Here we need to put the code to send the signal to the scanner
    obj.start() 
    while not runExit:
        # pygame stuff 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
		# if we have new volume		
        if (obj.hasNewVolume()):
		   # act accordingly
           obj.changeInternalState()
        else:
		   # just refresh display (right now just clear display after cue presentation)
           obj.refreshDisplay()
		   
        if (obj.endScan()):
           return;


############ give study params to FRIENDengine 
def study_params(subjid,runnum=1):
   
   # set the study directory
   obj.engine.setVariable('StudyDir', datadir);

   # path to study design file 
   obj.engine.setVariable('Design', designfilepath);

   # set the subject ID
   obj.engine.setVariable('Subject', subjid);

   # path to subject's anatomical file
   obj.engine.setVariable('RAI', 'outputdirrai.nii');   

   # path to subject's single functional volume 
   obj.engine.setVariable('RFI', 'outputdirrfi.nii');   

   # number of functional volumes
   obj.engine.setVariable('FuncVolumes', nfuncvolumes);
  
   # baseline condition
   obj.engine.setVariable('BaselineCondition',baselinecond);
  
   # where are the raw fmri vols from the scanner
   obj.engine.setVariable('Prefix', rawdatapath);

   # changing the activation level
   obj.engine.setVariable('ActivationLevel', activationLevel);

   # suffix for this run
   obj.engine.setVariable('CurrentRunSuffix', 'RUN0' + str(runnum));   



#########  get subjid 
def getSubjID():

  subjid = raw_input('subject id: ')
  print('\nyou entered: '+subjid+'\n')
  return subjid


#########  get subjid 
def getRunnum():

  runnum = raw_input('run number: ')
  print('\nyou entered: '+runnum+'\n')
  return runnum



#########  main function
if __name__ == '__main__':    

  print '\nstarting main function...\n'

  initDisplayObj()

  subjid=getSubjID()

  runnum=getRunnum()

  if (useEngine):
    initEngine(subjid,runnum)

  # run the main loop
  run_loop() 

  # engine finalization code  
  if (useEngine):
    obj.processEndRun()
   
  # finalizing pygame and script
  pygame.quit()
  quit()

