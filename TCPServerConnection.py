import socket
import threading

HOST = '192.168.1.10'  # Replace with your computer's IP address
PORT1 = 12345          # First port number
PORT2 = 54321          # Second port number

connections = []       # List to keep track of client connections
lock = threading.Lock() # A lock to synchronize access to the connections list

def broadcast_message(message):
    with lock:
        for conn in connections:
            try:
                conn.sendall(message.encode('utf-8'))
            except:
                # If sending fails, close the connection
                conn.close()
                connections.remove(conn)

def handle_client(conn, addr):
    with conn:
        with lock:
            connections.append(conn)
        print(f'Connected by {addr}')
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f'Received from {addr}: {data.decode("utf-8")}')
        except:
            pass
        finally:
            with lock:
                connections.remove(conn)
            print(f'Connection from {addr} closed')

def start_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of the address
        s.bind((HOST, port))
        s.listen()
        print(f"Server listening on {HOST}:{port}")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

def input_thread():
    while True:
        message = input("Enter message to send: ")
        broadcast_message(message)

# Start servers on both ports
server_thread1 = threading.Thread(target=start_server, args=(PORT1,))
server_thread2 = threading.Thread(target=start_server, args=(PORT2,))
input_thread = threading.Thread(target=input_thread)

server_thread1.start()
server_thread2.start()
input_thread.start()

server_thread1.join()
server_thread2.join()
input_thread.join()

