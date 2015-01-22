#!/usr/bin/env python


import os
import time
import sys

try:
    w = open("/dev/argus_ups", "w", 0)

except Exception, e:
    print "Failed to open watchdog"
    raise

pid = os.fork()
if pid == 0:
    while 1:
        print "Petting watchdog"
        w.write("\n")
        time.sleep(10)

print "Process ID:", pid
