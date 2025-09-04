import socket
import threading
from datetime import datetime

class PrivateChatServer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.clients = {}  # {client_socket: {'address': address, 'color': color, 'name': f"User{id}"}}
        self.private_chats = {}  # Track private conversations
        self.colors = ['\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m']
        self.color_index = 0
        self.server_socket = None
        self.user_counter = 1
        
    def assign_user_name(self):
        name = f"User{self.user_counter}"
        self.user_counter += 1
        return name
    
    def send_to_client(self, client_socket, message, color_code=None):
        """Send message to a specific client"""
        try:
            if color_code:
                colored_msg = f"{color_code}{message}\033[0m"
                client_socket.sendall(colored_msg.encode('utf-8'))
            else:
                client_socket.sendall(message.encode('utf-8'))
        except:
            self.remove_client(client_socket)
    
    def broadcast(self, message, sender_socket=None, color_code=None):
        """Send message to all clients except sender"""
        for client_socket, client_info in self.clients.items():
            if client_socket != sender_socket:
                self.send_to_client(client_socket, message, color_code)
    
    def send_private_message(self, sender_socket, target_name, message):
        """Send private message to specific user"""
        sender_name = self.clients[sender_socket]['name']
        
        # Find target client
        target_socket = None
        for sock, info in self.clients.items():
            if info['name'] == target_name:
                target_socket = sock
                break
        
        if target_socket:
            timestamp = datetime.now().strftime("%H:%M:%S")
            private_msg = f"[{timestamp}] PRIVATE from {sender_name}: {message}"
            
            # Send to target
            self.send_to_client(target_socket, private_msg, '\033[95m')  # Purple for private
            
            # Send confirmation to sender
            confirm_msg = f"[{timestamp}] PRIVATE to {target_name}: {message}"
            self.send_to_client(sender_socket, confirm_msg, '\033[95m')
            
            # Store in private chat history
            chat_key = tuple(sorted([sender_name, target_name]))
            if chat_key not in self.private_chats:
                self.private_chats[chat_key] = []
            self.private_chats[chat_key].append(f"{sender_name}: {message}")
            
        else:
            error_msg = f"User '{target_name}' not found or offline"
            self.send_to_client(sender_socket, error_msg, '\033[91m')
    
    def remove_client(self, client_socket):
        if client_socket in self.clients:
            user_info = self.clients[client_socket]
            print(f"Client {user_info['name']} ({user_info['address']}) disconnected")
            
            # Notify other users
            leave_msg = f"⚡ {user_info['name']} left the chat"
            self.broadcast(leave_msg, client_socket, '\033[93m')
            
            del self.clients[client_socket]
            client_socket.close()
    
    def handle_client(self, client_socket, address):
        """Handle messages from a client"""
        # Assign color and name
        color_code = self.colors[self.color_index % len(self.colors)]
        self.color_index += 1
        user_name = self.assign_user_name()
        
        # Store client information
        self.clients[client_socket] = {
            'address': address, 
            'color': color_code, 
            'name': user_name
        }
        
        print(f"New connection: {user_name} from {address}. Total: {len(self.clients)}")
        
        # Send welcome message with user name
        welcome_msg = f"Welcome {user_name}! Your color: {color_code}This text is colored\033[0m"
        self.send_to_client(client_socket, welcome_msg)
        
        # Notify all users about new connection
        join_msg = f"🎉 {user_name} joined the chat!"
        self.broadcast(join_msg, client_socket, '\033[92m')
        
        # Send help message
        help_msg = "\nAvailable commands:\n"
        help_msg += "#users - Show online users\n"
        help_msg += "#private <username> <message> - Send private message\n"
        help_msg += "#help - Show this help\n"
        help_msg += "quit - Exit chat\n"
        self.send_to_client(client_socket, help_msg, '\033[94m')
        
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8').strip()
                user_name = self.clients[client_socket]['name']
                
                if message == '#users':
                    # Send list of connected users
                    users_list = f"👥 Online users ({len(self.clients)}):\n"
                    for sock, info in self.clients.items():
                        status = " (you)" if sock == client_socket else ""
                        users_list += f"  {info['name']}{status}\n"
                    self.send_to_client(client_socket, users_list)
                
                elif message.startswith('#private '):
                    # Private message format: #private username message
                    parts = message.split(' ', 2)
                    if len(parts) >= 3:
                        target_name = parts[1]
                        private_message = parts[2]
                        self.send_private_message(client_socket, target_name, private_message)
                    else:
                        error_msg = "Usage: #private <username> <message>"
                        self.send_to_client(client_socket, error_msg, '\033[91m')
                
                elif message == '#help':
                    self.send_to_client(client_socket, help_msg, '\033[94m')
                
                elif message.lower() == 'quit':
                    break
                
                else:
                    # Public message - broadcast to everyone
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    public_msg = f"[{timestamp}] {user_name}: {message}"
                    self.broadcast(public_msg, client_socket, self.clients[client_socket]['color'])
                    
        except Exception as e:
            print(f"Error with client {user_name}: {e}")
        finally:
            self.remove_client(client_socket)
    
    def start_server(self):
        """Start the private chat server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Private chat server started on {self.host}:{self.port}")  # FIXED: Changed port to self.port
            print("Waiting for connections...")
            
            while True:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.server_socket.close()
            print("Server closed")

if __name__ == "__main__":
    server = PrivateChatServer()
    server.start_server()