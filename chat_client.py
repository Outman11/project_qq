from socket import *
import os, sys

# 服务器地址
ADDR = ("172.40.71.158", 9535)


# 发送消息
def send_msg(s, name):
    """
        发送消息及退出聊天室
    :param s: 数据报套接字
    :param name:姓名
    :return:
    """
    while True:
        try:
            news = input("发言：")
        except KeyboardInterrupt:
            news = "quit"
        #  退出聊天室
        if news == "quit":
            msg = "Q " + name
            s.sendto(msg.encode(), ADDR)
            sys.exit("退出聊天室！")
        msg = "C %s %s" % (name, news)
        s.sendto(msg.encode(), ADDR)

# 接收消息
def recv_msg(s):
    while True:
        data,addr = s.recvfrom(2048)
        #  服务端发送exit表示让客户端退出
        if data.decode() == "exit":
            sys.exit()
        print(data.decode() + "\n发言：", end="" )

# 创建网络连接
def main():
    # UDP套接字
    s = socket(AF_INET, SOCK_DGRAM)
    while True:
        name = input("输入你的姓名：")
        msg = "L " + name  # 协议请求类别
        s.sendto(msg.encode(), ADDR)
        # 等待回应
        data, addr = s.recvfrom(1024)
        if data.decode() == "OK":  # 如果接收到的信息为"OK"
            print("您已经进入聊天室")
            break
        else:
            print(data.decode())

    # 创建新的进程
    pid = os.fork()
    if pid < 0:
        sys.exit("Error")
    elif pid == 0:
        send_msg(s, name)  # 子进程负责发送内容
    else:
        recv_msg(s)  # 父进程负责接收内容


if __name__ == "__main__":
    main()
