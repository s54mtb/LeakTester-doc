
import serial
import time
import datetime
import sys

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

# Function to set pressure
def set_pressure(p):
    if p == 0:
        print("Error: Pressure cannot be zero.")
        return "Error: Pressure cannot be zero."
    elif p < 0:
        command = "VAL:VAC"
    else:
        command = "VAL:PRES"
    
    # Send the command with the parameter
    send_data(f"CONF:PRES {p}")
    response = receive_data()
    
    # Send the VAL command based on pressure
    send_data(command)
    response += "\n" + receive_data()
    
    return response


# Main entry
try:
    
    send_data("*rst")  # Send a string
    time.sleep(0.1)  # Wait a moment before receiving
    received = receive_data()  # Receive a response
    print(received);
    
    set_pressure(100);  # set pressure to 100mbar
    
    time.sleep(0.1)  # Wait a moment before pumping
    send_data("PUMP:STA:TARG:CLO"); # start the pump and seal

    print("Waiting for pressure stabilisation... ")
    time.sleep(1)  # wait a moment before start measurement
    # Flush the receive buffer before making measurements
    ser.reset_input_buffer()

    # make 100 measurements
    for i in range(100):
        
        # Query pressure
        send_data("meas:pres?")
        pressure = receive_data()  # Assume it returns a numeric string
        print(pressure)
 
    
finally:
    ser.close()  # Always close the port when done
