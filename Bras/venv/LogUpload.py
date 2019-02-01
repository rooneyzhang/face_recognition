import paramiko
import os
import sys
import threading
import time

def getdir(filepath):
    filelist=[]
    #遍历filepath下所有文件，包括子目录
    files = os.listdir(filepath)
    for fi in files:
        fi_d = os.path.join(filepath,fi)
        if not os.path.isdir(fi_d):
            filelist.append(fi)

    return  filelist

log=open(r'D:\Python\2018\Bras\upload.txt', 'w')
log.write("Start:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
remotepath='/root/perl/bras/OUT/'
localpath='D:\\Python\\2018\Bras\\OUT\\'
print(localpath)
filelist=getdir(localpath)

transport = paramiko.Transport(('192.168.13.33', 22))
transport.connect(username='root', password='*WO^sYsy^3L3yg')

sftp = paramiko.SFTPClient.from_transport(transport)  # 如果连接需要密钥，则要加上一个参数，hostkey="密钥"

for fi in filelist:
    print(fi)
    log.write(fi+'\n')
    sftp.put(localpath+fi ,remotepath + fi)  # 将本地的Windows.txt文件上传至服务器/root/Windows.txt
transport.close()  # 关闭连接

log.write(":"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
log.close()