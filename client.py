import socket
import random
import asyncio
import threading


def handle_connection(sock, addr):
    print("Connected by", addr)
    with sock:
        while True:
            # Пока клиент не отключился, читаем передаваемые
            # им данные и отправляем их обратно
            data = sock.recv(1024)
            if not data:
                # Клиент отключился
                break
            sock.sendall(data)

        sock.close()
        print('close')


async def connect_client(k):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('127.0.0.1', 53210))
    await asyncio.sleep(0.1)
    i = 0
    while i<5:
        client_sock.sendall(b'Hello, world')
        data = client_sock.recv(1024)
        print(f'Received client {k} {i}', repr(data))
        i+=1
        await asyncio.sleep(random.randint(1,10))
    client_sock.close()


def connect_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv_sock:
        serv_sock.bind(('', 53210))
        serv_sock.listen(1)
        i = 0
        while i<5:
            print("Waiting for connection...")
            sock, addr = serv_sock.accept()
            t = threading.Thread(target=handle_connection, args=(sock, addr))
            t.start()
            i+=1


async def tread_s():
    t = threading.Thread(target=connect_server)
    t.start()


ioloop = asyncio.get_event_loop()
tasks = [
    ioloop.create_task(tread_s()),
    ioloop.create_task(connect_client(1)),
    ioloop.create_task(connect_client(2)),
    ioloop.create_task(connect_client(3)),
    ioloop.create_task(connect_client(4)),
    ioloop.create_task(connect_client(5)),
]
ioloop.run_until_complete(asyncio.wait(tasks))
ioloop.close()
