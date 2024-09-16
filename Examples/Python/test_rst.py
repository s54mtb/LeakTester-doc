import serial
import time

# Set up the serial connection
ser = serial.Serial('COM7', 115200, timeout=1)  # Adjust baudrate as needed

# Give the serial connection a moment to initialize
time.sleep(.1)

# Function to send data
def send_data(data):
    data_with_terminator = data + '\n\r'  # Add /n/r to the end of the data
    ser.write(data_with_terminator.encode())  # Convert string to bytes and send
#    print(f"Sent: {data_with_terminator}")
    
# Function to receive data
def receive_data():
    data = ser.readline().decode().strip()  # Read line, decode to string, and strip newline
#    print(f"Received: {data}")
    return data

# Main entry
try:   
    send_data("*rst")  # Send a string
    time.sleep(0.1)  # Wait a moment before receiving
    received = receive_data()  # Receive a response
    print(received);
    send_data("*idn?")  # Send a string
    received = receive_data()  # Receive a response
    print(received);
    
finally:
    ser.close()  # Always close the port when done
