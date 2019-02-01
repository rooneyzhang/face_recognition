import sys
import paramiko as pm
import os
import re
import threading
import traceback
import time



USER = 'zhangyang13566291600'
PASSWORD = 'zhangyang!123'


def cm_connect(host):
    ne = {}
    ne['ip'] = host
    ne['connect'] = 0

    endhour = time.strftime("%H", time.localtime());
    starthour = 0
    if int(endhour) > 0:
        starthour = int(endhour) - 1
    else:
        endhour='1'
    ne['starthour'] = str(starthour)
    ne['endhour'] = endhour

    client = pm.SSHClient()
    # client.load_system_host_keys()
    client.set_missing_host_key_policy(pm.AutoAddPolicy())
    client.connect(host, port=22, username=USER, password=PASSWORD)
    channel = client.invoke_shell()
    stdin = channel.makefile('w')
    stdout = channel.makefile('r')
    ne['connect'] = 1
    ne['client'] = client
    ne['stdin'] = stdin
    ne['stdout'] = stdout
    return ne


def dis_connect(ne):
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']
    stdin.write(''' 
           screen-length 0 t
           ''')

    stdout.close()
    stdin.close()
    client.close()


def disp_arp(ne):
    f = open('D:\\Python\\2018\\Bras\\OUT\\' + ne['ip'] + '#disp_arp.txt', 'w')
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']
    stdin.write(''' 
           screen-length 0 t
           disp arp all
           ''')
    try:
        while True:
            text_line = stdout.readline()
            if text_line:
                #print(text_line)
                f.write(text_line)

                if (text_line.find("Total:") != -1 and text_line.find("Dynamic:") != -1) or ( text_line.find("Error:") != -1 ):
                    break;
            else:
                break
    finally:
        f.close()
        print(" disp arp all over ")


def disp_normal_offline_record(ne):
    f = open('D:\\Python\\2018\\Bras\\OUT\\' + ne['ip'] + '#disp_normal_offline_record.txt', 'w')
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']
    starthour = ne['starthour']
    endhour = ne['endhour']
    stdin.write(''' 
           screen-length 0 t
            disp aaa normal-offline-record time ''' + starthour + ':00:00 ' + endhour + ''':00:00 brief
           ''')
    try:
        while True:
            text_line = stdout.readline()
            if text_line:
                #print(text_line)
                f.write(text_line)
                if text_line.find("Total:") != -1 or text_line.find("Error:") != -1 :
                    break;
            else:
                break
    finally:
        f.close()
        print(" disp aaa normal-offline-record ")


def disp_offline_record(ne):
    f = open('D:\\Python\\2018\\Bras\\OUT\\' + ne['ip'] + '#disp_offline_record.txt', 'w')
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']
    starthour = ne['starthour']
    endhour = ne['endhour']
    stdin.write(''' 
           screen-length 0 t
            disp aaa offline-record time ''' + starthour + ':00:00 ' + endhour + ''':00:00 brief
           ''')
    try:
        while True:
            text_line = stdout.readline()
            if text_line:
                #print(text_line)
                f.write(text_line)
                if text_line.find("Total:") != -1 or text_line.find("Error:") != -1 :
                    break;
            else:
                break
    finally:
        f.close()
        print(" disp aaa offline-record ")

def disp_online_fail_record(ne):
    f = open('D:\\Python\\2018\\Bras\\OUT\\' + ne['ip'] + '#disp_online_fail_record.txt', 'w')
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']
    starthour = ne['starthour']
    endhour = ne['endhour']
    stdin.write(''' disp aaa online-fail-record time ''' + starthour + ':00:00 ' + endhour + ''':00:00 brief
           ''')
    try:
        while True:
            text_line = stdout.readline()
            if text_line:
                #print(text_line)
                f.write(text_line)
                if text_line.find("Total:") != -1 or text_line.find("Error:") != -1  or text_line.find(">") != -1:
                    break;
            else:
                break
    finally:
        f.close()
        print(" disp aaa offline-record ")

def disp_domain_user(ne):
    f = open('D:\\Python\\2018\\Bras\\OUT\\' + ne['ip'] + '#disp_domain_user.txt', 'w')
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']

    list = []
    try:
        stdin.write(''' 
                screen-length 0 t
                  disp domain
                ''')
        while True:
            text_line = stdout.readline()
            if text_line:
                #print(text_line)
                f.write(text_line)
                pattern = re.compile(r"\s+(\S+)\s+Active\s+\d+\s+\d+\s+(\d+)\s", re.I)
                m = pattern.match(text_line)
                if m:
                    list.append(m.group(0).strip().split()[0])
                    continue
                if text_line.find("Total") != -1 or text_line.find("Error:") != -1 :
                    break;
            else:
                break
    except Exception  as e:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        f.write(str(Exception))
        traceback.print_exc()
        f.write(traceback.format_exc())

    finally:
        print("disp domain over")

    for domain in list:
        stdin.write('display access-user domain ' + domain + '\n')
        f.write("=========="+domain+" START=========="+'\n')
        try:
            while True:
                text_line = stdout.readline()
                if text_line:
                    #print(text_line)
                    f.write(text_line)

                    if text_line.find("Total users") != -1 or text_line.find(" No online user") != -1  or text_line.find("Info:") != -1:
                        break;
                else:
                    break
        finally:
            f.write("==========" + domain + " END==========" + '\n')
            print(domain + " over")

    f.close()


def GetLog(HOST):
    ne=cm_connect(HOST)
    disp_normal_offline_record(ne)
    disp_offline_record(ne)
    disp_arp(ne)
    disp_domain_user(ne)
    dis_connect(ne)


def loadDatadet(infile):
    f = open(infile, 'r')
    sourceInLine = f.readlines()
    dataset = []
    for line in sourceInLine:
        temp1 = line.strip('\n')
        dataset.append(temp1)
    f.close()
    return dataset



log=open(r'D:\Python\2018\Bras\BrasLog.txt', 'w')
log.write("start:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')

infile=r'D:\Python\BrasIP1.txt'
brasList=loadDatadet(infile)
threads = []
for bras in brasList:
    print(bras)
    #GetLog(bras)
    t = threading.Thread(target=GetLog, args=(bras,))
    threads.append(t)

if __name__ == '__main__':
    try:
        for t in threads:
            t.setDaemon(True)
            t.start()

        for t in threads:
            t.join()
        log.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        log.close()
    except Exception  as e:
        log.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        log.write(str(Exception))
        traceback.print_exc()
        log.write(traceback.format_exc())
        log.close()



#log.write("End:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
#log.close()


