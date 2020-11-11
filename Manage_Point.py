import socket
import sys
import time
import json
from lfsr.db import *
from lfsr import *
import hashlib
import random
import rsa
import filewrite
import fileread            # 从文件中读取字典
from normal_node import *  # 导入思远的代码


class ManagePoint(normal_node):
    def __init__(self):
        super().__init__()
        dic = fileread.read(
            "Information/Priviate_info/manager_info/manager_info.txt")
        self.__prekey = dic["prekey"]    # 当前层密钥
        self.__class = dic["class"]          # 当前层与下一层ID
        self.__commuinfo = dic["connectinfo"]  # 父节点、管辖的群组、直接连接的下一层节点的通信信息
        self.__userkeys = dic["userkeys"]    # 存储连接的普通节点的私钥信息

    def infoupdate(self):
        dic = {}
        dic["prekey"] = self.__prekey
        dic["class"] = self.__class
        dic["connectinfo"] = self.__commuinfo
        dic["userkeys"] = self.__userkeys
        filewrite.write(
            "Information/Priviate_info/manager_info/manager_info.txt", dic)
        dic = {}
        dic["ID"] = self.ID
        dic["pkey"] = self.pkey
        dic["vector"] = self.vector
        dic["intz"] = self.intz
        dic["gc"] = self.gc
        dic["groupkey"] = self.groupkey
        filewrite.write(
            "Information/Priviate_info/self_info/self_into.txt", dic)

    def Monitor(self):
        # 监控函数
        Maxsize = 1024*16
        udp_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_port = ("", message_port)
        udp_recv.bind(ip_port)
        try:
            while 1:
                data, client_addr = udp_recv.recvfrom(Maxsize)
                data = data.decode("utf-8")
                client_addr = client_addr[0]
                try:
                    if eval(data)[0] == "Register":
                        self.adduser(eval(data)[1], client_addr)
                    elif eval(data)[0] == "Retreat":
                        self.deluser(eval(data), 2)
                except:
                    print("Ineffective request")
        except:
            udp_recv.close()

    def keysend(self, user, key, encryptkey=0):
        content = str(key).encode('utf-8')
        crypto = rsa.encrypt(content, encryptkey)
        try:
            send(user, msg=crypto, port=key_port)
        except:
            print("Ineffective request")

    def adduser(self, info, ip):
        '''新成员加入小组'''
        List = fileread.read(
            "Information/Priviate_info/manager_info/userlist.txt")
        if info in List:
            send(ip, msg=b"UserID have been used! Please Change another one")
        else:
            print("adduesr:", info)
            print("ip:", ip)
            List.append(info)
            filewrite.write(
                "Information/Priviate_info/manager_info/userlist.txt", List)
            tmp = random.randint(1, 100)       # 访问控制多项式更新Z
            newZ = LFSR(tmp) ^ int(round(time.time()*1000))
            tmp = random.randint(100, 200)       # 访问控制多项式更新k
            newk = LFSR(tmp) ^ int(round(time.time()*1000))
            s = None
            s = secretkey()                 # 私钥生成函数
            self.__commuinfo["Group"][info] = ip
            self.__userkeys[info] = s
            for i in range(4):
                time.sleep(1)
                send(ip, msg=b"Ask for pubkeyforencrypt")
            pubkey = self.keyreceive()
            pubkey = rsa.PublicKey.load_pkcs1(pubkey)
            time.sleep(4)
            self.keysend(ip, s, pubkey)  # 将生成的私钥返还给注册者
            H = []
            for s in self.__userkeys.values():
                H.append(int(sha2(s+str(newZ)), 16))
            accesscontrol = [1, -H[0]]
            for i in range(1, len(H)):
                tmp = accesscontrol.copy()
                for j in range(1, len(accesscontrol)):
                    accesscontrol[j] += -1*H[i]*tmp[j-1]
                accesscontrol.append(-1*tmp[len(accesscontrol)-1] * H[i])
            accesscontrol[-1] += newk
            self.vector = accesscontrol
            self.intz = newZ
            self.infoupdate()
            time.sleep(5)
            self.Grouppublicinfodistribute(
                str((accesscontrol, self.intz, self.ID)))
            print("register complete!")

    def Grouppublicinfodistribute(self, info):
        userlist = fileread.read(
            "Information/Priviate_info/manager_info/userlist.txt")
        for user in userlist:
            for i in range(4):
                time.sleep(1)
                send(self.__commuinfo["Group"][user], msg=info.encode("utf-8"))

    def deluser(self, info, Type=1):
        '''删除群成员'''
        if Type != 1:
            try:
                clock = int(round(time.time()*1000))
                clock_check = eval(info[2][0])
                if clock-clock_check > 1000*60:
                    print("Out of time")
                    return 0
                ip = self.__commuinfo["Group"][info[1]]
                for i in range(4):
                    time.sleep(1)
                    send(ip, msg=b"Ask for pubkeyforverify")
                pubkey = self.keyreceive()
                pubkey = rsa.PublicKey.load_pkcs1(pubkey)
                if not rsa.verify(info[2][0].encode(
                        "utf-8"), info[2][1], pubkey):
                    print("ineffective reteat request")
                    return 0
                else:
                    info = info[1]
            except:
                print("ineffective reteat request")
                return 0
        List = fileread.read(
            "Information/Priviate_info/manager_info/userlist.txt")
        List.remove(info)
        filewrite.write(
            "Information/Priviate_info/manager_info/userlist.txt", List)
        tmp = random.randint(1, 100)       # 访问控制多项式更新Z
        newZ = LFSR(tmp) ^ int(round(time.time()*1000))
        tmp = random.randint(100, 200)       # 访问控制多项式更新k
        newk = LFSR(tmp) ^ int(round(time.time()*1000))
        s = None
        s = self.__userkeys[info]  # 用户私钥搜索函数
        del self.__commuinfo["Group"][info]
        del self.__userkeys[info]
        H = []
        for s in self.__userkeys.values():
            H.append(int(sha2(s+str(newZ)), 16))
        if len(H) > 0:
            accesscontrol = [1, -H[0]]
            for i in range(1, len(H)):
                tmp = accesscontrol.copy()
                for j in range(1, len(accesscontrol)):
                    accesscontrol[j] += -1*H[i]*tmp[j-1]
                accesscontrol.append(-1*tmp[len(accesscontrol)-1] * H[i])
        else:
            accesscontrol = [1]
        accesscontrol[-1] += newk
        self.vector = accesscontrol
        self.intz = newZ
        self.infoupdate()
        time.sleep(4)
        self.Grouppublicinfodistribute(
            str((accesscontrol, self.intz)))


def LFSR(m):
    n = 64
    taps = max_len_lfsr_min_taps[n]
    poly = taps_to_poly(taps)
    prng = lfsr_ef(poly)
    for i in range(m):
        p = next(prng)
    return p


def receive(path):
    message = fileread.read(path)
    return message


def secretkey():
    value = random.randint(1000000000, 9999999999)
    return sha2(str(value))


T0 = ManagePoint()
# T0.Monitor()
# T0.node_registration("192.168.43.80")
T0.infoupdate()
msg = T0.group_session_key_calculation()
print("accesscontrol:", T0.vector)
print("intZ:", T0.intz)
print("key:", msg)
