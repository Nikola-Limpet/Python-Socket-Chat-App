import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
CLIENT_ID = "client2"  # You can customize this per client

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Chat Client - {CLIENT_ID}")

        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.chat_area.pack(padx=20, pady=5)
        self.chat_area.config(state=tk.DISABLED)

        self.msg_entry = tk.Entry(root, width=50)
        self.msg_entry.pack(padx=20, pady=5)
        self.msg_entry.bind("<Return>", self.send_message)

        self.connect_button = tk.Button(root, text="Connect", command=self.connect)
        self.connect_button.pack(padx=20, pady=5)

        self.client = None

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(ADDR)
            self.connect_button.config(state=tk.DISABLED)
            threading.Thread(target=self.receive_messages).start()
        except Exception as e:
            print(f"[ERROR] Could not connect to server: {e}")

    def send_message(self, event=None):
        msg = self.msg_entry.get()
        if msg:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            formatted_message = f"[{CLIENT_ID}] [{timestamp}] {msg}"
            self.client.send(formatted_message.encode(FORMAT))
            self.msg_entry.delete(0, tk.END)
            
            # Send email notification
            subject = f"New message from {CLIENT_ID}"
            body = f"Message: {msg}\nTimestamp: {timestamp}\nFrom {CLIENT_ID}"
            to_email = "recipient_email@gmail.com"  # Replace with the recipient's email
            send_email(subject, body, to_email)
            
            if msg == 'q':
                self.client.send(DISCONNECT_MESSAGE.encode(FORMAT))
                self.client.close()
                self.root.quit()

    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode(FORMAT)
                if msg:
                    self.chat_area.config(state=tk.NORMAL)
                    self.chat_area.insert(tk.END, msg + '\n')
                    self.chat_area.config(state=tk.DISABLED)
                    self.chat_area.yview(tk.END)
            except Exception as e:
                print("[ERROR] Connection lost")
                self.client.close()
                break

def send_email(subject, body, to_email):
    from_email = "your_email@gmail.com"  # Replace with your Gmail email address
    password = "your_app_password"  # Replace with your app-specific password

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.starttls()
        smtp_server.login(from_email, password)
        smtp_server.sendmail(from_email, to_email, msg.as_string())
        smtp_server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    client_gui = ClientGUI(root)
    root.mainloop()