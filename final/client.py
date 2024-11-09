import socket
import json
import time

MAX_RETRIES = 5
ACK_TIMEOUT = 1.0  # Timeout for acknowledgment in seconds
server_address = ('localhost', 8000)

class RPCClient:
    def __init__(self, server_address):
        self.server_address = server_address
        self.ready_to_send = True  # Flag to control sending requests

    def send_rpc_request(self, function_name, args=[], kwargs={}):
        # Wait until ready_to_send is True
        if not self.ready_to_send:
            print("Waiting for the previous request to complete...")
        
        while not self.ready_to_send:
            pass  # Empty loop, waits until ready_to_send turns True

        self.ready_to_send = False  # Block further requests until response is received
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(ACK_TIMEOUT)

        request_data = json.dumps([function_name, args, kwargs])
        start_time = time.time()  # Start timing

        for attempt in range(MAX_RETRIES):
            try:
                print(f"Sending request for {function_name}, attempt {attempt + 1}")
                client_socket.sendto(request_data.encode(), self.server_address)

                # Wait for server acknowledgment
                try:
                    ack, _ = client_socket.recvfrom(4096)
                    if ack.decode() == "ACK":
                        print("Acknowledgment received from server.")
                        break
                except socket.timeout:
                    print("Acknowledgment timeout, resending request...")
            except Exception as e:
                print(f"An error occurred: {e}")
                self.ready_to_send = True  # Reset flag in case of error
                return

        else:
            print("Failed to receive acknowledgment after multiple attempts.")
            self.ready_to_send = True  # Reset flag if acknowledgment fails
            return

        try:
            # Wait for the actual response from the server
            response, _ = client_socket.recvfrom(4096)
            end_time = time.time()  # End timing

            # Calculate response time in milliseconds
            response_time_ms = (end_time - start_time) * 1000
            response_data = json.loads(response.decode())
            print("Response from server:", response_data)
            # self.ready_to_send = True

            # Send acknowledgment back to server for the received response
            client_socket.sendto("ACK".encode(), self.server_address)
            print("Sent acknowledgment for response.")
            print(f"Response time: {response_time_ms:.3f} ms")

        except Exception as e:
            print(f"An error occurred while waiting for response: {e}")
        finally:
            client_socket.close()
            self.ready_to_send = True  # Allow the next request

# Initialize the RPCClient
client = RPCClient(server_address)

# Corrected function calls using the client instance
client.send_rpc_request("add", args=[5, 10])
client.send_rpc_request("multiply", args=[3, 4])
client.send_rpc_request("subtract", args=[10, 5])
