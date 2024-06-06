import socket
import random
import time
from datetime import datetime

def main():
    server_ip = "0.0.0.0"
    server_port = 12345
    buffer_size = 203  # 保证足够容纳报文

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))

    print(f"服务器已启动，在 {server_ip}:{server_port} 上监听")

    while True:
        try:
            # 接收连接请求
            data, client_address = server_socket.recvfrom(buffer_size)
            if data.decode() == "SYN":
                print(f"接收到来自 {client_address} 的连接请求")
                
                # 发送连接确认
                server_socket.sendto("ACK".encode(), client_address)

                # 接收连接确认
                data, _ = server_socket.recvfrom(buffer_size)
                if data.decode() == "ACK":
                    print(f"来自 {client_address} 的连接已建立")

                    # 连接建立后的数据传输
                    while True:
                        data, _ = server_socket.recvfrom(buffer_size)
                        
                        if data.decode() == "FIN":
                            server_socket.sendto("ACK".encode(), client_address)
                            time.sleep(0.1)  # 确保ACK发送完成
                            server_socket.sendto("FIN".encode(), client_address)
                            print(1)
                            data, _ = server_socket.recvfrom(buffer_size)
                            if data.decode() == "ACK":
                                print("关闭连接")
                            break

                        if random.random() < 0.2:  # 模拟丢包率为20%
                            print(f"模拟丢包，丢弃来自 {client_address} 的数据")
                            continue

                        seq_no = int.from_bytes(data[:2], byteorder='big')
                        ver = data[2]  # 获取版本号
                        received_time = time.time()
                        now_time = datetime.now().strftime("%H-%M-%S")

                        # 构建响应消息并发送
                        response_message = seq_no.to_bytes(2, byteorder='big') + bytes([ver]) + now_time.encode()+str(received_time).encode()
                        server_socket.sendto(response_message, client_address)
                        print(f"接收到来自 {client_address} 的数据: Request {seq_no}, Ver {ver}, Received at {now_time}")
                else:
                    print(f"来自 {client_address} 的无效连接确认")
            else:
                print(f"来自 {client_address} 的无效请求")
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    main()
