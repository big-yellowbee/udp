import socket
import time
from datetime import datetime
import argparse
import numpy as np
def main():
    parser = argparse.ArgumentParser(description="UDP 客户端")
    parser.add_argument("server_ip", help="服务器的IP地址")
    parser.add_argument("server_port", type=int, help="服务器的端口号")
    args = parser.parse_args()
    rtts = []
    times = [1, 2]
    rcount = 0
    flag=1
    scount = 0
    server_ip = args.server_ip
    server_port = args.server_port
    buffer_size = 203
    timeout = 0.1  # 超时时间设置为100ms
    max_retries = 2  # 最大重试次数
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)

    # 发送连接请求
    client_socket.sendto("SYN".encode(), (server_ip, server_port))

    # 等待服务器的连接确认
    try:
        data, _ = client_socket.recvfrom(buffer_size)
        if data.decode() == "ACK":
            print("收到服务器的连接确认")
            
            # 发送连接确认
            client_socket.sendto("ACK".encode(), (server_ip, server_port))
            print("连接已建立，可以进行数据传输")
            for i in range(1, 13):
                seq_no = i.to_bytes(2, byteorder='big')  # 将序列号转换为2字节大端序
                ver = b'\x02'  # 版本号为2，使用字节表示
                data = b'D' * 200  # 数据部分，填充200字节的'D'
                message = seq_no + ver + data
                retries = 0
                while retries <= max_retries:
                    try:
                        scount += 1
                        print(f"发送: {message} 到 {server_ip}:{server_port}")
                        client_socket.sendto(message, (server_ip, server_port))
                        start_time = time.time()
                        response, _ = client_socket.recvfrom(buffer_size)
                        rcount += 1
                        rtt = (time.time() - start_time) * 1000  # 转换为毫秒
                        seq_no_response = int.from_bytes(response[:2], byteorder='big')
                        received_time = response[3:12].decode()
                        s_time=response[12:].decode()
                        flag-=1
                        if flag == 0:
                            times[0] = s_time
                        rtts.append(rtt)
                        print(f"收到响应: Seq_no={seq_no_response}, server_IP={server_ip}:PORT{server_port}, Received Time={received_time}")
                        print(f"往返时间 (RTT): {rtt:.2f} ms")
                        times[1] = s_time
                        break
                    except socket.timeout:
                        retries += 1
                        if retries <= max_retries:
                            print(f"Seq_no={i} request time out")
                            print(f"超时，重试 {retries}/{max_retries} 次")
                        else:
                            print("重传失败")
        else:
            print("连接失败")
    except socket.timeout:
        print("连接超时")
    print("接收到的udp packet数量:", rcount)
    print("丢包率是：" + "{:.2f}%".format((1 - rcount / scount) * 100))
    print("RTT的最大值是:", round(np.max(rtts), 2))
    print("RTT的最小值是:", round(np.min(rtts), 2))
    print("RTT的平均值是:", round(np.mean(rtts), 2))
    print("RTT的标准差是:", round(np.std(rtts), 2))
    time1 = float(times[0])
    time2 = float(times[1])
    time_difference = time2 - time1
    time_difference_seconds = time_difference * 1000
    print("server的整体响应时间是:", round(time_difference_seconds, 2), "毫秒")
    client_socket.sendto("FIN".encode(), (server_ip, server_port))
    data, _ = client_socket.recvfrom(buffer_size)
    if data.decode() == "ACK":
        data, _ = client_socket.recvfrom(buffer_size)
        if data.decode() == "FIN":
            client_socket.sendto("ACK".encode(), (server_ip, server_port))
            print("连接已成功关闭")
            client_socket.close()
        else:
            print("服务器未发送FIN")
    else:
        print("服务器未发送ACK")

if __name__ == "__main__":
    main()
