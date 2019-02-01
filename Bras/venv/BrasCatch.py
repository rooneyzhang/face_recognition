import sys
import paramiko as pm
import os
import re
import threading
import time
import redis
import myTime

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
    ne['starthour'] = str(starthour)
    ne['endhour'] = endhour

    f = open('D:\\Python\\2018\\Bras\\OUT\\' + host + '.txt', 'w')

    client = pm.SSHClient()
    # client.load_system_host_keys()
    client.set_missing_host_key_policy(pm.AutoAddPolicy())
    client.connect(host, port=22, username=USER, password=PASSWORD)
    channel = client.invoke_shell()
    stdin = channel.makefile('w')
    stdout = channel.makefile('r')
    stdin.write(''' 
            screen-length 0 t

             ''')
    count = 0
    try:
        while True:
            text_line = stdout.readline()
            if text_line:
                print(text_line)
                f.write(text_line)
                pattern = re.compile(r"\<(.+)\>", re.I)
                text_line = text_line.strip().replace('\r', '').replace('\n', '')
                m = pattern.match(text_line)
                if m:
                    ne['name'] = m.group(1).strip().split()[0]
                    print(ne['name'])

                if text_line.find(">") != -1 and text_line.find("screen-length") == -1:
                    if count > 0:
                        break;
                    else:
                        count = count + 1
            else:
                break
    finally:
        print(" Connected ")

    r = redis.Redis(host='111.1.13.42', port=6380, db=0, password='3L3ygScS')
    ne['r'] = r
    ne['f'] = f
    ne['client'] = client
    ne['stdin'] = stdin
    ne['stdout'] = stdout
    return ne


def dis_connect(ne):
    f = ne['f']
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']
    r = ne['r']

    stdout.close()
    stdin.close()
    client.close()
    f.close()


def disp_arp(ne):
    f = ne['f']
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']
    starthour = ne['starthour']
    endhour = ne['endhour']
    r = ne['r']
    stdin.write('''screen-length 0 t
           disp arp all
           ''')
    try:
        while True:
            text_line = stdout.readline()
            if text_line:
                # print(type(text_line), text_line)
                print(text_line)
                f.write(text_line)
                pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\w{4}\-\w{4}\-\w{4})\s+(.*)", re.I)
                m = pattern.match(text_line)
                if m:
                    updatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    ip = m.group(1).strip().split()[0]
                    mac = m.group(2).strip().split()[0]
                    other = m.group(3).strip()
                    # print(mac)
                    r.hmset('mac:' + mac, {'ip': ip, 'bras_onu_ip': ip, 'update_time': updatetime})
                    r.expire('mac:' + mac, 864000)
                    '''
                    pattern = re.compile(r"(\d+)\s+\S+\s+(\S+)\s*(\S*)", re.I)
                    pattern2 = re.compile(r"\S+\s+(\S+)\s*(\S*)", re.I)
                    n = pattern.match(other)
                    n2 = pattern2.match(other)
                    if n:
                        ttl=n.group(1).strip()
                        instance=n.group(2).strip()
                        vpn=n.group(3).strip()

                    elif n2:
                        instance = n2.group(1).strip()
                        vpn = n2.group(2).strip()
                    if (mac and ip):
                        r.set('ip:%s:%s' %(vpn,ip),mac)
                        r.expire('ip:%s:%s' %(vpn,ip), 864000)
                        #print(myTime.now_to_timestamp())
                        #r.zadd('ip_mac:%s:%s' %(vpn,ip),mac,print(myTime.now_to_timestamp()))
                        #r.expire('ip_mac:%s:%s' %(vpn,ip), 864000)
                        #r.zadd('mac_ip:%s' % (mac), '%s:%s' %(vpn,ip), print(myTime.now_to_timestamp()))
                        #r.expire('mac_ip:%s' % (mac), 864000)
                        '''
                if (text_line.find("Total:") != -1 and text_line.find("Dynamic:") != -1) or (
                        text_line.find("Error:") != -1):
                    break;
            else:
                break
    finally:
        print(" disp arp all over ")


def disp_normal_offline_record(ne):
    f = ne['f']
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']
    starthour = ne['starthour']
    endhour = ne['endhour']
    r = ne['r']
    stdin.write(''' disp aaa normal-offline-record time ''' + starthour + ':00:00 ' + endhour + ''':00:00 brief

           ''')
    try:
        while True:
            text_line = stdout.readline()
            if text_line:
                # print(type(text_line), text_line)
                print(text_line)
                f.write(text_line)
                pattern = re.compile(r"\d+\s+(\w+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\w{4}\-\w{4}\-\w{4})", re.I)
                text_line = text_line.strip().replace('\r', '').replace('\n', '')
                m = pattern.match(text_line)
                if m:
                    updatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    account = m.group(1).strip().split()[0]
                    ip = m.group(2).strip().split()[0]
                    mac = m.group(3).strip().split()[0]
                    print("account:" + account + "\t ip:" + ip + "\t mac:" + mac)

                    if (account and mac and ip):
                        r.set('r:' + account, mac)
                        r.hmset('mac:' + mac, {'bras_account': account, 'bras_user_ip': ip, 'update_time': updatetime,
                                               'record_type': 'normal_offline'})
                        r.expire('mac:' + mac, 2592000)

                if text_line.find("Total:") != -1 or text_line.find("Error:") != -1 or (
                        text_line.find(">") != -1 and text_line.find("disp") == -1):
                    print("======")
                    print(text_line)
                    break;
            else:
                break
    finally:
        print(" disp aaa normal-offline-record ")


def disp_offline_record(ne):
    f = ne['f']
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']
    starthour = ne['starthour']
    endhour = ne['endhour']
    r = ne['r']
    stdin.write(''' disp aaa offline-record time ''' + starthour + ':00:00 ' + endhour + ''':00:00 brief
    
           ''')
    try:
        while True:
            text_line = stdout.readline()
            if text_line:
                # print(type(text_line), text_line)
                print(text_line)
                f.write(text_line)
                pattern = re.compile(r"\d+\s+(\w+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\w{4}\-\w{4}\-\w{4})", re.I)
                text_line = text_line.strip().replace('\r', '').replace('\n', '')
                m = pattern.match(text_line)
                if m:
                    updatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    account = m.group(1).strip().split()[0]
                    ip = m.group(2).strip().split()[0]
                    mac = m.group(3).strip().split()[0]
                    # print("mac:%s \t ip:%s \t account:%s" %(mac,ip,account))
                    if (account and mac and ip):
                        r.set('r:' + account, mac)
                        print('mac:' + mac)
                        r.hmset('mac:' + mac, {'bras_account': account, 'bras_user_ip': ip, 'update_time': updatetime,
                                               'record_type': 'offline'})
                        r.expire('mac:' + mac, 2592000)

                if text_line.find("Total:") != -1 or text_line.find("Error:") != -1 or (
                        text_line.find(">") != -1 and text_line.find("disp") == -1):
                    print("1")
                    break;
            else:
                break
    finally:
        print(" disp aaa offline-record ")


def disp_domain_user(ne):
    f = ne['f']
    client = ne['client']
    stdout = ne['stdout']
    stdin = ne['stdin']
    starthour = ne['starthour']
    endhour = ne['endhour']
    r = ne['r']
    stdin.write(''' 
           screen-length 0 t
             disp domain
           ''')
    list = []
    try:
        while True:
            text_line = stdout.readline()
            if text_line:
                print(text_line)
                f.write(text_line)
                pattern = re.compile(r"\s+(\S+)\s+Active\s+\d+\s+\d+\s+(\d+)\s", re.I)
                m = pattern.match(text_line)
                if m:
                    list.append(m.group(0).strip().split()[0])
                if text_line.find("Total") != -1 or text_line.find("Error:") != -1:
                    break;
            else:
                break
    finally:
        print("2 over")

    for domain in list:
        stdin.write('display access-user domain ' + domain + '\n')
        try:
            while True:
                text_line = stdout.readline()
                if text_line:
                    print(text_line)
                    f.write(text_line)
                    pattern = re.compile(
                        r"(\d+)\s+(\S+?)\s+(\S+)\s+(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\s+(\w{4}-\w{4}-\w{4})", re.I)
                    text_line = text_line.strip().replace('\r', '').replace('\n', '')
                    m = pattern.match(text_line)
                    if m:
                        updatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        bras_user_id = m.group(1).strip().split()[0]
                        bras_account = m.group(2).strip().split()[0]
                        bras_trunk = m.group(3).strip().split()[0]
                        bras_user_ip = m.group(4).strip().split()[0]
                        mac = m.group(5).strip().split()[0]
                        # print("mac:%s \t ip:%s \t account:%s" %(mac,ip,account))

                        if (bras_account and mac):
                            r.set('r:' + bras_account, mac)
                            r.expire('r:' + bras_account, 2592000)

                            r.hmset('mac:' + mac,
                                    {'bras_account': bras_account, 'bras_user_ip': bras_user_ip,
                                     'update_time': updatetime,
                                     'domain': domain, 'bras_user_id': bras_user_id, 'bras_trunk': bras_trunk,
                                     'bras_ip': ne['ip'],
                                     'timer': myTime.now_to_timestamp(), 'bras_name': ne['name']})
                            r.expire('mac:' + mac, 2592000)

                            # r.set('ip:%s:%s' %(domain,bras_user_ip), mac)

                            #add mac2 and r2
                            pattern = re.compile(r"(\S+)\.(\d+)")
                            m = pattern.match(bras_trunk)
                            if m:
                                trunk = m.group(1).strip().split()[0]
                                trunknum = m.group(2).strip().split()[0]
                                if(int(trunknum)>10000):
                                    trunk=trunk+'.'+str(int(int(trunknum)/10000))
                                    oltlist=r.get("bras_olt:%s:%s" %(ne['ip'],trunk))
                                    if(oltlist):
                                        list = oltlist.decode().split(',')
                                        oltip=""
                                        for olt in list:
                                            if r.hget("mac2:"+olt+":"+mac,'olt_update_time'):
                                                oltip=olt
                                                break

                                        if oltip!='':
                                            r.set('r2:' + bras_account, oltip+':'+mac)
                                            r.expire('r2:' + bras_account, 2592000)

                                            r.hmset('mac2:'+oltip+':'+mac,
                                                    {'bras_account': bras_account, 'bras_user_ip': bras_user_ip,
                                                     'update_time': updatetime,
                                                     'domain': domain, 'bras_user_id': bras_user_id,
                                                     'bras_trunk': bras_trunk,
                                                     'bras_ip': ne['ip'],
                                                     'timer': myTime.now_to_timestamp(), 'bras_name': ne['name']})
                                            r.expire('mac2:'+oltip+':'+mac, 2592000)


                    if text_line.find("Total users") != -1 or text_line.find(" No online user") != -1:
                        break;
                else:
                    break
        finally:
            print(domain + " over")


def GetLog(HOST):
    ne = cm_connect(HOST)
    disp_normal_offline_record(ne)
    disp_offline_record(ne)
    disp_arp(ne)
    disp_domain_user(ne)
    #disp_online_fail_record(ne)
    dis_connect(ne)