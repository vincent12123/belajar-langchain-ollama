import tkinter as tk
from tkinter import ttk, scrolledtext
import asyncio
import websockets
import threading
from datetime import datetime

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Chat Application")
        self.root.geometry("600x500")  # Set initial window size
        self.root.minsize(400, 300)    # Set minimum size for resizing
        self.root.configure(bg="#f0f0f0")  # Light gray background

        # Use ttk style for modern look
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use 'clam' theme for a professional feel
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", foreground="#333333", font=("Arial", 10))
        self.style.configure("TButton", padding=6, font=("Arial", 10))
        self.style.configure("TEntry", padding=5)

        # Main frame
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header label
        self.header_label = ttk.Label(self.main_frame, text="Chat Room", font=("Arial", 14, "bold"))
        self.header_label.pack(pady=(0, 10))

        # Chat area frame
        self.chat_frame = ttk.Frame(self.main_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Scrollbar for chat area
        self.chat_scrollbar = ttk.Scrollbar(self.chat_frame)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Chat text area
        self.chat_area = tk.Text(self.chat_frame, wrap=tk.WORD, state='disabled', yscrollcommand=self.chat_scrollbar.set,
                                 bg="#ffffff", fg="#000000", font=("Arial", 10), borderwidth=1, relief="flat")
        self.chat_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_scrollbar.config(command=self.chat_area.yview)

        # Input frame
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X)

        # Message entry
        self.message_entry = ttk.Entry(self.input_frame, font=("Arial", 10))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)

        # Send button
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        # Status label at the bottom
        self.status_label = ttk.Label(root, text="Disconnected", relief=tk.SUNKEN, anchor=tk.W, padding=5, background="#e0e0e0")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.client_id = "User1"  # Replace with your username
        self.websocket = None
        self.loop = asyncio.new_event_loop()

        # Run connection in a separate thread
        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def display_message(self, message, is_sent=False):
        self.chat_area.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {'You: ' if is_sent else ''}{message}\n"
        self.chat_area.insert(tk.END, formatted_message)
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message and self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.send(message), self.loop)
            self.display_message(message, is_sent=True)
            self.message_entry.delete(0, tk.END)

    def connect_to_server(self):
        try:
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.websocket_connection())
        except Exception as e:
            print(f"Connection error: {e}")
            self.root.after(0, self.update_status, f"Connection error: {e}")

    async def websocket_connection(self):
        uri = f"ws://localhost:8000/ws/{self.client_id}"
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                self.root.after(0, self.update_status, "Connected to chat server")
                self.display_message("Connected to chat server")
                while True:
                    try:
                        message = await websocket.recv()
                        self.root.after(0, self.display_message, message)
                    except websockets.exceptions.ConnectionClosed:
                        self.root.after(0, self.update_status, "Connection closed by server")
                        self.display_message("Connection closed by server")
                        break
                    except Exception as e:
                        print(f"Receive error: {e}")
                        break
        except Exception as e:
            self.root.after(0, self.update_status, f"Could not connect to server: {e}")
            self.root.after(0, self.display_message, f"Could not connect to server: {e}")
            print(f"WebSocket connection failed: {e}")

    def update_status(self, status):
        self.status_label.config(text=status)

if __name__ == "__main__":
    print("Starting Chat App...")
    root = tk.Tk()
    app = ChatApp(root)
    print("Entering mainloop...")
    root.mainloop()