# Import the os module for interacting with the operating system
import os

# Import the sha256 function from the hashlib module for hashing
from hashlib import sha256

# Import the socket module for network communication
import socket

# Import the pandas library for data manipulation and analysis
import pandas as pd

# Import the streamlit library for creating web applications
import streamlit as st

# Import the Fernet class from the cryptography.fernet module for encryption
from cryptography.fernet import Fernet


# The buffer size for sending and receiving data over the network is 102400 bytes (100 KB)
SIZE = 102400 
# Define the port number for the server
PORT = 4455
# Define the encryption key for Fernet encryption
KEY = 'epVKiOHn7J0sZcJ4-buWQ5ednv3csHdQHfvEKk0qVvk='

# Function to encrypt data using Fernet symmetric encryption
def Encrypt_Data(data):
    # Create a Fernet object using the provided encryption key (KEY).
    fernet = Fernet(KEY)
    
    # Encrypt the input data (converted to bytes) using the Fernet object.
    cipherText = fernet.encrypt(data.encode())
    
    # Return the encrypted data (cipherText).
    return cipherText
    
# Function to decrypt data using Fernet symmetric encryption
def Decrypt_Data(data):
    # Create a Fernet object using the provided encryption key (KEY)
    fernet = Fernet(KEY)
    
    # Decrypt the input data (converted to bytes) using the Fernet object
    plainText = fernet.decrypt(data.encode())
    
    # Return the decrypted data (plainText)
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

    # Combine the left and right hashes, hash them, and return the result
    return sha256(left_hash.encode() + right_hash.encode()).hexdigest()
    
def Show_Files(ip):
    # Get the IP address of the local machine
    IP = socket.gethostbyname(socket.gethostname()) 
    # Change the value to input ip while connecting to server on another system
    # IP = ip
    
    # Define the server address using the IP and a predefined PORT
    server_address = (IP, PORT)

    try:
        # Establish a connection to the server creating a new socket object using the 
        # IPv4 address family (AF_INET) and the TCP protocol (SOCK_STREAM)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)

        # Send the "Show" message to the server to request file names
        client.send("Show".encode())

        # Receive and decode the acknowledgment message from the server
        msg = client.recv(SIZE).decode()
        print(msg)
        
    except:
        # Handle connection failure
        st.error("Connection Failure! Check if the server is active.")
        return
    
    # Send a message indicating that filenames are being sent
    client.send("Sending Filenames".encode())
    
    # Receive and decode the list of filenames from the server
    file_names = client.recv(SIZE).decode()
    
    # Close the connection to the server
    client.close()
    
    # Print a confirmation message
    print("File names Received")
    
    # Return the list of filenames
    return file_names

# Function to upload a file to the server
def Upload_File(filename, ip):
    # Get the IP address of the local machine
    IP = socket.gethostbyname(socket.gethostname()) 
    # Uncomment the next line to use the provided IP address instead
    # IP = ip
    server_address = (IP, PORT)  # Define the server address using IP and PORT

    try:
        # Establish a connection to the server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)

        # Send the "Upload" message to the server
        client.send("Upload".encode())

        # Receive acknowledgment from the server
        ack_msg1 = client.recv(SIZE).decode()
        print(ack_msg1)
        
    except:
        # Handle connection failure
        st.error("Connection Failure! Check if the server is active.")
        return

    # Send the filename to the server
    client.send(filename.encode())

    # Receive acknowledgment from the server
    ack_msg2 = client.recv(SIZE).decode()
    print(f"Server: {ack_msg2}")

    # Read the contents of the file
    with open(filename, "r") as file:
        data = file.read()
        # Send encrypted file data to the server
        client.sendall(Encrypt_Data(data))

    # Create file chunks and calculate Merkle tree root hash
    file_chunk = Chunk_File(filename, 1024)
    hash_value = Merkle_Tree(file_chunk)
    print(f"Hash value: {hash_value}")

    # Send calculated hash to the server
    client.send(hash_value.encode())

    # Receive verification of data integrity from the server
    verfi_msg = client.recv(SIZE).decode()
    if verfi_msg == "True":
        st.success("Data Integrity assured!", icon="✅")
    else:
        st.error("Data might be lost.")
    
    # Receive acknowledgment of file data receipt from the server
    ack_msg3 = client.recv(SIZE).decode()
    print(f"Server: {ack_msg3}")
    
    # Close the connection
    client.close()  
    if ack_msg3 == "File data received":
        return True
    return False
    
def Authenticate(username, password, ip):
    # Get the IP address of the local machine
    IP = socket.gethostbyname(socket.gethostname()) 
    # Uncomment the next line to use the provided IP address instead
    # IP = ip
    server_address = (IP, PORT)  # Define the server address using IP and PORT
    try:
        # Establish a connection to the server creating a new socket object using the 
        # IPv4 address family (AF_INET) and the TCP protocol (SOCK_STREAM)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)
        
        # Send the "Auth" message to the server
        client.send("Auth".encode())

        # Receive acknowledgment from the server
        ack_msg1 = client.recv(SIZE).decode()
        print(ack_msg1)
        
        
    except:
        # Handle connection failure
        st.error("Connection Failure! Check if the server is active.")
        return
    
    # Encrypt username and password
    encrypted_data = Encrypt_Data(f"{username}\n{password}")
    
    # Send the encrypted data to the server
    client.sendall(encrypted_data)
    
    # Receive acknowledgment from the server
    ack_msg2 = client.recv(SIZE).decode()
    print(f"Server: {ack_msg2}")
    
    # Close the connection
    client.close()  
    if ack_msg2 == "Authentication successful":
        return True
    return False
    
# Function to download a file from the server
def Download_File(filename, ip):
    # Get the IP address of the local machine
    IP = socket.gethostbyname(socket.gethostname()) 
    # Uncomment the next line to use the provided IP address instead
    # IP = ip
    server_address = (IP, PORT)  # Define the server address using IP and PORT

    try:
        # Establish a connection to the server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)

        # Send the "Download" message to the server
        client.send("Download".encode())

        # Receive acknowledgment from the server
        ack_msg1 = client.recv(SIZE).decode()
        print(ack_msg1)
    except:
        # Handle connection failure
        st.error("Connection Failure! Check if the server is active.")
        return
    
    # Send the filename to the server
    client.send(filename.encode())
    
    # Receive acknowledgment from the server
    ack_msg2 = client.recv(SIZE).decode()
    print(ack_msg2)
    
    # Check if the file exists on the server
    exist = client.recv(SIZE).decode()
    print(f"Exists? {exist}")
    client.send("Downloading".encode())  # Send acknowledgment to start downloading
    
    if exist == "Exist":
        # Receive encrypted file data from the server
        data = client.recv(SIZE).decode()

        os.makedirs("Downloaded", exist_ok=True)
        # Decrypt and write the data to a file in the "Downloaded" folder
        with open("Downloaded/" + filename, 'w') as f:
            f.write(Decrypt_Data(data).decode())

        # Receive the hash value of the downloaded file from the server
        received_hash_val = client.recv(SIZE).decode()
        print(f"Hash value {received_hash_val}")
        client.close()

        # Create file chunks and calculate Merkle tree root hash
        file_chunk = Chunk_File("Downloaded/" + filename, 1024)
        file_hash_value = Merkle_Tree(file_chunk)
        print(f"Hash value: {file_hash_value}")

        # Verify data integrity
        if file_hash_value == received_hash_val:
            print("Downloaded data has the same hash values")
            st.success("Data Integrity assured!", icon="✅")
            return True
        else:
            st.error("Data might be lost", icon="🚨")
            return False
        
    elif exist == "NotExist":
        # Handle case where the file does not exist on the server
        st.error("No such file exists in the server", icon="🚨")
        return False
    else:
        print("Some other error")
        return False
        
# Streamlit web application entry point
if __name__ == "__main__":
    # Set the title of the Streamlit app
    st.title("Secure File Transfer System")
    # Set the subheader of the Streamlit app
    st.subheader("Encrypt and Verify in a Flash ⚡")
    
    ip = st.text_input("Enter IP address of the server: ")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login = st.button("Login")
    
    # Check if the user has attempted to log in
    if login:
        try:
            # Attempt to authenticate the user with the provided username, password, and IP address
            if Authenticate(username, password, ip):
                # If authentication is successful, display a success message
                st.success("Authentication successful! You can now use the application.", icon="✅")
            else:
                # If authentication fails, display an error message with an icon
                st.error('Authentication Failed! You can\'t now use the application.', icon="🚨")
        except:
            # Handle any exceptions that occur during the authentication process
            pass         
    # Add a divider in the Streamlit app
    st.divider()
    
    # Button to show files on the server
    showfiles = st.button("Show Files")
    
    if showfiles:
        try:
            # Call the function to show files on the server
            files = Show_Files(ip)
            print(files)
            if files != "None":
                # Split the files string into a list
                files = files.split("\n")
                # Create a DataFrame to display the files
                df = pd.DataFrame({"Files in the server: ": files})
                # Display the DataFrame in the Streamlit app
                st.dataframe(df, use_container_width=True)
            else:
                # Show a warning if no files are found
                st.warning("No Files in the server.")
        except:
            # Handle any exceptions that occur
            pass
    # Add a divider in the Streamlit app
    st.divider()
    
    # File uploader input for uploading files
    uploaded_file = st.file_uploader("Choose a text file!", accept_multiple_files=True)
    # Button to upload files
    upload = st.button("Upload Files!")
    if upload:
        if uploaded_file:
            filenames = []
            for x in uploaded_file:
                # Call the function to upload the file
                if Upload_File(x.name, ip):
                    # Show success message if the file is uploaded successfully
                    st.success(f'File {x.name} was transferred successfully!', icon="✅")
                    filenames.append(x.name)
                else:
                    # Show error message if there is a problem with the upload
                    st.error(f'There is some problem with transferring {x.name}! Try again', icon="🚨")
            print(filenames)
        else:
            # Show error message if no files are selected for upload
            st.error(f'Browse files to upload first!', icon="🚨")
    # Add a divider in the Streamlit app
    st.divider()
    
    # Text input for downloading a certain file from the server
    filename = st.text_input("Enter file you want to download from the server: ")
    # Button to download the file
    download = st.button("Download File")
    if download:
        if filename:
            # Call the function to download the file
            if Download_File(filename, ip):
                # Show success message if the file is downloaded successfully
                st.success(f'File {filename} was downloaded successfully! Check your "Downloaded" folder.', icon="✅")
            else:
                # Show error message if there is a problem with the download
                st.error(f'Downloading of {filename} failed! Try again', icon="🚨")
        else:
            # Show error message if no filename is entered
            st.error(f'Enter a filename to be downloaded first!', icon="🚨")
        