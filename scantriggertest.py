import sys, signal, time, os
from datetime import datetime
from utilities import start_scanner

pulsetime = start_scanner()
cmd = 'echo scan trigger time: '+str(pulsetime)+' >> afile'
os.system(cmd)