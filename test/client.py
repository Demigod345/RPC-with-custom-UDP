import socket
import json
import time
import threading

SIZE = 512  # Packet size
TIMEOUT = 0.05  # Small timeout to reduce waiting time
BUFFER_SIZE = 4096  # Larger buffer size to receive multiple packets

class LowLatencyBatchUDPClient:
    def __init__(self, server_address):
        self.server_address = server_address
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Set larger buffer sizes for high throughput
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
        self.client_socket.settimeout(TIMEOUT)
        self.sequence_number = 0

    def send_request(self, function_name, args=[], kwargs={}):
        sequence = self.sequence_number
        request_packet = json.dumps([function_name, args, kwargs, sequence]).encode()
        start_time = time.time()

        def receive_response():
            try:
                response_packet, _ = self.client_socket.recvfrom(SIZE)
                response, seq = json.loads(response_packet.decode())
                
                # Measure time for response
                end_time = time.time()
                if seq == sequence:
                    print(f"Response for {function_name}: {response}")
                    print(f"Response time: {end_time - start_time:.6f} seconds")
            except (socket.timeout, json.JSONDecodeError):
                print("Request timed out or malformed response received")

        # Send the request
        self.client_socket.sendto(request_packet, self.server_address)
        print(f"Sent request {function_name} with sequence {sequence}")

        # Start a new thread to handle the response
        threading.Thread(target=receive_response).start()
        self.sequence_number += 1

    def send_batch_requests(self, requests):
        threads = []
        for request in requests:
            function_name, args, kwargs = request
            thread = threading.Thread(target=self.send_request, args=(function_name, args, kwargs))
            thread.start()
            threads.append(thread)

        # Join all threads to complete batch requests
        for thread in threads:
            thread.join()

    def close(self):
        self.client_socket.close()

# Example client usage
server_address = ('localhost', 9999)
client = LowLatencyBatchUDPClient(server_address)

# Prepare batch of requests to send
requests = [
    ("add", [5, 10], {}),
    ("multiply", [3, 4], {}),
    ("add", [15, 25], {}),
    ("multiply", [6, 7], {})
]

# Send batch requests
client.send_batch_requests(requests)
client.close()
