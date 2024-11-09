import socket
import json

server_address = ('localhost', 8000)

class RPCServer:
    def __init__(self, host='localhost', port=8000):
        self._methods = {}
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)  # Listen for incoming connections

    # Register methods to be available for RPC
    def register_method(self, name, method):
        self._methods[name] = method

    def start(self):
        print(f'TCP RPC Server listening on {self.host}:{self.port}')
        while True:
            # Accept a new connection
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address}")

            try:
                # Receive request data from the client
                data = client_socket.recv(4096)
                if not data:
                    break  # No data received, close the connection
                
                # Decode the request
                try:
                    function_name, args, kwargs = json.loads(data.decode())
                    print(f'Function requested: {function_name} with args {args} and kwargs {kwargs}')
                except Exception as e:
                    error_message = f"Error: Invalid request format. {e}"
                    client_socket.sendall(error_message.encode())
                    continue

                # Execute the requested function and store the response
                try:
                    if function_name in self._methods:
                        response = self._methods[function_name](*args, **kwargs)
                    else:
                        response = f"Error: Function '{function_name}' not found."
                except Exception as e:
                    response = f"Error while executing function: {e}"

                # Send the response to the client
                response_data = json.dumps(response).encode()
                client_socket.sendall(response_data)

            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                client_socket.close()  # Close the connection

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
