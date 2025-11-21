import serial
import time

SERIAL_PORT = "COM5"  # Change to "COMX" on Linux (e.g., "/dev/rfcomm0")
BAUD_RATE = 115200  # This is assumed; verify for your adapter

# OBD2 Initialization and Query Commands 
INIT_COMMANDS = [
    'ATD', 'ATZ', 'ATE0', 'ATL0', 'ATS0', 'ATH1', 'ATSTFF', 'ATFE', 'ATSP6', 'ATCRA7EC'
]
OBD2_COMMANDS = ['220105', '220101']


def connect_obd2():
    """Establish a serial connection with the OBD2 adapter."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to OBD2 adapter on {SERIAL_PORT}")
        return ser
    except Exception as e:
        print(f"Error connecting to OBD2 adapter: {e}")
        return None


def send_command(ser, command, delay=0.2):
    """Send a command and read the response."""
    cmd_to_send = command + "\r"
    print(f"Sending: {command}")
    ser.write(cmd_to_send.encode())
    time.sleep(delay)
    response = ser.read(ser.in_waiting).decode().strip()
    print(f"Received: {response}")
    return response.replace(" ", "")


def handle_obd2_error(ser, error):
    """
    Handle an OBD2 error similar to the Vue event handler:
      - Print a warning message.
      - Disconnect from the OBD2 adapter.
    """
    print("OBD2_ERROR detected:", error)
    try:
        ser.close()
        print("Disconnected from OBD2 adapter due to error.")
    except Exception as e:
        print("Error disconnecting:", e)


def initialize_obd2(ser):
    """Send the initialization commands to the OBD2 adapter."""
    for cmd in INIT_COMMANDS:
        response = send_command(ser, cmd)
        # Detect error conditions as in the Vue code
        if ("CANERROR" in response or
            "UNABLETOCONNECT" in response or
            "BUFFERFULL" in response):
            handle_obd2_error(ser, response)
            return False  # Abort initialization on error
        time.sleep(0.5)
    return True


def read_obd2_data(ser):
    for current_command in OBD2_COMMANDS:
        response = send_command(ser, current_command, delay=2)
        if ("CANERROR" in response or
                "UNABLETOCONNECT" in response or
                "BUFFERFULL" in response):
            handle_obd2_error(ser, response)
            break  # Exit loop on error
        if "NODATA" in response:
            print("No Data received. Sending ATPC for low power mode.")
            send_command(ser, "ATPC")
        else:
            parsed_data = parse_data(response, current_command)
            print("Parsed Data:", parsed_data)
        # Toggle between commands
        time.sleep(2)


def parse_data(data, command):
    """Parse the OBD2 response based on the command."""
    parsed_data = {}
    try:
        if command == '220105':
            fourthBlock = '7EC24'
            fifthBlock = '7EC25'
            if fourthBlock in data and fifthBlock in data and "7EC26" in data:
                extractedFourthBlock = data[data.index(fourthBlock):data.index(fifthBlock)]
                extractedFourthData = extractedFourthBlock.replace(fourthBlock, '')
                extractedFifthBlock = data[data.index(fifthBlock):data.index("7EC26")]
                extractedFifthData = extractedFifthBlock.replace(fifthBlock, '')
                if extractedFourthData and extractedFifthData:
                    parsed_data = {
                        "SOC_DISPLAY": int(extractedFifthData[:2], 16) / 2,
                        "SOH": ((int(extractedFourthData[2:4], 16) << 8) + int(extractedFourthData[4:6], 16)) / 10
                    }
        elif command == '220101':
            firstBlock = '7EC21'
            secondBlock = '7EC22'
            thirdBlock = '7EC23'
            fourthBlock = '7EC24'
            fifthBlock = '7EC25'
            sixthBlock = '7EC26'
            seventhBlock = '7EC27'
            eigthBlock = '7EC28'

            if (firstBlock in data and secondBlock in data and thirdBlock in data and
                    fourthBlock in data and fifthBlock in data and sixthBlock in data and
                    seventhBlock in data and eigthBlock in data):

                # Extract blocks and remove header identifiers
                extractedFirstBlock = data[data.index(firstBlock):data.index(secondBlock)]
                extractedFirstData = extractedFirstBlock.replace(firstBlock, '')
                extractedSecondBlock = data[data.index(secondBlock):data.index(thirdBlock)]
                extractedSecondData = extractedSecondBlock.replace(secondBlock, '')
                extractedThirdBlock = data[data.index(thirdBlock):data.index(fourthBlock)]
                extractedThirdData = extractedThirdBlock.replace(thirdBlock, '')
                extractedFourthBlock = data[data.index(fourthBlock):data.index(fifthBlock)]
                extractedFourthData = extractedFourthBlock.replace(fourthBlock, '')
                extractedFifthBlock = data[data.index(fifthBlock):data.index(sixthBlock)]
                extractedFifthData = extractedFifthBlock.replace(fifthBlock, '')
                extractedSixthBlock = data[data.index(sixthBlock):data.index(seventhBlock)]
                extractedSixthData = extractedSixthBlock.replace(sixthBlock, '')
                extractedSeventhBlock = data[data.index(seventhBlock):data.index(eigthBlock)]
                extractedSeventhData = extractedSeventhBlock.replace(seventhBlock, '')
                extractedEightBlock = data[data.index(eigthBlock):data.index(eigthBlock) + 18]
                extractedEightData = extractedEightBlock.replace(eigthBlock, '')

                # Calculate chargingBits: extract 10th-12th characters from the 7th block, convert to binary and pad to 8 bits
                charging_int = int(extractedSeventhData[10:12], 16)
                chargingBits = bin(charging_int)[2:].zfill(8)

                if extractedFirstData and extractedSecondData and extractedFourthData:
                    # Inline conversion for signed 8-bit values (for temperatures)
                    battery_min_temperature = int(extractedSecondData[10:12], 16)
                    if battery_min_temperature >= 128:
                        battery_min_temperature -= 256
                    battery_max_temperature = int(extractedSecondData[8:10], 16)
                    if battery_max_temperature >= 128:
                        battery_max_temperature -= 256
                    battery_inlet_temperature = int(extractedThirdData[10:12], 16)
                    if battery_inlet_temperature >= 128:
                        battery_inlet_temperature -= 256

                    # Inline conversion for signed 16-bit value (battery current from concatenated first 2 bytes)
                    battery_current = int(extractedSecondData[0:2] + extractedSecondData[2:4], 16)
                    if battery_current >= 32768:
                        battery_current -= 65536

                    cumulative_energy_charged = (
                                                        (int(extractedSixthData[0:2], 16) << 24) +
                                                        (int(extractedSixthData[2:4], 16) << 16) +
                                                        (int(extractedSixthData[4:6], 16) << 8) +
                                                        int(extractedSixthData[6:8], 16)
                                                ) / 10

                    cumulative_energy_discharged = (
                                                           (int(extractedSixthData[8:10], 16) << 24) +
                                                           (int(extractedSixthData[10:12], 16) << 16) +
                                                           (int(extractedSixthData[12:14], 16) << 8) +
                                                           int(extractedSeventhData[0:2], 16)
                                                   ) / 10

                    # Determine charging flags based on specific bits of chargingBits and values in extractedFirstData
                    # For CHARGING: bit at index 4 must be 1 and bit at index 5 must be 0.
                    charging = 1 if int(chargingBits[4]) == 1 and int(chargingBits[5]) == 0 else 0
                    # NORMAL_CHARGE_PORT: charging bit at index 1 must be 1 and byte at positions 12-14 must be '03'
                    normal_charge_port = 1 if int(chargingBits[1]) == 1 and extractedFirstData[12:14] == '03' else 0
                    # RAPID_CHARGE_PORT: charging bit at index 1 must be 1 and byte at positions 12-14 must not be '03'
                    rapid_charge_port = 1 if int(chargingBits[1]) == 1 and extractedFirstData[12:14] != '03' else 0

                    parsed_data = {
                        "SOC_BMS": int(extractedFirstData[2:4], 16) / 2,
                        "DC_BATTERY_VOLTAGE": ((int(extractedSecondData[4:6], 16) << 8) + int(extractedSecondData[6:8],
                                                                                              16)) / 10,
                        "CHARGING": charging,
                        "NORMAL_CHARGE_PORT": normal_charge_port,
                        "RAPID_CHARGE_PORT": rapid_charge_port,
                        "BATTERY_MIN_TEMPERATURE": battery_min_temperature,
                        "BATTERY_MAX_TEMPERATURE": battery_max_temperature,
                        "BATTERY_INLET_TEMPERATURE": battery_inlet_temperature,
                        "DC_BATTERY_CURRENT": battery_current * 0.1,
                        "CUMULATIVE_ENERGY_CHARGED": cumulative_energy_charged,
                        "CUMULATIVE_ENERGY_DISCHARGED": cumulative_energy_discharged,
                        "AUX_BATTERY_VOLTAGE": int(extractedFourthData[10:12], 16) / 10
                    }
                    # Calculate battery power (in kW)
                    parsed_data["DC_BATTERY_POWER"] = parsed_data["DC_BATTERY_CURRENT"] * parsed_data[
                        "DC_BATTERY_VOLTAGE"] / 1000

        '''
        elif command == '220101':
            firstBlock = '7EC21'
            secondBlock = '7EC22'
            if firstBlock in data and secondBlock in data and "7EC23" in data:
                extractedFirstBlock = data[data.index(firstBlock):data.index(secondBlock)]
                extractedFirstData = extractedFirstBlock.replace(firstBlock, '')
                extractedSecondBlock = data[data.index(secondBlock):data.index("7EC23")]
                extractedSecondData = extractedSecondBlock.replace(secondBlock, '')
                if extractedFirstData and extractedSecondData:
                    parsed_data = {
                        "SOC_BMS": int(extractedFirstData[2:4], 16) / 2,
                        "DC_BATTERY_VOLTAGE": ((int(extractedSecondData[4:6], 16) << 8) + int(extractedSecondData[6:8], 16)) / 10
                    }
            '''
    except Exception as e:
        print("Error parsing data:", e)
    return parsed_data


if __name__ == "__main__":
    ser = connect_obd2()
    if ser:
        initialized = initialize_obd2(ser)
        if initialized:
            read_obd2_data(ser)
        else:
            print("Initialization failed due to an error.")
        ser.close()
    else:
        print("Could not establish connection to the OBD2 adapter.")




'''
OUTPUT

Connected to OBD2 adapter on COM5
Sending: ATD
>
Sending: ATZ
>
Sending: ATE0
>
Sending: ATL0
>
Sending: ATS0
>
Sending: ATH1
>
Sending: ATSTFF
>
Sending: ATFE
>
Sending: ATSP6
>
Sending: ATCRA7EC
>
Sending: 220105
>
Parsed Data: {'SOC_DISPLAY': 39.5, 'SOH': 100.0}
Sending: 220101
>
Parsed Data: {'SOC_BMS': 38.0, 'DC_BATTERY_VOLTAGE': 356.7}

Process finished with exit code 0

'''
