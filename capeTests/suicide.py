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
    print "Petting watchdog quickly to force suicide shutdown"
    while 1:
        w.write("\n")
        time.sleep(0.01)

print "Process ID:", pid
