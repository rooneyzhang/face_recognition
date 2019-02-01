import sys
import os
import re
import threading
import time
import redis
import myTime
import traceback



def disp_domain_user(host):
    r = redis.Redis(host='111.1.13.42', port=6380, db=0, password='3L3ygScS')
    f = open('D:\\Python\\2018\\Bras\\OUT\\' +host + '#disp_domain_user.txt', 'r')
    lines = f.readlines()
    f.close()
    list = []
    bras_name=''
    domain=''
    level=1
    if lines[0]:
        pattern = re.compile(r"\<(.+)\>", re.I)
        text_line = lines[0].strip().replace('\r', '').replace('\n', '')
        m = pattern.match(text_line)
        if m:
            bras_name = m.group(1).strip().split()[0]
            print(bras_name)
    try:
        for inx, text_line in enumerate (lines):
            if text_line:
                #print(text_line)
                if level==1:
                    pattern = re.compile(r"\s+(\S+)\s+Active\s+\d+\s+\d+\s+(\d+)\s", re.I)
                    m = pattern.match(text_line)
                    if m:
                        list.append(m.group(0).strip().split()[0])
                        continue
                    if text_line.find("Total") != -1 or text_line.find("Error:") != -1:
                        level = 2
                        continue
                elif   level == 2 :
                    pattern = re.compile(r"==========(\S+) START==========", re.I)
                    m = pattern.match(text_line)
                    if m:
                        domain=m.group(0).strip().split()[0].replace("=","")
                        print(host+"   "+domain)
                        level=3
                        continue
                elif level == 3:
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
                        #print("mac:%s \t  account:%s" %(mac,bras_account))

                        if (bras_account and mac):
                            r.set('r:' + bras_account, mac)
                            r.expire('r:' + bras_account, 2592000)

                            r.hmset('mac:' + mac,
                                    {'bras_account': bras_account, 'bras_user_ip': bras_user_ip,
                                     'update_time': updatetime,
                                     'domain': domain, 'bras_user_id': bras_user_id, 'bras_trunk': bras_trunk,
                                     'bras_ip': host,
                                     'timer': myTime.now_to_timestamp(), 'bras_name': bras_name})
                            r.expire('mac:' + mac, 2592000)
                            # r.set('ip:%s:%s' %(domain,bras_user_ip), mac)

                            # add mac2 and r2
                            pattern = re.compile(r"(\S+)\.(\d+)")
                            m = pattern.match(bras_trunk)
                            if m:
                                trunk = m.group(1).strip().split()[0]
                                trunknum = m.group(2).strip().split()[0]
                                if (int(trunknum) > 10000):
                                    trunk = trunk + '.' + str(int(int(trunknum) / 10000))
                                    oltlist = r.get("bras_olt:%s:%s" % (host, trunk))
                                    if (oltlist):
                                        list = oltlist.decode().split(',')
                                        oltip = ""
                                        if len(list)>1:
                                            for olt in list:
                                                if r.hget("mac2:" + olt + ":" + mac, 'olt_update_time'):
                                                    oltip = olt
                                                    break
                                        else :
                                            oltip=list[0]

                                        if oltip != '':
                                            r.set('r2:' + bras_account, oltip + ':' + mac)
                                            r.expire('r2:' + bras_account, 2592000)

                                            r.hmset('mac2:' + oltip + ':' + mac,
                                                    {'bras_account': bras_account, 'bras_user_ip': bras_user_ip,
                                                     'update_time': updatetime,
                                                     'domain': domain, 'bras_user_id': bras_user_id,
                                                     'bras_trunk': bras_trunk,
                                                     'bras_ip':host,
                                                     'timer': myTime.now_to_timestamp(), 'bras_name': bras_name})
                                            r.expire('mac2:' + oltip + ':' + mac, 2592000)
                        continue
                    pattern = re.compile(r"==========(\S+) END==========", re.I)
                    m = pattern.match(text_line)
                    if m:
                        level = 2
                        continue
            else:
                break

    finally:
        print(host+"    disp domain over")


def disp_arp(host):
    r = redis.Redis(host='111.1.13.42', port=6380, db=0, password='3L3ygScS')
    f = open('D:\\Python\\2018\\Bras\\OUT\\' +host + '#disp_arp.txt', 'r')
    lines = f.readlines()
    f.close()
    if lines[1]:
        pattern = re.compile(r"\<(.+)\>", re.I)
        text_line = lines[1].strip().replace('\r', '').replace('\n', '')
        m = pattern.match(text_line)
        if m:
            bras_name = m.group(1).strip().split()[0]
            print(host+"   "+bras_name)
    try:
        for inx, text_line in enumerate(lines):
            if text_line:
                # print(type(text_line), text_line)
                # print(text_line)
                # f.write(text_line)
                pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\w{4}\-\w{4}\-\w{4})\s+(.*)", re.I)
                m = pattern.match(text_line)
                if m:
                    updatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    ip = m.group(1).strip().split()[0]
                    mac = m.group(2).strip().split()[0]
                    other = m.group(3).strip()
                    #print(mac)
                    r.hmset('mac:' + mac, {'ip': ip, 'bras_onu_ip': ip, 'update_time': updatetime})
                    #r.expire('mac:' + mac, 864000)
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
                    continue
                if (text_line.find("Total:") != -1 and text_line.find("Dynamic:") != -1) or (
                        text_line.find("Error:") != -1):
                    break;
            else:
                break
    finally:
        print(host+"  disp arp all over ")

def disp_normal_offline_record(host):
    r = redis.Redis(host='111.1.13.42', port=6380, db=0, password='3L3ygScS')
    f = open('D:\\Python\\2018\\Bras\\OUT\\' +host + '#disp_normal_offline_record.txt', 'r')
    lines = f.readlines()
    f.close()
    if lines[0]:
        pattern = re.compile(r"\<(.+)\>", re.I)
        text_line = lines[0].strip().replace('\r', '').replace('\n', '')
        m = pattern.match(text_line)
        if m:
            bras_name = m.group(1).strip().split()[0]
            print(host+"   "+bras_name)
    try:
        for inx, text_line in enumerate(lines):
            if text_line:
                # print(type(text_line), text_line)
                #print(text_line)
                #f.write(text_line)
                pattern = re.compile(r"\d+\s+(\w+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\w{4}\-\w{4}\-\w{4})", re.I)
                text_line = text_line.strip().replace('\r', '').replace('\n', '')
                m = pattern.match(text_line)
                if m:
                    updatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    account = m.group(1).strip().split()[0]
                    ip = m.group(2).strip().split()[0]
                    mac = m.group(3).strip().split()[0]
                    #print("account:" + account + "\t ip:" + ip + "\t mac:" + mac)

                    if (account and mac and ip):
                        r.set('r:' + account, mac)
                        r.hmset('mac:' + mac, {'bras_account': account, 'bras_user_ip': ip, 'update_time': updatetime,
                                               'record_type': 'normal_offline'})
                        #r.expire('mac:' + mac, 2592000)

                if text_line.find("Total:") != -1 or text_line.find("Error:") != -1 :
                    break;
            else:
                break
    finally:
        print(host+"  disp_normal_offline_record ")


def disp_offline_record(host):
    r = redis.Redis(host='111.1.13.42', port=6380, db=0, password='3L3ygScS')
    f = open('D:\\Python\\2018\\Bras\\OUT\\' +host + '#disp_offline_record.txt', 'r')
    lines = f.readlines()
    f.close()
    if lines[0]:
        pattern = re.compile(r"\<(.+)\>", re.I)
        text_line = lines[0].strip().replace('\r', '').replace('\n', '')
        m = pattern.match(text_line)
        if m:
            bras_name = m.group(1).strip().split()[0]
            print(host+"   "+bras_name)
    try:
        for inx, text_line in enumerate(lines):
            if text_line:
                # print(text_line)
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
                        #print('mac:' + mac)
                        r.hmset('mac:' + mac, {'bras_account': account, 'bras_user_ip': ip, 'update_time': updatetime,
                                               'record_type': 'offline'})
                        #r.expire('mac:' + mac, 2592000)

                if text_line.find("Total:") != -1 or text_line.find("Error:") != -1 :
                    break;
            else:
                break
    finally:
        print(host+"  disp_offline_record ")

def Log2Reids(HOST):
    disp_domain_user(HOST)
    disp_arp(HOST)
    disp_offline_record(HOST)
    disp_normal_offline_record(HOST)

def loadDatadet(infile):
    f = open(infile, 'r')
    sourceInLine = f.readlines()
    dataset = []
    for line in sourceInLine:
        temp1 = line.strip('\n')
        dataset.append(temp1)
    f.close()
    return dataset

log=open(r'D:\Python\2018\Bras\Bras2DB_log.txt', 'w')
log.write("start:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')

infile=r'D:\Python\BrasIP1.txt'
brasList=loadDatadet(infile)
threads = []
for bras in brasList:
    print(bras)
    #Log2Reids(bras)
    t = threading.Thread(target=Log2Reids, args=(bras,))
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
