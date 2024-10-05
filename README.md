# Secure File Transfer Application

### Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Usage](#usage)
4. [Requirements](#requirements)
5. [Installation](#installation)
6. [Contributing](#contributing)

### Project Overview
This project implements a secure file transfer application using Python, featuring end-to-end encryption, authentication, and integrity verification. It provides a web-based interface for easy file management between clients and servers.

### Features
- **End-to-End Encryption**: Uses Fernet symmetric encryption for secure data transmission.
- **Authentication**: Implements a simple authentication system for secure access.
- **Integrity Verification**: Utilizes Merkle trees to verify the integrity of transferred files.
- **Web Interface**: Provides a user-friendly interface using Streamlit for easy file operations.
- **Cross-platform Compatibility**: Designed to work across different operating systems.

### Usage
To use this Secure File Transfer Application:

1. Start the server:
           `python server.py`
2. Run the client script:
           `python -m streamlit client.py`
3. Follow the prompts to perform various operations:
   - Login to authenticate
   - View available files on the server
   - Upload files to the server
   - Download files from the server

### Requirements
- Python 3.x
- cryptography==40.0.0
- pandas==1.5.3
- streamlit==1.16.2
- socket==22.0.0
- datetime==4.9.0
- hashlib==2023.7.30
- os==1.17.1

### Installation
1. Clone this repository: `git clone https://github.com/Youssef-Mohammed72/CodeAlpha_Secure-File-Transfer-Application.git`
2. Navigate to the project directory: `CodeAlpha_Secure-File-Transfer-Application`
3. Install dependencies: `pip install -r requirements.txt`

### Contributing
Contributions are welcome! Please fork this repository and submit pull requests.

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments
This project was developed using Python, cryptography, pandas, and Streamlit libraries during an internship at CodeAlpha.
