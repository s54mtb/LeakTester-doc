"""
This script performs the following tasks:
1. Initializes a serial connection to a device on COMx with a baud rate of 115200.
2. Initializes the measuring interface for pressure, activates the flow sensor, configure the pulse duration and start pumping the air to the preset value
3. Queries the device 100 times to retrieve both pressure and flow data.
4. For each query, the script captures and prints the pressure, flow rate, temperature, bubbles detected, and overflow detected.
5. Each reading includes a timestamp in the format (DD.MM.YYYY HH:MM:SS.mmm).
6. When the loop reaches half way, the script sends the command "PUL:TRIG" to the device activating the pinch valve.
"""


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


# Function to parse flow result
def parse_flow_result(flow_response):
    try:
        flow_rate, temperature, bubbles_detected, overflow_detected = flow_response.split(',')
        flow_rate = float(flow_rate)
        temperature = float(temperature)
        bubbles_detected = int(bubbles_detected)
        overflow_detected = int(overflow_detected)
        return flow_rate, temperature, bubbles_detected, overflow_detected
    except ValueError:
        print(f"Error parsing flow response: {flow_response}")
        return None, None, None, None


# Main entry
try:
    readings = []
    
    send_data("*rst")  # Send a string
    time.sleep(0.1)  # Wait a moment before receiving
    received = receive_data()  # Receive a response
    print(received);
    
    set_pressure(110);  # set pressure to 100mbar

    send_data("CONF:PUL 0.1")   # set output pulse to 100ms
    
    send_data("FLOW:STA 0")   # start the flow sensor with water calibration
    
    time.sleep(0.1)  # Wait a moment before pumping
    send_data("PUMP:STA:TARG:CLO"); # start the pump and seal

    print("Waiting for pressure stabilisation... 5")
    time.sleep(1)  # wait a moment before start measurement
    print("Waiting for pressure stabilisation... 4")
    time.sleep(1)  # wait a moment before start measurement
    print("Waiting for pressure stabilisation... 3")
    time.sleep(1)  # wait a moment before start measurement
    print("Waiting for pressure stabilisation... 2")
    time.sleep(1)  # wait a moment before start measurement
    print("Waiting for pressure stabilisation...1 ")
    time.sleep(1)  # wait a moment before start measurement
    # Flush the receive buffer before making measurements
    ser.reset_input_buffer()

    # make 100 measurements
    for i in range(100):
        sys.stdout.write('M')
        # Get the current datetime
        now = datetime.datetime.now()
        # format the timestamp
        timestamp = now.strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]
        
        # Query pressure
        send_data("meas:pres?")
        pressure = receive_data()  # Assume it returns a numeric string
        
        # Query flow
        send_data("meas:flow?")
        flow_response = receive_data()  # Assume it returns a comma-separated string
        
        # Parse flow response
        flow_rate, temperature, bubbles_detected, overflow_detected = parse_flow_result(flow_response)
        
        # Store the readings
        readings.append((timestamp, pressure, flow_rate, temperature, bubbles_detected, overflow_detected))

        # Send command "PUL:TRIG" when loop is half way
        if (i + 1) == 50:
            send_data("PUL:TRIG")

        #time.sleep(0.0001)  # Wait for 5 ms between readings
    print("<")
    
    # Print all readings
    for i, (timestamp, pressure, flow_rate, temperature, bubbles_detected, overflow_detected) in enumerate(readings, start=1):
        print(f"Reading {i} at {timestamp}: Pressure = {pressure}, Flow Rate = {flow_rate}, "
              f"Temperature = {temperature}, Bubbles Detected = {bubbles_detected}, Overflow Detected = {overflow_detected}")

    
finally:
    ser.close()  # Always close the port when done
