import sys
import paramiko as pm
import os
import re
import time
import BrasCatch
import traceback
import six
import packaging
import packaging.version
import packaging.specifiers
import packaging.requirements


def loadDatadet(infile):
    f=open(infile,'r')
    sourceInLine=f.readlines()
    dataset=[]
    for line in sourceInLine:
        temp1=line.strip('\n')
        dataset.append(temp1)
    f.close()
    return dataset

try:
    log=open(r'D:\Python\2018\Bras\log1.txt', 'w')
    log.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')

    infile=r'D:\Python\BrasIP1.txt'
    brasList=loadDatadet(infile)
    for bras in brasList:
        print(bras)
        BrasCatch.GetLog(bras)

    log.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    log.close()


except Exception  as e:
    log.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    log.write(str(Exception))
    traceback.print_exc()
    log.write(traceback.format_exc())
    log.close()




