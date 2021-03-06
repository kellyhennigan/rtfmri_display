"""Utilities for starting a scan and collecting pulse timings (to do)"""
import re
#import serial
import sys, signal, time, os
from datetime import datetime


def alphanum_key(entry, only_digits=False):
    """
    DICOM filenames are numerically sequential, but not zero-padded.
    The SFTP server gives us a list of files in "sorted" order, but
    that means the files are not in sequential order. Fix that here.
    """
    converted_parts = []
    fname = entry.split()[-1]
    parts = re.split("([0-9]+)", fname)
    for part in parts:
        if part.isdigit():
            converted_parts.append(int(part))
        else:
            if not only_digits:
                converted_parts.append(part)
    return converted_parts

def _get_device():
    
    # get the name of the operating system
    user_os=sys.platform

    # mac
    if user_os == 'darwin':
        device = '/dev/tty.usbmodem123451'
    
    # windows
    elif user_os=='windows':
        #should be a COM port (eg. COM 4)
        raise Exception("Not tested on windows.")
    
    # linux
    else:
         device = '/dev/ttyACM1'
    
    return device

def start_scanner():
    """Send the start scan trigger to the scanner."""

    #user_os='darwin'
    device = _get_device()
    
    if not os.path.exists(device):
        sys.stderr.write("ERROR: Serial device %r not found!\n\n" % (device))
        return 1

    ser = serial.Serial(device, 115200, timeout=1)
    #time.sleep(0.05)

    # Send an out pulse
    print("\n\n\nsending pulse to start scanner now...")
    ser.write('[t]\n');
    ser.close()
    pulsetime=datetime.now()
    print("done.\n\n\n")
    return pulsetime
