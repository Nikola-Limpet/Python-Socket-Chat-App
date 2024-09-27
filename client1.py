import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
CLIENT_ID = "client1"

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
        """ 
        Connect to server
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)
        self.connect_button.config(state=tk.DISABLED)
        threading.Thread(target=self.receive_messages).start()

    def send_message(self, event=None):
        """
        Send message to server
        """
        msg = self.msg_entry.get()
        if msg:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.client.send(f"[{CLIENT_ID}] [{timestamp}] {msg}".encode(FORMAT))
            self.msg_entry.delete(0, tk.END)
            if msg == 'q':
                self.client.send(DISCONNECT_MESSAGE.encode(FORMAT))
                self.client.close()
                self.root.quit()

    def receive_messages(self):
        """ 
        Receive messages from server
        """
        while True:
            try:
                msg = self.client.recv(1024).decode(FORMAT)
                if msg:
                    self.chat_area.config(state=tk.NORMAL)
                    self.chat_area.insert(tk.END, msg + '\n')
                    self.chat_area.config(state=tk.DISABLED)
                    self.chat_area.yview(tk.END)
            except:
                print("[ERROR] Connection lost")
                self.client.close()
                break

if __name__ == "__main__":
    root = tk.Tk()
    client_gui = ClientGUI(root)
    root.mainloop()