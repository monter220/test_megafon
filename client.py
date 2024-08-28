import socket
import datetime
import random
import asyncio
import threading
import logging


COUNT_OF_CLIENTS: int = 5
COUNT_OF_ECHO: int = 5
IP_SERVER: str = '127.0.0.1'
PORT_SERVER: int = 53210
TEST_ECHO_MESSAGE: bytes = b'Hello, world'
MAX_SEC_BETWEEN_REQUEST: int = 10
MIN_SEC_BETWEEN_REQUEST: int = 1
LOG_NAME: str = 'log'


def handle_connection(connect, address) -> None:
    """Обработка сервером запросов от клиента"""
    logging.info(f'SERVER: Connected by {address}')
    with connect:
        while True:
            data: bytes = connect.recv(1024)
            if not data:
                break
            connect.sendall(data)
        connect.close()
        logging.info(f'SERVER: Closed by {address}')


def connect_server() -> None:
    """
    Ожидание подключения к серверу.
    Создание нового сопотока для обработки подключения к серверу.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv_sock:
        serv_sock.bind((IP_SERVER, PORT_SERVER))
        serv_sock.listen(1)
        client_connections: int = 0
        while client_connections < COUNT_OF_CLIENTS:
            logging.info('SERVER: Waiting for connection...')
            sock, addr = serv_sock.accept()
            soprocess = threading.Thread(
                target=handle_connection, args=(sock, addr))
            soprocess.start()
            client_connections += 1


async def new_server_process() -> None:
    """Запуск сервера в новом потоке"""
    soprocess = threading.Thread(target=connect_server)
    soprocess.start()


async def connect_client(client_number: int) -> None:
    """
    Подключение клиента к серверу
    с передачей сообщений и получением эхо ответа.
    """
    client_connect: socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    client_connect.connect((IP_SERVER, PORT_SERVER))
    message_number: int = 0
    while message_number < COUNT_OF_ECHO:
        client_connect.sendall(TEST_ECHO_MESSAGE)
        data: bytes = client_connect.recv(1024)
        logging.info(
            'CLIENT: Received client '
            f'{client_number} {message_number} {repr(data)}')
        message_number += 1
        await asyncio.sleep(random.randint(
            MIN_SEC_BETWEEN_REQUEST, MAX_SEC_BETWEEN_REQUEST))
    client_connect.close()


if __name__ == '__main__':
    start: datetime = datetime.datetime.now()
    logging.basicConfig(
        level=logging.INFO, filename=f'{LOG_NAME}.log', filemode='w',
        format='%(asctime)s %(levelname)s %(message)s'
    )
    ioloop = asyncio.get_event_loop()
    tasks = [
        ioloop.create_task(new_server_process()),
    ]
    for client in range(COUNT_OF_CLIENTS):
        tasks.append(ioloop.create_task(connect_client(client)))
    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()
    logging.info(f'WORK TIME: {datetime.datetime.now()-start} sec')
