import rsa
import random
import hashlib
import fileread
import filewrite
import socket
import time
import struct

# large_integer_p=9209
# hash256@hashlib
group_size_n = 35

# 组播地址
mcast_group_ip = '234.2.2.2'

mttl = 10

# 端口列表
message_port = 12345
key_port = 12346
mcast_group_port = 23456


timeout = 60
socket.setdefaulttimeout(timeout)


class normal_node:
    def __init__(self):
        dic = fileread.read(
            "Information/Priviate_info/self_info/self_into.txt")
        self.ID = dic["ID"]
        self.pkey = dic["pkey"]
        self.vector = dic["vector"]
        self.intz = dic["intz"]
        self.gc = dic["gc"]
        self.groupkey = dic["groupkey"]
        try:
            with open("Information/Priviate_info/self_info/pubkeyforencrypt.pem", "rb") as f:
                p = f.read()
                self.pubkeyforencrypt = rsa.PublicKey.load_pkcs1(p)
            with open("Information/Priviate_info/self_info/privkeyfordecrypt.pem", "rb") as f:
                p = f.read()
                self.privkeyfordecrypt = rsa.PrivateKey.load_pkcs1(p)
            with open("Information/Priviate_info/self_info/pubkeyforverify.pem", "rb") as f:
                p = f.read()
                self.pubkeyforverify = rsa.PublicKey.load_pkcs1(p)
            with open("Information/Priviate_info/self_info/privkeyforsign.pem", "rb") as f:
                p = f.read()
                self.privkeyforsign = rsa.PrivateKey.load_pkcs1(p)
        except:
            self.pubkeyforencrypt = None
            self.privkeyfordecrypt = None
            self.pubkeyforverify = None
            self.privkeyforsign = None
            self.signkeycreate()
            self.sharekeycreate()

    def sharekeycreate(self):
        '''层间共享密钥生成函数rsa算法生成密钥'''
        (pubkey, privkey) = rsa.newkeys(1024)
        self.pubkeyforencrypt = pubkey
        self.privkeyfordecrypt = privkey
        with open("Information/Priviate_info/self_info/pubkeyforencrypt.pem", "wb+") as f:
            f.write(pubkey.save_pkcs1())
        with open("Information/Priviate_info/self_info/privkeyfordecrypt.pem", "wb+") as f:
            f.write(privkey.save_pkcs1())

    def signkeycreate(self):
        (pubkey, privkey) = rsa.newkeys(1024)
        self.pubkeyforverify = pubkey
        self.privkeyforsign = privkey
        with open("Information/Priviate_info/self_info/pubkeyforverify.pem", "wb+") as f:
            f.write(pubkey.save_pkcs1())
        with open("Information/Priviate_info/self_info/privkeyforsign.pem", "wb+") as f:
            f.write(privkey.save_pkcs1())

    def keyreceive(self):
        # 密钥接收函数
        Maxsize = 1024*16
        udp_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_port = ("", key_port)
        udp_recv.bind(ip_port)
        try:
            data, client_addr = udp_recv.recvfrom(Maxsize)
            del client_addr
        except:
            print("Link lose")
            data = None
        udp_recv.close()
        return data

    def group_session_key_calculation(self):
        # 计算群会话密钥
        # 访问控制多项式构造方式为 f(x) = (x-hash(s0,z))(x-hash(s1,z))...(x-hash(sn,z))+k
        # 考虑访问控制多项式 f(x)=a0x^n+a1x^(n-1)+...+an 的存储方式为 [a0,a1,...,an]
        # 此时只需令 x = hash(si,z) 带入计算即可得到群会话密钥 k 的值
        group_session_key = self.vector[-1]
        hash_num = int(sha2(self.pkey+str(self.intz)), 16)
        for i in range(1, len(self.vector)):
            group_session_key += self.vector[-(i+1)]*pow(hash_num, i)
        self.groupkey = group_session_key
        filewrite.write(
            "Information\Priviate_info\self_info\group_key.txt", group_session_key)
        return group_session_key

    def public_info_receiving(self):
        # 此处也需要一个控件
        # 更新acp系数向量和随机整数
        Maxsize = 1024*16
        udp_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_port = ("", message_port)
        udp_recv.bind(ip_port)
        try:
            msg, client_addr = udp_recv.recvfrom(Maxsize)
            del client_addr
            self.vector = eval(msg)[0]
            self.intz = eval(msg)[1]
            self.gc["USER_ID"] = eval(msg)[2]
        except:
            print("Link lose")
        udp_recv.close()
        return 0

    def node_registration(self, your_gc):
        # 注册新节点，赋予随机私钥
        # new_public_key=去找gc注册
        # self.pkey = new_private_key
        send(ip=your_gc, msg=str(("Register", self.ID)).encode("utf-8"))
        Maxsize = 1024*16
        udp_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_port = ("", message_port)
        udp_recv.bind(ip_port)
        try:
            while 1:
                data, client_addr = udp_recv.recvfrom(Maxsize)
                data = data.decode("utf-8")
                client_addr = client_addr[0]
                if data == "Ask for pubkeyforencrypt":
                    for i in range(4):
                        time.sleep(1)
                        send(your_gc, msg=self.pubkeyforencrypt.save_pkcs1(),
                             port=key_port)
                    pkey = self.keyreceive()
                    udp_recv.close()
                    break
                else:
                    continue
            pkey = rsa.decrypt(pkey, self.privkeyfordecrypt)
            self.pkey = pkey.decode("utf-8")
            self.gc["IP"] = your_gc
            self.public_info_receiving()
        except:
            udp_recv.close()
        return 0

    def node_retreat(self):
        # 节点撤销
        message = str((self.ID, int(round(time.time()*1000))))
        tmpmessage = self.info_signature(message)
        message = ("Retreat", self.ID, (message, tmpmessage))
        gc = self.gc["IP"]
        send(gc, msg=str(message).encode("utf-8"))
        Maxsize = 1024*16
        udp_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_port = ("", message_port)
        udp_recv.bind(ip_port)
        while 1:
            data, client_addr = udp_recv.recvfrom(Maxsize)
            data = data.decode("utf-8")
            client_addr = client_addr[0]
            if data == "Ask for pubkeyforverify":
                time.sleep(6)
                send(gc, msg=self.pubkeyforverify.save_pkcs1(),
                     port=key_port)
                udp_recv.close()
                break

    def info_signature(self, message):
        content = message.encode("utf-8")
        signed_message = rsa.sign(content, self.privkeyforsign, "SHA-1")
        return signed_message


def send(ip="127.0.0.1", Type=4, msg=b"", port=message_port):
    udp_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if Type == 0:
        msg = b"Ask for layor key"
    elif Type == 1:
        msg = b"Ask for initkeygeneration"
    elif Type == 2:
        msg = b"Ask for init"
    else:
        pass
    udp_send.sendto(msg, (ip, port))
    udp_send.close()


def sha2(value):
    if type(value) != str:
        value = str(value)
    hash_object = hashlib.sha256()
    hash_object.update(value.encode("utf-8"))
    hash_value = hash_object.hexdigest()
    return hash_value


def sender(message):
    addrinfo = socket.getaddrinfo(mcast_group_ip, None)[0]
    send_sock = socket.socket(
        addrinfo[0], socket.SOCK_DGRAM)
    ttl_bin = struct.pack('@i', mttl)
    if addrinfo[0] == socket.AF_INET:
        send_sock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    else:
        send_sock.setsockopt(socket.IPPROTO_IPV6,
                             socket.IPV6_MULTICAST_HOPS, ttl_bin)
    count = 0
    while 1:
        count += 1
        send_sock.sendto(message.encode("utf-8"),
                         (addrinfo[4][0], mcast_group_port))
        if count >= 4:
            break
        time.sleep(5)


def receiver():
    addrinfo = socket.getaddrinfo(mcast_group_ip, None)[0]
    sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", mcast_group_port))
    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    mreq = group_bin+struct.pack("=I", socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    while True:
        try:
            message, addr = sock.recvfrom(1024)
            return message.decode("utf-8")
        except:
            print("while receive message error occur")
