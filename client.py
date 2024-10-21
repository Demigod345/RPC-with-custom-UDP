import socket
import json

def send_rpc_request(server_address, function_name, args=[], kwargs={}):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Prepare the request data
    request_data = json.dumps([function_name, args, kwargs])
    
    try:
        print("Send Request for ", function_name)
        # Send request to server
        client_socket.sendto(request_data.encode(), server_address)

        # Receive response from server
        response, _ = client_socket.recvfrom(4096)
        print("Response from server:", json.loads(response.decode()))

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

# Send requests to the RPC server
server_address = ('localhost', 8000)

send_rpc_request(server_address, "add", args=[5, 10])
send_rpc_request(server_address, "multiply", args=[3, 4])
send_rpc_request(server_address, "subtract", args=[10, 5])  # This will result in an error
