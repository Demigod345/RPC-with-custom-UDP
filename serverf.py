import socket
import json
import threading

# Packet size for UDP messages
SIZE = 1024
ACK_TIMEOUT = 1  # Timeout in seconds for ACK
MAX_RETRIES = 5  # Maximum number of retransmission attempts

class ReliableUDPServer:
    def __init__(self, host='localhost', port=9999):
        self._methods = {}
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.client_addresses = {}
    
    # Register methods to be available for RPC
    def register_method(self, name, method):
        self._methods[name] = method

    def start(self):
        print(f'UDP RPC Server listening on {self.host}:{self.port}')
        while True:
            # Receive message from client
            data, client_address = self.server_socket.recvfrom(SIZE)
            print(f'Received request from {client_address}')
            
            # Send ACK back to client and print a confirmation message
            self.server_socket.sendto(b'ACK', client_address)
            print(f'Sent ACK to {client_address} for received request')

            try:
                # Decode the received data
                function_name, args, kwargs, sequence_number = json.loads(data.decode())
                print(f'Function requested: {function_name} with args {args} and kwargs {kwargs}')
            except Exception as e:
                error_message = f"Error: Invalid request format. {e}"
                self.server_socket.sendto(error_message.encode(), client_address)
                continue

            # Execute the requested function
            try:
                if function_name in self._methods:
                    response = self._methods[function_name](*args, **kwargs)
                else:
                    response = f"Error: Function '{function_name}' not found."
            except Exception as e:
                response = f"Error while executing function: {e}"

            # Send the response back to the client along with the sequence number
            response_packet = json.dumps([response, sequence_number]).encode()
            self.server_socket.sendto(response_packet, client_address)

# Example functions to register
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# Create an instance of the RPC server
server = ReliableUDPServer()

# Register methods
server.register_method("add", add)
server.register_method("multiply", multiply)

# Start the server
server.start()
