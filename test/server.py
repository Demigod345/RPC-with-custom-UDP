import socket
import json

SIZE = 512  # Optimal packet size for single-packet messages
ACK_BATCH = 5  # Send an ACK every 5 requests to reduce ACK overhead
BUFFER_SIZE = 4096  # Larger buffer size for handling multiple packets efficiently

class LowLatencyBatchUDPServer:
    def __init__(self, host='localhost', port=9999):
        self._methods = {}
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Set larger buffer sizes for high throughput
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
        self.server_socket.bind((self.host, self.port))
        self.request_count = 0

    # Register methods for RPC
    def register_method(self, name, method):
        self._methods[name] = method

    def start(self):
        print(f'Low-latency UDP RPC Server listening on {self.host}:{self.port}')
        while True:
            data, client_address = self.server_socket.recvfrom(SIZE)
            
            # Decode received data
            try:
                function_name, args, kwargs, sequence_number = json.loads(data.decode())
            except json.JSONDecodeError:
                continue  # Skip malformed packet

            # Execute requested function
            response = self._methods.get(function_name, lambda *args, **kwargs: "Function not found")(*args, **kwargs)

            # Send response with sequence number
            response_packet = json.dumps([response, sequence_number]).encode()
            self.server_socket.sendto(response_packet, client_address)

            # Only send an ACK every ACK_BATCH requests
            self.request_count += 1
            if self.request_count % ACK_BATCH == 0:
                self.server_socket.sendto(b'ACK', client_address)
                print(f'Sent ACK to {client_address} after {self.request_count} requests')

# Example functions
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# Initialize server
server = LowLatencyBatchUDPServer()
server.register_method("add", add)
server.register_method("multiply", multiply)
server.start()
