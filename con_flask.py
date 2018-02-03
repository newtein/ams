import subprocess as sub
import time


p = sub.Popen(['arp'],stdout=sub.PIPE,stderr=sub.PIPE)
output, errors = p.communicate()
row=output.split("                  ")
print row
print errors
