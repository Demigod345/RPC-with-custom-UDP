import socket
import json
import threading

SIZE = 1024

class ReliableTCPServer:
    def __init__(self, host='localhost', port=9999):
        self._methods = {}
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
    
    # Register methods to be available for RPC
    def register_method(self, name, method):
        self._methods[name] = method

    def handle_client(self, client_socket):
        while True:
            try:
                # Receive message from client
                data = client_socket.recv(SIZE)
                if not data:
                    break  # Disconnect if no data received

                # Decode the received data
                function_name, args, kwargs = json.loads(data.decode())
                print(f'Function requested: {function_name} with args {args} and kwargs {kwargs}')
                
                # Execute the requested function
                if function_name in self._methods:
                    response = self._methods[function_name](*args, **kwargs)
                else:
                    response = f"Error: Function '{function_name}' not found."

            except Exception as e:
                response = f"Error while executing function: {e}"

            # Send the response back to the client
            response_packet = json.dumps(response).encode()
            client_socket.sendall(response_packet)

        client_socket.close()

    def start(self):
        print(f'TCP RPC Server listening on {self.host}:{self.port}')
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f'Connection established with {client_address}')
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

# Example functions to register
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# Create an instance of the RPC server
server = ReliableTCPServer()

# Register methods
server.register_method("add", add)
server.register_method("multiply", multiply)

# Start the server
server.start()
