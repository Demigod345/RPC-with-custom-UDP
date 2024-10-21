import socket
import json
import threading
import time

SIZE = 1024  # Base packet size
ACK_TIMEOUT = 1  # Timeout in seconds for ACK
MAX_RETRIES = 5  # Maximum number of retransmission attempts
INITIAL_WINDOW_SIZE = 1  # Start with a window size of 1
MAX_BUFFER_SIZE = 4096  # Maximum buffer size (adjust dynamically)

class ReliableUDPServer:
    def __init__(self, host='localhost', port=9999):
        self._methods = {}
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.client_buffers = {}  # Store client-specific buffers dynamically
        self.lock = threading.Lock()  # Lock for thread-safe buffer adjustment
    
    def register_method(self, name, method):
        self._methods[name] = method

    def adjust_buffer(self, client_address):
        with self.lock:
            if client_address not in self.client_buffers:
                # Initialize buffer with a base size
                self.client_buffers[client_address] = SIZE
            else:
                # Dynamically adjust based on the number of incoming requests
                if self.client_buffers[client_address] < MAX_BUFFER_SIZE:
                    self.client_buffers[client_address] += SIZE
                else:
                    self.client_buffers[client_address] = SIZE  # Reset if too large
    
    def start(self):
        print(f'UDP RPC Server listening on {self.host}:{self.port}')
        while True:
            # Dynamically adjust buffer size based on client load
            for client_address in self.client_buffers:
                self.adjust_buffer(client_address)
            
            # Receive message from client (non-blocking to simulate load)
            try:
                data, client_address = self.server_socket.recvfrom(SIZE)
                print(f'Received request from {client_address}')
                self.adjust_buffer(client_address)  # Adjust buffer dynamically

                # Send ACK back to client
                self.server_socket.sendto(b'ACK', client_address)
                
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
            
            except socket.error:
                continue

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
