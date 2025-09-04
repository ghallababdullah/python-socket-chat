# Python Socket Chat Application 🐍💬

A multi-client chat system built with Python sockets featuring private messaging, colored messages, and real-time communication.

## Features ✨

- **Multi-client support** - Multiple users can chat simultaneously
- **Private messaging** - Send secret messages with `#private username message`
- **Colored messages** - Each user has a unique color for easy identification
- **Real-time communication** - Instant message delivery
- **User management** - See online users with `#users` command
- **Server monitoring** - Server displays all activity and messages


## Installation & Setup 🚀

### Prerequisites
- Python 3.6+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/python-socket-chat.git
cd python-socket-chat

python server.py
# Terminal 2
python client.py

# Terminal 3  
python client.py

# Terminal 4
python client.py

Server Commands
The server runs on 127.0.0.1:8080 by default

Server displays all messages and connections in real-time

Client Commands
#users - Show all online users

#private <username> <message> - Send private message


python-socket-chat/
├── server.py          # Main server application
├── client.py          # Client application
├── README.md          # This file
└── requirements.txt   # Python dependencies (none required!)

#help - Show available commands

quit - Exit the chat

Example
text
💬 Your message: #private User2 Hello secret!
💬 Your message: Hello everyone! 👋
