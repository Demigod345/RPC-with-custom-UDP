import socket
import json
import time

# Packet size for UDP messages
SIZE = 1024
ACK_TIMEOUT = 1  # Timeout in seconds for ACK
MAX_RETRIES = 5  # Maximum number of retransmission attempts

class ReliableUDPClient:
    def __init__(self, server_address):
        self.server_address = server_address
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = 0

    def send_request(self, function_name, args=[], kwargs={}):
        # Prepare the request packet with a sequence number
        request_packet = json.dumps([function_name, args, kwargs, self.sequence_number]).encode()

        for attempt in range(MAX_RETRIES):
            # Send the request to the server
            self.client_socket.sendto(request_packet, self.server_address)
            print(f'Sent request {function_name} with sequence {self.sequence_number}')

            # Wait for ACK
            self.client_socket.settimeout(ACK_TIMEOUT)
            try:
                # Try receiving an ACK
                ack, _ = self.client_socket.recvfrom(SIZE)
                if ack == b'ACK':
                    print(f'Received ACK for sequence {self.sequence_number}')
                    break  # Exit the retry loop if ACK received
            except socket.timeout:
                print(f'No ACK, retrying... {attempt + 1}/{MAX_RETRIES}')

        if attempt == MAX_RETRIES - 1:
            print('Max retries reached. Request failed.')
            return

        # Wait for the server's response
        self.client_socket.settimeout(None)  # Disable timeout for actual response
        response_packet, _ = self.client_socket.recvfrom(SIZE)
        response, seq = json.loads(response_packet.decode())

        # Ensure the response matches the request sequence
        if seq == self.sequence_number:
            print(f'Received response: {response}')
        else:
            print('Mismatched response sequence number.')

        self.sequence_number += 1  # Increment sequence number for the next request

# Client-Side Usage
server_address = ('192.168.1.100', 9999)  # Update with server's IP address

client = ReliableUDPClient(server_address)
client.send_request("add", args=[5, 10])
client.send_request("multiply", args=[3, 4])
