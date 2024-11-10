# RPC with custom UDP

## Team Information

This project was developed as part of the CSN-341 Computer Networks course. Our team members are:

- Divyansh Jain - 22114032 - divyansh_j@cs.iitr.ac.in
- Aaditya Aren - 22114001 - aaditya_a@cs.iitr.ac.in
- Alind Sharma - 22113013 - alind_s@cs.iitr.ac.in
- Kunal Bansal - 22115083 - kunal_b@cs.iitr.ac.in
- Aviral Vishwakarma - 22114017 - aviral_v@cs.iitr.ac.in

### Course Details
- **Course**: CSN-341 Computer Networks
- **Instructor**: Dr. Sandeep Kumar Garg
- **Semester**: Fall 2024
- **Institution**: Indian Institute of Technology (IIT) Roorkee

### Project Overview
This project demonstrates the practical application of network programming concepts learned in our Computer Networks course. It implements a client-server architecture to perform remote mathematical operations, showcasing our understanding of:

- Socket programming
- Client-server communication
- User authentication
- Graphical User Interface (GUI) development

We'd like to thank our instructor and peers for their support and feedback throughout the development of this project.


## Features

### Server

- UDP socket binding and listening
- Request handling and response generation
- Real-time logging of all operations
- Support for multiple mathematical functions
- Acknowledgment system for reliable communication


### Client

- User authentication system
- Dynamic parameter handling
- Progress tracking for RPC calls
- Real-time logging
- Tabbed interface for better organization
- Modern and responsive GUI


## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Dependencies

- PyQt6==6.4.0
- socket (built-in)
- json (built-in)
- time (built-in)
- sys (built-in)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Demigod345/RPC-with-custom-UDP.git
cd RPC-with-custom-UDP
```

2. Make the setup script executable:


```shellscript
 chmod +x setup.sh
```

3. Run the setup script:


```shellscript
 ./setup.sh
```

Here's an improved version of the Usage section for your README:

## Usage

Follow these steps to set up and use the application:

1. **Start the server:**

   Open a terminal and run:
   ```bash
   python server_frontend.py
   ```

2. **Launch the client:**

   Open a new terminal window and execute:
   ```bash
   python client_frontend.py
   ```

3. **User Authentication:**
   - When the client interface appears, you can either log in with existing credentials or create a new account.

4. **Using the GUI:**
   Once logged in, you can perform mathematical operations remotely:

   a. Choose a mathematical function:
      - Addition
      - Multiplication
      - Subtraction

   b. Input parameters:
      - Enter at least two numerical values
      - Add more parameters as needed

   c. Execute the operation:
      - Click the "Call Remote Function" button to send your request to the server

   d. Review the results:
      - View the calculated result
      - Check the operation logs
      - See a summary of the performed calculation

5. **Logout:**
   - Use the logout button when you're done to securely end your session


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
