import all_func as af
import psycopg2 as p
import schedule, time,os
from datetime import datetime


con = p.connect("dbname='NZ' user='harshit'")


TIME = [['walkin','02:00:00','02:45:00'],['walkout','03:00:00','07:00:00']]

def job():
    global TIME
    date = datetime.now().strftime("%d%m%Y")
    filename="macrecord.xml"
    current_time = datetime.now().strftime("%H:%M:%S")
    print(current_time,TIME[1][1],TIME[0][2])
    if current_time >= TIME[0][1] and current_time <= TIME[0][2]:
    	    print(current_time,TIME[0][0])
            os.system("sudo nmap -sP 172.16.100.0/24 -oX "+filename)
            af.mac_parser(filename,TIME[0][0],con)
    elif current_time >= TIME[1][1] and current_time <= TIME[1][2]:
            print(current_time,TIME[1][0])
            os.system('sudo nmap -sP 172.16.100.0/24 -oX ' + filename)
            af.mac_parser(filename, TIME[1][0],con)
    elif (current_time>TIME[0][2] and current_time<TIME[1][1]):
        s1 = current_time
        s2 = TIME[1][1]
        FMT = '%H:%M:%S'
        tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
        print(tdelta.seconds)
        time.sleep(int(tdelta.seconds))
    elif (current_time>TIME[1][2] or current_time<TIME[0][1]):
        s1 = current_time
        s2 = TIME[0][1]
        FMT = '%H:%M:%S'
        tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
        print(tdelta.seconds)
        time.sleep(int(tdelta.seconds))


schedule.every(2).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(10)


'''import subprocess as sub
import sys
import time





p = sub.Popen(['nmap','-sP','192.168.54.0/24'],stdout=sub.PIPE,stderr=sub.PIPE)
output, errors = p.communicate()
print output
print errors
time.sleep(20)'''
