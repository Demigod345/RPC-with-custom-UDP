import socket
import json
import time

MAX_RETRIES = 5
server_address = ('localhost', 8000)

class RPCClient:
    def __init__(self, server_address):
        self.server_address = server_address

    def send_rpc_request(self, function_name, args=[], kwargs={}):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(self.server_address)  # Establish TCP connection

        request_data = json.dumps([function_name, args, kwargs])
        start_time = time.time()  # Start timing

        try:
            # Send request to the server
            print(f"Sending request for {function_name}")
            client_socket.sendall(request_data.encode())

            # Receive response from the server
            response = client_socket.recv(4096)
            end_time = time.time()  # End timing

            # Calculate response time in milliseconds
            response_time_ms = (end_time - start_time) * 1000
            response_data = json.loads(response.decode())
            print("Response from server:", response_data)
            print(f"Response time: {response_time_ms:.3f} ms")

            return response_time_ms  # Return the response time for further processing

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        finally:
            client_socket.close()  # Close the connection after the request

# Initialize the RPCClient
client = RPCClient(server_address)

# Measure total time for 1000 requests
total_time = 0
num_requests = 10000

for i in range(num_requests):
    print(f"Sending request {i + 1}/{num_requests}")
    response_time = client.send_rpc_request("add", args=[5, 10])  # Example request
    if response_time:
        total_time += response_time

# Calculate average response time
average_time = total_time / num_requests
print(f"\nTotal time for {num_requests} requests: {total_time:.3f} ms")
print(f"Average response time: {average_time:.3f} ms")
