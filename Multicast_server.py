import struct
import time
import socket

mttl = 10

# 组播组IP和端口
mcast_group_ip = '234.2.2.2'
mcast_group_port = 23456


def sender():
    addrinfo = socket.getaddrinfo(mcast_group_ip, None)[0]
    # 建立发送socket，和正常UDP数据包没区别
    send_sock = socket.socket(
        addrinfo[0], socket.SOCK_DGRAM)
    ttl_bin = struct.pack('@i', mttl)
    if addrinfo[0] == socket.AF_INET:
        send_sock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    else:
        send_sock.setsockopt(socket.IPPROTO_IPV6,
                             socket.IPV6_MULTICAST_HOPS, ttl_bin)
    # 每十秒发送一遍消息
    while True:
        message = "([1,23,3],2)"
        # 发送写法和正常UDP数据包的还是完全没区别
        # 猜测只可能是网卡自己在识别到目的ip是组播地址后，自动将目的mac地址设为多播mac地址
        send_sock.sendto(message.encode("utf-8"),
                         (addrinfo[4][0], mcast_group_port))
        print(
            f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}: message send finish')
        time.sleep(2)


if __name__ == "__main__":
    sender()

# # coding:utf-8,
# import socket
# import time

# ANY = '0.0.0.0'
# SENDERPORT = 1501
# MCAST_ADDR = '224.168.2.9'
# MCAST_PORT = 1600

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.bind((ANY, SENDERPORT))  # 绑定发送端口到SENDERPORT，即此例的发送端口为1501
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)  # 设置使用多播发送
# while 1:
#     # 将'hello world'发送到多播地址的指定端口，属于这个多播组的成员都可以收到这个信息
#     sock.sendto(b'Hello World', (MCAST_ADDR, MCAST_PORT))
#     time.sleep(10)
