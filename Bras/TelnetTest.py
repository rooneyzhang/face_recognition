import logging
import telnetlib
import time
import re

username = 'olt_check'
password = '3L3ygScS'

class TelnetClient():
    def __init__(self,):
        self.tn = telnetlib.Telnet()

    # 此函数实现telnet登录主机
    def login_host(self,host_ip,username,password):
        try:
            # self.tn = telnetlib.Telnet(host_ip,port=23)
            self.tn.open(host_ip,port=23)
        except:
            logging.warning('%s网络连接失败'%host_ip)
            return False
        # 等待login出现后输入用户名，最多等待10秒
        self.tn.read_until(b'login: ',timeout=10)
        self.tn.write(username.encode('ascii') + b'\n')
        # 等待Password出现后输入用户名，最多等待10秒
        self.tn.read_until(b'Password: ',timeout=10)
        self.tn.write(password.encode('ascii') + b'\n')
        # 延时两秒再收取返回结果，给服务端足够响应时间
        time.sleep(2)
        # 获取登录结果
        # read_very_eager()获取到的是的是上次获取之后本次获取之前的所有输出
        command_result = self.tn.read_very_eager().decode('ascii')
        if 'Login incorrect' not in command_result:
            logging.warning('%s登录成功'%host_ip)
            return True
        else:
            logging.warning('%s登录失败，用户名或密码错误'%host_ip)
            return False

    # 此函数实现执行传过来的命令，并输出其执行结果
    def execute_some_command(self,command):
        result=""
        # 执行命令
        self.tn.write(command.encode('ascii')+b'\n')
        time.sleep(2)
        # 获取命令结果
        command_result = self.tn.read_very_eager().decode('ascii')
        result=command_result
        logging.warning('命令执行结果：\n%s' % command_result)
        while True:
            if command_result.__contains__("---- More"):
                command=" "
                self.tn.write(command.encode('ascii') + b'\n')
                time.sleep(2)
                command_result = self.tn.read_very_eager().decode('ascii')
                logging.warning('命令执行结果：\n%s' % command_result)
                result=result+'\r\n'+command_result
                result=result.replace("---- More ( Press 'Q' to break ) ----","")
            elif command_result.__contains__("#"):
                print("over")
                break
            else :
                break
        return  result.replace("---- More ( Press 'Q' to break ) ---- ","")



    # 退出telnet
    def logout_host(self):
        self.tn.write(b"exit\n")


def cm_connect(host):
    ne = {}
    ne['ip'] = host
    ne['connect'] = 0
    telnet_client = TelnetClient()
    # 如果登录结果返加True，则执行命令，然后退出
    if telnet_client.login_host(host_ip, username, password):
        command = 'enable'
        telnet_client.execute_some_command(command)
        command = 'config'
        ne['client'] = telnet_client
        ne['connect'] = 1

    return ne


def dis_connect(ne):
    client = ne['client']
    ne['connect']=0
    client.logout_host()



def check_autofind(ne,ontsn):
    if ne['connect']!=1:
        ne=cm_connect(ne['ip'])
    client=ne['client']
    command="display ont autofind  all"
    res=client.execute_some_command(command)
    res=res.replace('\r', '').replace('\n', '')
    a=res.find(ontsn)
    if a:
        pon=res[a-55:a]
        print(pon)
        pattern = re.compile(r"(\d{1,2})\/(\d{1,2})\/(\d{1,3})", re.I)
        m = pattern.search(pon)
        if m:
            list=m.group(0).strip().split(r'/')
            ne['frame'] = list[0]
            ne['slot']=list[1]
            ne['port']=list[2]
            ne['gpon'] = m.group(0).strip()
            print("-------------"+a)
    return  res.find(ontsn)






if __name__ == '__main__':
    host_ip = '10.192.7.22'
    ontsn="48575443F57AF29B"
    ne=cm_connect(host_ip)
    if check_autofind(ne,ontsn):
        print('自动发现')
    else :
        print('未发现ONT')
    dis_connect(ne)
