import socket
import threading
from datetime import datetime
import logging

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = set()
clients_lock = threading.Lock()
client_count = 0

def broadcast(message, _client=None):
    """ Broadcast message to all clients """
    with clients_lock:
        for client in clients:
            if client != _client:
                try:
                    client.sendall(message)
                except:
                    client.close()
                    clients.remove(client)

def handle_client(conn, addr):
    global client_count
    with clients_lock:
        client_count += 1
        client_id = f"client{client_count}"
        clients.add(conn)

    logging.info(f"[NEW CONNECTION] {addr} Connected as {client_id}")

    try:
        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"[{timestamp}] [{client_id}] {msg}".encode(FORMAT)
            logging.info(message.decode(FORMAT))
            broadcast(message, conn)

    except Exception as e:
        logging.error(f"[ERROR] {e}")

    finally:
        with clients_lock:
            clients.remove(conn)
        conn.close()

def server_broadcast():
    while True:
        msg = input("send meessage to all clients: ")
        if msg:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"[{timestamp}] [SERVER] {msg}".encode(FORMAT)
            logging.info(message.decode(FORMAT))
            broadcast(message)

def start():
    logging.info('[SERVER STARTED]!')
    server.listen()
    threading.Thread(target=server_broadcast).start()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()