import socket
import json

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

            try:
                # Decode the received data
                function_name, args, kwargs = json.loads(data.decode())
                print(f'Function requested: {function_name} with args {args} and kwargs {kwargs}')
            except Exception as e:
                # If decoding fails, send error back
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

            # Send the response back to the client
            self.server_socket.sendto(json.dumps(response).encode(), client_address)

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
