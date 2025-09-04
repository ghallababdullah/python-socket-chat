import socket
import threading

def start_client(host='127.0.0.1', port=8080):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((host, port))
        print(f"✅ Connected to private chat server at {host}:{port}")
        print("💡 Type '#help' to see available commands")
        print("🔒 Use '#private UserX message' for private chats")
        print("-" * 50)
        
        def receive_messages():
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        print("❌ Server disconnected")
                        break
                    message = data.decode('utf-8')
                    print(f"\r{message}")
                    print("💬 Your message: ", end="", flush=True)
                except:
                    print("\n❌ Connection lost")
                    break
        
        receive_thread = threading.Thread(target=receive_messages, daemon=True)
        receive_thread.start()
        
        while True:
            try:
                message = input("💬 Your message: ")
                
                if message.lower() == 'quit':
                    client_socket.sendall('quit'.encode('utf-8'))
                    break
                
                client_socket.sendall(message.encode('utf-8'))
                
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                client_socket.sendall('quit'.encode('utf-8'))
                break
                
    except ConnectionRefusedError:
        print("❌ Could not connect to server. Make sure it's running.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client_socket.close()
        print("🔌 Disconnected from server")

if __name__ == "__main__":
    start_client()