import socket
import ssl
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

SERVER_HOST = 'localhost'  # Change to server IP for cloud deployment
SERVER_PORT = 6060

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


class ClientApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Secure Chat - Client")
        self.window.geometry("400x500")
        self.window.configure(bg="#2C3E50")

        self.client_socket = None

        # Chat area
        self.chat_area = scrolledtext.ScrolledText(self.window, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 10))
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.config(state='disabled')

        # Message input
        self.input_area = tk.Entry(self.window, font=("Arial", 12), bg="#BDC3C7", fg="#2C3E50")
        self.input_area.pack(padx=10, pady=5, fill=tk.X)
        self.input_area.bind('<Return>', lambda event: self.send_message())

        # Send button
        self.send_button = tk.Button(self.window, text="Send", command=self.send_message, bg="#3498DB", fg="white", font=("Arial", 10, "bold"))
        self.send_button.pack(pady=5)

        # Define alignment tags
        self.chat_area.tag_configure("left", justify="left", foreground="#2C3E50")
        self.chat_area.tag_configure("right", justify="right", foreground="#27AE60")

        # Connect to server
        self.connect_to_server()

    def connect_to_server(self):
        try:
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket = context.wrap_socket(raw_socket)
            self.client_socket.connect((SERVER_HOST, SERVER_PORT))

            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.display_message("Connected to server...", "server")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message, "left")
            except Exception:
                self.display_message("Disconnected from server.", "server")
                self.client_socket.close()
                break

    def send_message(self):
        message = self.input_area.get()
        if message:
            self.display_message(f"You: {message}", "right")
            try:
                self.client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")
            self.input_area.delete(0, tk.END)

    def display_message(self, message, sender):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n", sender)
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def run(self):
        self.window.mainloop()


if __name__ == '__main__':
    app = ClientApp()
    app.run()
