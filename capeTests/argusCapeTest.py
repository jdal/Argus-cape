#!/usr/bin/env python


import time
import os
import sys
import signal
import fcntl


# Globals

error = 0
leds = 0
flash = 0
phase = 0


def wioctl(fd, req, arg): # Extension of ioctl to ignore exceptions
    try:
        fcntl.ioctl(fd, req, arg)
    except:
        pass
    


def alarmSigHandler(signum, frame):
    global leds, phase, error, flash
    if error:                   # Flash the error
        flash ^= 0xF
        wioctl(wdog, 10002, 0xF0 | (error & flash)) 
    else:
        phase += 1
        if (phase % 5) == 0:
            leds = (leds + 1) & 0xF
            wioctl(wdog, 10002, 0xF0 | leds) 

def hupSigHandler(signum, frame):
    return;

# Signal handler for UPS notification

def ioSigHand(signum, frame):
    print "Halting system in 5 seconds due to signal"
    time.sleep(5)
    os.system("halt")

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0) # Unbuffered stdout for journald
wdog = open("/dev/argus_ups", "r+", 0) # Must open watchdog unbuffered
wioctl(wdog, 10002, 0xF0)              # Turn off all leds
fcntl.fcntl(wdog, fcntl.F_SETOWN, os.getpid()) # Register our process with the driver...
fcntl.fcntl(wdog, fcntl.F_SETFL, # and tell it we need notification
    fcntl.fcntl(wdog, fcntl.F_GETFL) | fcntl.FASYNC)
                
# Test cape Real-time clock
if not os.path.exists("/dev/rtc1"): # If no rtc, try and make one
    try:
        d = open("/sys/bus/i2c/devices/i2c-2/delete_device", "w")
        d.write("0x68")
        d.close()
    except Exception, e:
        pass                        # It's OK if we can't delete it

    try:
        n = open("/sys/bus/i2c/devices/i2c-2/new_device", "w")
        n.write("ds1307 0x68")
        n.close()
    except Exception, e:
        print "Exception creating clock", e
        error = 0xA;                # Both Red LEDs on - no device

    time.sleep(1);                  # Wait a second for i2c device to settle

try:
    t1 = time.mktime(time.strptime(os.popen("/sbin/hwclock -f /dev/rtc1").read()[:31],
                                   "%a %d %b %Y %I:%M:%S %p %Z"))
    print t1        
    
    time.sleep(10)        # Wait ten seconds, then check clock is ticking
    
    t2 = time.mktime(time.strptime(os.popen("/sbin/hwclock -f /dev/rtc1").read()[:31],
                                "%a %d %b %Y %I:%M:%S %p %Z"))
    print t2
    timeDiff = t2 - (t1 + 10)

    print "10 second time difference from rtc1:", timeDiff

    if abs(timeDiff) > 1:
        print "Greater than 1 second is an error"
        error = 0x02            # Error in clock timing - red LED 1
    else:
        print "Test passed"
except Exception, e:
    print "Exception", e
    error = 0x08                # General timing error - red LED 2



signal.signal(signal.SIGHUP, hupSigHandler)
signal.signal(signal.SIGALRM, alarmSigHandler)
signal.signal(signal.SIGIO, ioSigHand)   # Register shutdown signal handler

signal.setitimer(signal.ITIMER_REAL, 0.2, 0.2) # Start 5Hz flash timer


while 1:
    wdog.write('\n')            # Pet watchdog every second
    time.sleep(1)
    
