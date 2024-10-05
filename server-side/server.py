import os  # Import the os module for interacting with the operating system
import csv  # Import the csv module for reading and writing CSV files
import socket  # Import the socket module for network communication
import datetime  # Import the datetime module for manipulating dates and times
from hashlib import sha256  # Import the sha256 function from the hashlib module for hashing
from cryptography.fernet import Fernet  # Import the Fernet class from the cryptography.fernet module for encryption

# Get the IP address of the local machine
IP = socket.gethostbyname(socket.gethostname())

# Define the port number for the server
PORT = 4455

# Define the server address using IP and PORT
ADDR = (IP, PORT)

# The buffer size for sending and receiving data over the network is 102400 bytes (100 KB)
SIZE = 102400 

# Define the encryption key for Fernet encryption
KEY = 'epVKiOHn7J0sZcJ4-buWQ5ednv3csHdQHfvEKk0qVvk='

# Define your credentials
credentials = {
    "UserOne": "password1",
    "UserTwo": "password2"
}

  
# Function to encrypt data using Fernet symmetric encryption
def Encrypt_Data(data):
    # Create a Fernet object using the predefined encryption key
    fernet = Fernet(KEY)
    # Encrypt the data (after encoding it to bytes) and store it in cipherText
    cipherText = fernet.encrypt(data.encode())
    # Return the encrypted data
    return cipherText

# Function to decrypt data using Fernet symmetric encryption
def Decrypt_Data(data):
    # Create a Fernet object using the predefined encryption key
    fernet = Fernet(KEY)
    # Decrypt the data (after encoding it to bytes) and store it in plainText
    plainText = fernet.decrypt(data.encode())
    # Return the decrypted data
    return plainText
    
# Function to break a file into chunks for building the merkle tree
def Chunk_File(file_path, chunk_size):
    # Initialize an empty list to store the chunks of the file
    chunks = []
    
    # Open the file in read mode
    with open(file_path, "r") as file:
        # Continuously read the file in chunks of the specified size
        while True:
            chunk = file.read(chunk_size)
            # If a chunk is read, append it to the chunks list
            if chunk:
                chunks.append(chunk)
            # If no more data is read, break out of the loop
            else:
                break
    
    # Return the list of file chunks
    return chunks
    
# Function to create a Merkle tree from file chunks and 
# returns the root hash value of the tree
def Merkle_Tree(chunks):
    # Base case: if there is only one chunk, return its SHA-256 hash
    if len(chunks) == 1:
        return sha256(chunks[0].encode()).hexdigest()

    # Find the midpoint of the chunks list
    mid = len(chunks) // 2
    
    # Recursively create the Merkle tree for the left half of the chunks
    left_hash = Merkle_Tree(chunks[:mid])
    
    # Recursively create the Merkle tree for the right half of the chunks
    right_hash = Merkle_Tree(chunks[mid:])
    
    print(f"Left Chunk:{chunks[:mid]}, Left Hash: {left_hash}\nRight Chunk:{chunks[mid:]}, Right Hash: {right_hash}\n")

    # Combine the left and right hashes, hash them, and return the result
    return sha256(left_hash.encode() + right_hash.encode()).hexdigest()
    
# Function to log data to a CSV file
def Log_To_CSV(log_data):
    # Open the "logs.csv" file in append mode ('a') and ensure no extra newline characters are added
    with open("logs.csv", mode='a', newline='') as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        # Write the log data as a new row in the CSV file
        writer.writerow(log_data)
        
def Upload_File(conn, addr):
    # Receive the filename from the client
    file_name = conn.recv(SIZE).decode()
    print(f"Filename: {file_name} received")
    conn.send("filename received".encode())  # Acknowledgment to the client

    # Receive the file data, decrypt it, and store it in the "Received data" folder
    with open("Received Data/" + file_name, 'wb') as file:
        data = conn.recv(SIZE).decode()
        file.write(Decrypt_Data(data))

    # Receive the root hash value of the Merkle tree created by the client
    client_hash_val = conn.recv(SIZE).decode()
    print(f"Hash value {client_hash_val}")

    # Create chunks from the received file and calculate the Merkle tree root hash
    file_chunk = Chunk_File("Received data/" + file_name, 1024)
    server_hash_val = Merkle_Tree(file_chunk)
    print(f"Hash value: {server_hash_val}")

    # Compare the calculated hash with the received hash value
    if server_hash_val == client_hash_val:
        conn.send("True".encode())  # Inform the client that the upload was successful
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Upload", file_name, "Successful"]
        Log_To_CSV(log_data)  # Log the successful upload
        print('Your data is in good hands')
    else:
        conn.send("False".encode())  # Inform the client that the upload failed
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Upload", file_name, "Unsuccessful"]
        Log_To_CSV(log_data)  # Log the failed upload
        print('Your data is not in good hands')

    # Inform the client that the file data has been received
    print(f"File Data Received")
    conn.send("File data received".encode())

def Authenticate_User(conn, addr):
    # Receive encrypted data from the client
    encrypted_data = conn.recv(SIZE).decode()
    
    # Print the received encrypted data for debugging purposes
    print(f"Encrypted data received: {encrypted_data}")
    
    # Decrypt the received data
    decrypted_data = Decrypt_Data(encrypted_data)
    
    # Print the decrypted data for debugging purposes
    print(f"Decrypted data: {decrypted_data}")

    # Split the decrypted data into username and password
    username, password = decrypted_data.decode().split('\n')
    
    # Print the username and password for debugging purposes
    print(f"Username: {username}, Password: {password}")
    
    # Check if the username exists in the credentials dictionary and if the password matches
    if username in credentials and credentials[username] == password:
        # Send a success message to the client
        conn.send("Authentication successful".encode())  
        
        # Log the successful authentication attempt
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Auth", f"{username},:{password}", "Successful"]
        Log_To_CSV(log_data)  
        
        # Print a success message for debugging purposes
        print('Your Authentication is Successful')
        
        # Return True indicating successful authentication
        return True
    else:
        # Send a failure message to the client
        conn.send("Authentication failed".encode())  
        
        # Log the unsuccessful authentication attempt
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Auth", f"{username},:{password}", "Unsuccessful"]
        Log_To_CSV(log_data)  
        
        # Print a failure message for debugging purposes
        print('Your Authentication is failed')
        
        # Return False indicating failed authentication
        return False
    
def Download_File(conn, addr):
    # Receive the filename from the client
    file_name = conn.recv(SIZE).decode()
    print(f"Filename: {file_name} received")
    conn.send("filename received".encode())  # Acknowledgment to the client

    # Check if the file the client needs exists on the server
    if os.path.exists("Received Data/" + file_name):
        # Send a message to the client indicating that the file exists
        conn.send("Exist".encode())
        print("File exists")

        # Receive a message from the client (could be a confirmation or further instructions)
        msg = conn.recv(SIZE).decode()
        print(msg)

        # Read, encrypt, and send the file data to the client
        with open("Received data/" + file_name, 'r') as file:
            data = file.read()
            conn.send(Encrypt_Data(data))

        # Create chunks from the file and calculate the Merkle tree root hash
        file_chunk = Chunk_File("Received Data/" + file_name, 1024)
        hash_val = Merkle_Tree(file_chunk)
        print(f"Hash value: {hash_val}")
        conn.send(hash_val.encode())  # Send the hash value to the client

        # Log the successful download
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Download", file_name, "Successful"]
        Log_To_CSV(log_data)
    else:
        # Send a message to the client indicating that the file does not exist
        conn.send("NotExist".encode())

        # Log the failed download attempt
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Download", file_name, "File not found"]
        Log_To_CSV(log_data)
        print("File does not exist")
        
def Show_Files(conn, addr):
    # Initialize an empty list to store filenames
    files = []

    # Iterate over all files in the "Received Data" directory
    for file in os.listdir('./Received Data'):
        # Check if the file has a ".txt" extension
        if file.endswith(".txt"):
            # Add the file to the list
            files.append(file)

    # Check if there are any files in the list
    if files:
        # Join the list of filenames into a single string separated by newlines
        files = '\n'.join(files)
        print("Files: \n", files)  # Print the filenames
    else:
        # If no files were found, set the files variable to "None"
        files = "None"

    # Receive a message from the client (could be a confirmation or further instructions)
    msg = conn.recv(SIZE).decode()

    # Send the list of filenames (or "None") to the client
    conn.send(files.encode())

    # Log the action of sending file names
    log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Get File Names"]
    Log_To_CSV(log_data)

    # Print a confirmation message
    print("File names sent!")
    
def main():
    # Print a message indicating that the server is starting
    print("Server is starting...")

    # Create a new socket using the IPv4 address family and TCP protocol
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the specified address and port
    server.bind(ADDR)

    # Enable the server to accept connections, with a default backlog
    server.listen()
    print("Server is listening")

    # Continuously accept and handle client connections
    while True:
        # Accept a new connection from a client
        conn, addr = server.accept()
        print(f"New connection: {addr} connected.")

        # Log the new connection with the current date, time, and client address
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "New connection"]
        Log_To_CSV(log_data)

        # Receive the type of transfer (Upload, Download, or Show) from the client
        transfer_type = conn.recv(SIZE).decode()
        print(f"Received Transfer type: {transfer_type}")
        conn.send("Received Transfer type".encode())  # Acknowledgment to the client

        # If the client wants to upload files to the server
        if transfer_type == "Upload":
            Upload_File(conn, addr)

        # If the client wants to download files from the server
        elif transfer_type == "Download":
            Download_File(conn, addr)

        # If the client wants to see the list of files on the server
        elif transfer_type == "Show":
            Show_Files(conn, addr)
        
        # If the client wants to authenticate to the server
        elif transfer_type == "Auth":
            Authenticate_User(conn, addr)

        else:
            # Handle invalid transfer type received from the client
            print("Invalid Transfer Type Received")
            break

    # Close the connection with the client
    conn.close()
    print(f"Disconnected with {addr}")
    return
    
if __name__ == '__main__':
    # Check if the "Received Data" directory does not exist
    if not os.path.exists("Received Data"):
        # Create the "Received Data" directory
        os.makedirs("Received Data")
        print("Directory 'Received Data' created.")

    # Check if the file "logs.csv" does not exist
    if not os.path.exists("logs.csv"):
        # Open the file "logs.csv" in write mode with no newline character
        with open("logs.csv", mode='w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file)
            # Write the header row to the CSV file
            writer.writerow(["Date", "Timestamp", "Client Address", "Event", "Filename", "Status"])
    
    # Call the main function to start the server
    main()