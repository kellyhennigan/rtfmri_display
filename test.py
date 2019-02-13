from visualizers import *

#initializing object
obj = Thermometer()
#set the baseline condition
obj.setBaseline("REST")
#read design file
# designfile="/home/cniuser/rt/exp_display/design181120.txt"
designfile="/Users/kelly/neurofeedback/rt/exp_display/design181218.txt"
subjid="subj006"
obj.readDesignFile(designfile)

obj.feedbackMapping = []

# Here we are building an array that maps the condition index to the correct feedback value. The conditions are sorted in alphabetical order
obj.feedbackMapping.append(1) # IMAGELEFT
obj.feedbackMapping.append(2) # IMAGERIGHT
obj.feedbackMapping.append(1) # LEFT
obj.feedbackMapping.append(0) # REST
obj.feedbackMapping.append(2) # RIGHT


useEngine = True # to use the engine (so thermometer fluctuates based on fmri data)
dry_run = True  # if dry_run equals True, the scanner will NOT be triggered

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

def study_paramsHacks(option=1):
   
   # set the study directory
   obj.engine.setVariable('StudyDir', '/home/cniuser/rt/data');   

   # set the subject ID
   obj.engine.setVariable('Subject', subjid)

   # path to subject's anatomical file
   obj.engine.setVariable('RAI', 'outputdirrai.nii');   

   # path to subject's single functional volume 
   obj.engine.setVariable('RFI', 'outputdirrfi.nii');   

   # path to study design file 
   obj.engine.setVariable('Design', designfile)

   # changing the directory of the volumes
   obj.engine.setVariable('Prefix', '/home/cniuser/rt/FriendEngine/Friend_Engine_Sources/Friend_Engine_Sources/Application/output_scans/serie04' + os.path.sep + 'vol_');   

   # changing the activation level
   obj.engine.setVariable('ActivationLevel', '0.01');   

   # changing the current suffix
   obj.engine.setVariable('CurrentRunSuffix', 'RUN0' + str(option));   

# initialization of the engine. Need to be done here to run preproc before the scanning
if (useEngine):
   obj.useEngine = useEngine
   obj.dry_run = dry_run     
   print('Connecting to the engine\n')
   obj.connectEngine()
   print('Configuring the Engine\n')
   obj.configureEngine()
   study_paramsHacks() 
   print('Starting initial processes\n')
   obj.startEngine()

# run the main loop
run_loop() 

# engine finalization code  
if (useEngine):
   obj.processEndRun()
   
# finalizing pygame and script
pygame.quit()
quit()

