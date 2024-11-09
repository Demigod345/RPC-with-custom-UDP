import socket
import json
import time

MAX_RETRIES = 5
ACK_TIMEOUT = 1.0  # Timeout for acknowledgment in seconds

# Dictionary to store available methods
class RPCServer:
    def __init__(self, host='localhost', port=8000):
        self._methods = {}
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))

    # Register methods to be available for RPC
    def register_method(self, name, method):
        self._methods[name] = method

    def start(self):
        print(f'UDP RPC Server listening on {self.host}:{self.port}')
        while True:
            # Receiving data from the client
            data, client_address = self.server_socket.recvfrom(4096)
            print(f'Received request from {client_address}')

            # Send acknowledgment to client for the request
            self.server_socket.sendto("ACK".encode(), client_address)
            print("Sent acknowledgment to client for request.")

            # Decode the request
            try:
                function_name, args, kwargs = json.loads(data.decode())
                print(f'Function requested: {function_name} with args {args} and kwargs {kwargs}')
            except Exception as e:
                error_message = f"Error: Invalid request format. {e}"
                self.server_socket.sendto(error_message.encode(), client_address)
                continue

            # Execute the requested function and store the response
            try:
                if function_name in self._methods:
                    response = self._methods[function_name](*args, **kwargs)
                else:
                    response = f"Error: Function '{function_name}' not found."
            except Exception as e:
                response = f"Error while executing function: {e}"

            response_data = json.dumps(response).encode()
            attempts = 0

            # Send the response and wait for acknowledgment from client
            while attempts < MAX_RETRIES:
                self.server_socket.sendto(response_data, client_address)
                print(f"Sent response to client, attempt {attempts + 1}")

                # Wait for acknowledgment from client
                try:
                    self.server_socket.settimeout(ACK_TIMEOUT)
                    ack, _ = self.server_socket.recvfrom(4096)
                    if ack.decode() == "ACK":
                        print("Acknowledgment received from client for response.")
                        break
                except socket.timeout:
                    print("No acknowledgment from client, resending response...")
                    attempts += 1

            # Reset the timeout so it does not close the server
            self.server_socket.settimeout(None)

            if attempts == MAX_RETRIES:
                print("Failed to receive acknowledgment after multiple attempts.")

# Example functions to register
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def subtract(a, b):
    return a - b

# Create an instance of the RPC server
server = RPCServer()

# Register methods
server.register_method("add", add)
server.register_method("multiply", multiply)
server.register_method("subtract", subtract)

# Start the server
server.start()
