import threading
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_email = "your_email@gmail.com"  # Replace with your Gmail email address
smtp_password = "your_app_password"  # Replace with your app-specific password

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
clients_info = {}
clients_lock = threading.Lock()

def send_email_notification(sender_name, sender_email, recipient_name, recipient_email, message):
    """
    Send an email notification to the recipient when they receive a message.
    """
    subject = f"New Message from {sender_name}"
    body = f"""
    Hello {recipient_name},

    You have received a new message from {sender_name} ({sender_email}):

    "{message}"

    Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    Regards,
    Chat Server
    """

    msg = MIMEMultipart()
    msg['From'] = smtp_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Send email using SMTP
        smtp_server_conn = smtplib.SMTP(smtp_server, smtp_port)
        smtp_server_conn.starttls()
        smtp_server_conn.login(smtp_email, smtp_password)
        smtp_server_conn.sendmail(smtp_email, recipient_email, msg.as_string())
        smtp_server_conn.quit()
        print(f"[EMAIL] Notification sent to {recipient_email}.")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

def broadcast(message, sender_conn=None):
    """
    Send a message to all connected clients except the sender (if applicable).
    """
    with clients_lock:
        for client_conn, client_id in clients.items():
            if client_conn != sender_conn:  # Don't send to the sender
                try:
                    client_conn.sendall(message)
                except Exception as e:
                    print(f"[ERROR] Failed to send message to {client_id}: {e}")
                    clients.pop(client_conn)

def handle_client(conn, addr):
    try:
        # Request and receive the client's name
        conn.send("Enter your name: ".encode(FORMAT))
        name = conn.recv(1024).decode(FORMAT).strip()

        # Request and receive the client's email
        conn.send("Enter your email: ".encode(FORMAT))
        email = conn.recv(1024).decode(FORMAT).strip()

        # Store client information
        with clients_lock:
            clients[conn] = f"{addr}"
            clients_info[conn] = {"name": name, "email": email}

        print(f"[NEW CONNECTION] {name} ({addr}) connected with email {email}")

        connected = True
        while connected:
            try:
                msg = conn.recv(1024).decode(FORMAT)
                if not msg:
                    break

                if msg == DISCONNECT_MESSAGE:
                    connected = False
                    continue

                print(f"[{addr}] Received: {msg}")

                # Broadcast the message to all clients
                broadcast_message(conn, msg)

            except ConnectionResetError:
                print(f"[ERROR] Connection with {addr} was reset.")
                break

    except Exception as e:
        print(f"[ERROR] Exception in handling client {addr}: {e}")
    finally:
        with clients_lock:
            clients.pop(conn, None)
            clients_info.pop(conn, None)
        conn.close()
        print(f"[DISCONNECT] {addr} Disconnected")

def broadcast_message(conn, message):
    sender_name = clients_info[conn]['name']
    formatted_message = f"[{sender_name}] {message}"
    print(f"[{sender_name}] Broadcasting to all clients: {message}")
    broadcast(formatted_message.encode(FORMAT), sender_conn=conn)

def server_console():
    """
    Allows server to send messages to all clients.
    Type your message in the server terminal to broadcast it to all clients.
    """
    while True:
        msg = input()
        if msg == 'q':
            break
        broadcast(f"[SERVER] {msg}".encode(FORMAT))

def start():
    print('[SERVER STARTED]! Listening for connections...')
    server.listen()

    # Start server console for broadcasting messages
    console_thread = threading.Thread(target=server_console, daemon=True)
    console_thread.start()

    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
        except Exception as e:
            print(f"[ERROR] Exception in accepting connections: {e}")

if __name__ == "__main__":
    try:
        start()
    except Exception as e:
        print(f"[ERROR] Server encountered an error: {e}")
    finally:
        server.close()