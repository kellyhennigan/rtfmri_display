"""High-levelest level visualization class for functional data that wraps
   a full scanner interface."""
import pdb
import sys, time
import math
import signal
import os
import logging
from random import randint, random
from time import sleep

import pygame
import numpy as np
import matplotlib.pyplot as plt
from friendEngine import Engine;
from utilities import start_scanner

logger = logging.getLogger(__name__)

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

# object that handles one experiment block info
class designBlock(object):
    startBlock = 0
    endBlock = 0
    condition = ""
		
    def indexInBlock(self, index):
        return (index >= self.startBlock) and (index <= self.endBlock)
		
    def display(self):
        print("%.3d-%.3d,%s" % (self.startBlock, self.endBlock, self.condition))

# object that handles the design information of an experiment		
class design(object):
    blockList = []
    actualBlock  = -1;
    baselineCondition=""
    conditions = []	
	
    def readFile(self, filename):
        self.blockList = []; 
        file = open(filename, 'r') 
        self.conditions = [];		
        for line in file:
            line = line.strip()		
            if len(line) > 0:
               block = designBlock()
               parts = line.split(',')
               block.condition = parts[1]
               self.conditions.append(block.condition)			   
               parts = parts[0].split('-')
               block.startBlock = int(parts[0])			   
               block.endBlock = int(parts[1])			   
               self.blockList.append(block)		  
        self.conditions = list(set(self.conditions))
        self.conditions.sort()
		
    def displayBlocks(self):
        for block in self.blockList:
            block.display()

    def getBlock(self, volumeIndex):
        for i in range(len(self.blockList)):
            if (self.blockList[i].indexInBlock(volumeIndex)):
                return i
        return -1
		
    def getConditionIndex(self, volumeIndex):
        i = self.getBlock(volumeIndex)	
        if (i > -1):
           i = self.conditions.index(self.blockList[i].condition)
        return i;
		
    def setActualBlock(self, volumeIndex):
        self.actualBlock = self.getBlock(volumeIndex) 
 
    def validBlockIndex(self, index): 		
        return (index > -1 ) and (index < len(self.blockList))

    def actualCondition(self):
        if self.validBlockIndex(self.actualBlock):
            return self.blockList[self.actualBlock].condition	
		
    def restBlock(self):
        return (self.actualCondition() == self.baselineCondition)
			
    def activationBlock(self):
        return (self.actualCondition() != self.baselineCondition)
		
    def blockStart(self, volumeIndex):
        block = self.getBlock(volumeIndex)
        if self.validBlockIndex(block):
           return self.blockList[block].startBlock == volumeIndex
        return False;

    def blockEnd(self, volumeIndex):
        block = self.getBlock()
        if self.validBlockIndex(block):
           return self.blockList[block].endBlock == volumeIndex
        return False;
		
    #verifies if the given volumeIndex is the last one
    def scanEnd(self, volumeIndex):
        return self.blockList[len(self.blockList)-1].endBlock == volumeIndex
	
class Visualizer(object):
    """Given an interface that gives you volumes,
       visualize something about those volumes"""

    def __init__(self, timeout=0):
        self.state = 0
        self.timeout = timeout
        self.alive = True
        self.setup_exit()

    def setup_exit(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, sig, frame):
        print("Exiting the visualizer gracefully")
        self.halt()

    def get_volume(self, *args, **kwargs):
        """Gather new information from the interface, ie get volumes"""
        return True

    def update_state(self):
        """Any visualizer will need a function to update its internal
           representation of the data it's gathering from the interface"""
        new_volume = self.get_volume()
        # state never changes in base class
        self.state = self.state

        # sleep(self.timeout)

    def draw(self):
        """ Function to actually handle updating the screen"""
        pass

    def run(self):
        """structure of main run"""
        while self.alive:
            self.update_state()
            self.draw()
        self.halt()

    def halt(self):
        """Halt command"""
        self.alive = False

    def __del__(self):
        self.halt()


class RoiVisualizer(Visualizer):
    """Class that assumes you want to use a masking object"""

    def __init__(self, timeout=0):

        super(RoiVisualizer, self).__init__(timeout)
        # keep track of the ROI's information over time.
        self.roi_tc = []
        self.nvol = 0
        self.TR = 2

    def start_timer(self):
        self.start = time.time()
        self.last_time = self.start

    def log_times(self):
        n = len(self.roi_tc)
        toc = time.time()
        start_diff = toc - self.start
        last_diff  = toc - self.last_time
        volume_collected = self.start + self.nvol * self.TR - 2
        lag = toc - volume_collected

        self.last_time = toc
        print("Time since start: {}".format(start_diff ))
        print("Time since last: {}".format(last_diff))
        print("Average since start: {}".format(start_diff/n))
        print("Lag: {}".format(lag))

    def update_state(self):
        logger.debug("Fetching volume...")
        vol = self.get_volume()
        self.nvol += 1
        roi_mean = self.masker.reduce_volume(vol)
        self.roi_tc.append(roi_mean)
        self.state = roi_mean

class TextVisualizer(RoiVisualizer):
    """
    Most basic visualizer. Prints out the newest ROI
    """
    def draw(self):
        print(self.roi_tc)
        self.log_times()

class GraphVisualizer(RoiVisualizer):
    """
    Very basic visualizer that graphs ROI average time course in real time
    """
    def __init__(self, timeout=0):
        super(GraphVisualizer, self).__init__(timeout)
        plt.ion()
        self.old_n = 0
        self.tic = time.time()

    def draw(self):
        n = len(self.roi_tc)

        #x = 2*range(2, n-1)
        x = range(1, n)
        y = []
        if n > 1:
            y = self.roi_tc[1:]

        self.log_times()
        plt.plot(x, y)

        plt.xlabel('time (s)')
        plt.ylabel('ROI activation - Raw')
        plt.title('Neurofeedback!!!')
        plt.grid(True)
        #plt.savefig("test.png")
        plt.show()

        plt.pause(0.1)



class PyGameVisualizer(RoiVisualizer):
    """ Handle pygame setup"""
    designObj = design()
    engine = Engine()
    cueDisplayTime=1
    cueDisplaying=False
    useEngine = False
    dispLogData = True
    delay = 1
    feedbackMapping = []
	
    def __init__(self, TR=2, timeout=0):
        super(PyGameVisualizer, self).__init__(timeout)
        self.bg_color = (0, 0, 0)
        self.clock = pygame.time.Clock()
        self.state = 0
        self.tic = 0
        self.rate = 100
        self.period = 2000  # how often to refresh state
        self.pygame_live = False
        self.TR = 2
        self.lastVolumeIndex=-1
        self.lastBlockStartTime=0
        self.dry_run = True

    def setBaseline(self, condition):
        self.designObj.baselineCondition = condition

    def readDesignFile(self, filename):
        self.designObj.readFile(filename)
		
    def halt(self):
        self.alive = False
        if self.pygame_live:
            pygame.display.quit()
            pygame.quit()
            self.pygame_live = False

    def loadFont(self, fontName='Comic Sans MS', size=30):
        self.myfont = pygame.font.SysFont(fontName, size)

    def start_display(self, width=800, height=600, title='NeuroFeedback'):
        pygame.init()
        display_width, display_height = (int(width), int(height))
        self.display_width = display_width;
        self.display_height = display_height;
        self.screen = pygame.display.set_mode((display_width, display_height), pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self.loadFont()
        self.pygame_live = True

    def text_objects(self, text, color=white):
        textSurface = self.myfont.render(text, True, color)
        return textSurface, textSurface.get_rect()
    
    def start(self):
        self.lastVolumeIndex = -1
        self.startTime = time.time()
        if not self.dry_run:
            start_scanner()
            print("STARTED SCANNER")
        if (not self.pygame_live):
            self.start_display()
        if self.dispLogData:
            self.loadvalsfromlogfile()

    def loadvalsfromlogfile(self):
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
        self.logdatavals=fbval1     
        print('log data vals: ')
        print(self.logdatavals)

    def connectEngine(self):
        # creating the main socket variable
        self.engine.connectEngine();

        # creating a session and getting sessionID
        self.engine.createSession();
        print("sessionID received = %s" % (self.engine.sessionID));

    # right now its rigged to the an example scanned. We need to generalize it
    def configureEngine(self, option=1, plugInType=3, additionalFeedbacks = 1):
        # initiating processing
        self.engine.doTrain = False
        self.engine.doGLM = True
        self.engine.doFeatureSelection = True
        self.engine.additionalFeedbacks = additionalFeedbacks
        self.engine.setPlugInInformation(plugInType)
        self.engine.phase = 1
        self.engine.actualVolume = 1

	# call the finalization engine steps
    def processEndRun(self):
        self.engine.processEndRun()
		
    def processPhase(self, feedbackRun=True):
        self.engine.processPhase(feedbackRun)
	
	# only leave the loop when the preproc phase is finished
    def startEngine(self, feedbackRun=True):
        while (self.engine.phase != 2):
            self.engine.processPhase(feedbackRun, True);
            time.sleep(self.engine.TR / 7)
        self.engine.processPhase(feedbackRun, True);

    def actualVolumeIndex(self):
        return ((time.time() - self.startTime) // self.TR) + 1
		
    def hasNewVolume(self):
        actualIndex = self.actualVolumeIndex()
        if (actualIndex > self.lastVolumeIndex):
           self.lastVolumeIndex = actualIndex
           return True
        else:
           return False

    def displayCue(self):
        self.clearDisplay()
        self.message_display(self.designObj.actualCondition())
        self.cueDisplaying = True
		
    def clearDisplay(self, color=black):
        self.screen.fill(color) 
       	
    def message_display(self, text):
        TextSurf, TextRect = self.text_objects(text)
        TextRect.center = ((self.display_width/2),(self.display_height/2))
        self.screen.blit(TextSurf, TextRect)
        pygame.display.update()

    def refreshDisplay(self):
        if (self.cueDisplaying) and ((time.time()-self.lastBlockStartTime) > self.cueDisplayTime):
           self.clearDisplay()
           self.message_display(" ")
           self.cueDisplaying = False

    def displayActivation(self):
        return True
		
	# verifies the scan end
    def endScan(self):
        return self.designObj.scanEnd(self.actualVolumeIndex())
		
    def changeInternalState(self):	
        index = self.actualVolumeIndex()
        if (self.designObj.blockStart(index)):
           self.lastBlockStartTime = time.time()
           self.designObj.setActualBlock(index)
           self.displayCue()
        else:
           if (not self.cueDisplaying) and (self.designObj.activationBlock()):
              self.displayActivation()              

class Thermometer(PyGameVisualizer):
    """ The first fully functional visualizer that actually does something.
        Maintains a thermometer displayed on screen consisting of a red
        box that moves up and down a range corresponding to numbers 1 to 100.

        TODO: refactor the ugly
    """

    def __init__(self, timeout=0):
        super(Thermometer, self).__init__(timeout)
        self.temp = 50
        self.max_move = 100

    def _center_rect(self, width, height):
        sw, sh = self.screen.get_size()
        center_y = (sh - height)//2
        center_x = (sw - width) // 2
        return (center_x, center_y)

    def _get_wh(self):
        sw, sh = self.screen.get_size()
        w = sw*.1//1
        h = sh*.7//1
        return (w, h)

    def draw_box(self):
        box_color = (255, 253, 251)
        w, h = self._get_wh()
        x, y = self._center_rect(w, h)
        xywh = (x, y, w, h)
        self.xywh = xywh
        pygame.draw.rect(self.screen, box_color, xywh, 4)

    def displayActivation(self):
        self.screen.fill(self.bg_color)
        self.draw_box()
        print('useEngine: ')
        print(self.useEngine)
        print('dispLogData: ')
        print(self.dispLogData)
        
        if (not self.useEngine):
            if self.dispLogData:
                val = self.logdatavals.pop(0)
                self.temp = float(val)
                print("Value to display: %f " % self.temp);
                self._draw_temp()
            else:
                print("displaying random values")
                self.update_temp(random)
        else:
    	    # this delay is necessary because we do not have access to the actual scan. It will only be avaiable after Tr seconds plus the transfer and conversion time
            self.engine.actualVolume = self.actualVolumeIndex() - self.delay
            if (self.engine.actualVolume > 0):
                classe, self.temp, otherResponses = self.engine.getFeedbackValue()
                condIndex = self.designObj.getConditionIndex(self.engine.actualVolume)
                print("self.temp : %s " % self.temp);
                print("otherResponses[0]: %s " % str(otherResponses[0]));
                if self.feedbackMapping[condIndex] == 2:
                    self.temp = otherResponses[0];
                self.temp = max(min(float(self.temp), 1), 0) * 100.0
                print("Value chosen : %f " % self.temp);
                self._draw_temp()
            else:
                self.temp = 0
        pygame.display.flip()
		
    def run(self, random=False):
        mainloop = True

        while mainloop:
            # Limit frame speed to 50 FPS
            self.clock.tick(self.rate)
            self.tic += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mainloop = False
                elif event.type == pygame.VIDEORESIZE:
                    self.draw_box()

            # Redraw the background
            self.screen.fill(self.bg_color)
            self.draw_box()
            self.update_temp(random)
            pygame.display.flip()

    def _draw_temp(self):
        sw, sh = self.screen.get_size()
        w = int(sw*.1//1) - 6 + 1
        h = int(sh*.05//1)
        top_y = (sh - self.xywh[3])//2
        bottom_y = (sh - self.xywh[3])//2 + self.xywh[3] - h
        x = int((sw - self.xywh[2]) // 2) + 3
        target_y = top_y + int(((bottom_y - top_y) * (100-self.temp)/100)//1)
        if not hasattr(self, 'old_y'):
            self.old_y = target_y
        if self.old_y == target_y:
            if random() > .5:
                target_y += randint(-10, 10)
        diff = target_y - self.old_y
        if abs(diff) > self.max_move:
            y = self.old_y + self.max_move if diff > 0 else self.old_y - self.max_move
        else:
            y = target_y

        if y < top_y:
            y = top_y
            print(self.temp)
        if y > bottom_y:
            y = bottom_y
        self.blob = pygame.draw.rect(self.screen, (255, 0, 0), (x, y, w, h), 0)
        self.old_y = y

    def update_temp(self, random=False):
        if not random:
            self.temp = self.get_temp()
            logger.debug("New temp = {}".format(self.temp))
        else:
            # get a random temperature
            self.temp = self.get_random_temp()
        self._draw_temp()

    def get_temp(self):
        self.update_state()
        buffer_size = 5
        if len(self.roi_tc) > buffer_size:
            start_ind = max(len(self.roi_tc) - buffer_size, 0)
            mean = np.mean(self.roi_tc)
            std = np.std(self.roi_tc)
            temp = 50 + 25 * ((self.state - mean) / std)
            return temp
        else:
            return self.temp

    def get_random_temp(self):
        if self.tic % (self.period//self.rate) == 0:
            return max(min(self.temp + randint(-20, 20), 90), 10)
        else:
            return self.temp
