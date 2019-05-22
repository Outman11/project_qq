"""
    Chat room
    env:python3.5
    socket fork 练习
"""

from socket import *
import os, sys

# 服务器地址
ADDR = ("0.0.0.0", 9535)
# 存储用户信息
user = {}


def do_login(s, name, addr):
    """
        登录及进入聊天室处理
    :param s:数据报套接字
    :param name:进入聊天室人的姓名
    :param addr:进入聊天室客户端地址
    :return:
    """
    if name in user or "管理员" in name:  # 如果姓名存在字典或者名字里存在管理员字段都提醒用户存在
        s.sendto("该用户已存在！".encode(), addr)
        return
    s.sendto(b"OK", addr)  # 如果用户不存在字典,向客户端发送OK消息

    # 通知其他人
    msg = "\n欢迎%s进入聊天室" % name
    for item in user:
        s.sendto(msg.encode(), user[item])  # 遍历字典,将消息发送给所有的客户端

    # 将用户加入
    user[name] = addr


# 聊天
def do_chat(s, name, str_news):
    """
        聊天处理
    :param s:数据报套接字
    :param name:发送消息人的姓名
    :param str_news:发送的消息
    :return:
    """
    msg = "\n%s:%s" % (name, str_news)
    for item in user:
        if item != name:
            s.sendto(msg.encode(), user[item])  # 遍历字典,将消息发送给所有客户端


# 退出聊天
def do_quit(s, name):
    """
        退出聊天处理
    :param s:数据报套接字
    :param name:退出聊天室的姓名
    :return:
    """
    msg = "\n%s退出了聊天室" % name
    for item in user:
        if item != name:
            s.sendto(msg.encode(), user[item])
        else:
            s.sendto(b"exit", user[item])  # 直接给退出的客户端发送exit消息
    # 将用户删除
    del user[name]


#  处理客户端请求
def do_request(s):
    """
        处理客户端请求
    :param s:数据报套接字
    :return:
    """
    while True:
        data, addr = s.recvfrom(1024)  # 接收消息
        msg = data.decode().split(" ")  # 将数据拆分,前面部分是请求类型,后面是内容
        # 区分请求类型
        if msg[0] == "L":  # 如果请求类型是L,则是判断用户是否存在,存在字典里直接进入聊天室,如果不在添加到字典,通知进入消息
            do_login(s, msg[1], addr)  # 请求类型
        elif msg[0] == "C":  # 如果请求类型是C,则是发送聊天内容
            str_news = " ".join(msg[2:])  # 拆分,取出除了请求类型的部分,其他内容全部都需要
            do_chat(s, msg[1], str_news)
        elif msg[0] == "Q":
            if msg[1] not in user:
                s.sendto(b"exit", addr)
                continue
            do_quit(s, msg[1])

# 创建网络连接
def main():
    # UDP套接字
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(ADDR)

    pid = os.fork()  # 创建新的进程

    if pid < 0:
        return
    elif pid == 0:
        while True:
            msg = input("管理员消息：")
            msg = "C 管理员消息 " + msg
            s.sendto(msg.encode(), ADDR)  # 管理员消息直接发送给父进程,父进程就是服务器接收
    else:
        # 请求处理
        do_request(s)  # 处理客户端请求


if __name__ == "__main__":
    main()

