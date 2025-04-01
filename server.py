import socket
import ssl
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

HOST = 'localhost'  # Change this to your server IP when deploying
PORT = 6060

# Create SSL context
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile='server.crt', keyfile='server.key')


class ServerApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Secure Chat - Server")
        self.window.geometry("400x500")
        self.window.configure(bg="#34495E")

        self.clients = []
        self.server_socket = None

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

        # Start server
        self.start_server()

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(5)
            self.server_socket = context.wrap_socket(self.server_socket, server_side=True)

            threading.Thread(target=self.accept_clients, daemon=True).start()
            self.display_message("Server started...", "server")
        except Exception as e:
            messagebox.showerror("Server Error", str(e))

    def accept_clients(self):
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                self.clients.append(client_socket)
                threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()
                self.display_message(f"Client connected: {addr}", "server")
            except Exception as e:
                print(f"Error accepting clients: {e}")

    def handle_client(self, client_socket, addr):
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(f"Client: {message}", "left")
        except Exception:
            self.display_message(f"Client {addr} disconnected.", "server")
            self.clients.remove(client_socket)
            client_socket.close()

    def send_message(self):
        message = self.input_area.get()
        if message:
            self.display_message(f"You: {message}", "right")
            for client_socket in self.clients:
                try:
                    client_socket.send(message.encode('utf-8'))
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
    app = ServerApp()
    app.run()
