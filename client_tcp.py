import socket
import json
import time

SIZE = 1024

class ReliableTCPClient:
    def __init__(self, server_address):
        self.server_address = server_address
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)

    def send_request(self, function_name, args=[], kwargs={}):
        # Prepare the request packet
        request_packet = json.dumps([function_name, args, kwargs]).encode()

        # Measure time at the start of sending request
        start_time = time.time()

        # Send the request to the server
        self.client_socket.sendall(request_packet)
        print(f'Sent request {function_name}')

        # Wait for the server's response
        response_packet = self.client_socket.recv(SIZE)
        
        # Measure time after receiving response and calculate response time
        end_time = time.time()
        response_time = end_time - start_time

        # Decode and print the response
        response = json.loads(response_packet.decode())
        print(f'Received response: {response}')
        print(f'Response time: {response_time:.6f} seconds')

    def close(self):
        self.client_socket.close()

# Client-Side Usage
server_address = ('localhost', 9999)  # Update with server's IP address

client = ReliableTCPClient(server_address)
client.send_request("add", args=[5, 10])
client.send_request("multiply", args=[3, 4])
client.close()
