import struct
import time
import socket

mcast_group_ip = '234.2.2.2'
mcast_group_port = 23456


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
            print(
                f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}: Receive data from {addr}: {message.decode()}')
        except:
            print("while receive message error occur")


if __name__ == "__main__":
    receiver()

# coding:utf-8,

# ANY = '0.0.0.0'
# MCAST_ADDR = '224.168.2.9'
# MCAST_PORT = 1600

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
#                      socket.IPPROTO_UDP)  # 创建UDP socket
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许端口复用
# sock.bind((ANY, MCAST_PORT))  # 绑定监听多播数据包的端口
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,
#                 255)  # 告诉内核这是一个多播类型的socket
# status = sock.setsockopt(socket.IPPROTO_IP,  # 告诉内核把自己加入指定的多播组，组地址由第三个参数指定
#                          socket.IP_ADD_MEMBERSHIP,
#                          socket.inet_aton(MCAST_ADDR) + socket.inet_aton(ANY))

# sock.setblocking(0)
# ts = time.time()
# while 1:
#     try:
#         data, addr = sock.recvfrom(1024)
#     except:
#         pass
#     else:
#         print("We got data!")
#         print("FROM: ", addr)
#         print("DATA: ", data)
