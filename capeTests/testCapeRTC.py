#!/usr/bin/env python


import os
import time
import sys

ret = 0

try:
    d = open("/sys/bus/i2c/devices/i2c-2/delete_device", "w")
    d.write("0x68")
    d.close()
except Exception, e:
    pass

try:
    n = open("/sys/bus/i2c/devices/i2c-2/new_device", "w")
    n.write("ds1307 0x68")
    n.close()
except Exception, e:
    print "Exception creating clock", e
    ret = 1

for i in range(20):
    ret = os.system("/sbin/hwclock -w -f /dev/rtc1")
    if ret:
        print "Attempt:", i, "Error returned from hwclock:", ret
        time.sleep(1)
    else:
        print "Success on attempt:", i
        break


t = os.popen("/sbin/hwclock -f /dev/rtc1").read()

timeDiff = time.mktime(time.strptime(t[:31], "%a %d %b %Y %I:%M:%S %p %Z")) - time.time()
print "Time difference between Argus cape RTC and system:", timeDiff

if abs(timeDiff) > 1:
    print "Greater than 1 second is an error"
    ret = 1
else:
    print "Test passed"


sys.exit(ret)
