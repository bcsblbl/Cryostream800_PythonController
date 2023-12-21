import os
import re
import socket
import struct
import subprocess
from subprocess import CalledProcessError, PIPE
import sys
import time

# Useful for parsing XML files
# Should be activated if not using _buildOxCryoPropertiesInline() Method
# import xml.etree.ElementTree as ET

# Python 2.7 Edition.
# Remember to run with Python2.7 otherwise it will not work.
# Porting to Python3 should be straightforward.
# We are running this version for business reasons, but we could for sure use Python3.

#Authors:
#John Taylor, Berkeley National Laboratory (Email: jrtaylor_at_lbl.gov)
#Gabriel Gazolla, Berkeley National Laboratory (Email: gabrielgazolla_at_lbl.gov)

# Controls Cryostream 800 (Oxford Cryosystems)
class Cryostream800:

    # Constructor
    def __init__(self, ip):

        # Stores IP of the Cryostream 800
        self._ip = ip

        # Port where status is broadcasted as UDP to all subnetwork
        self._statusPort = 30304

        # Port where commands are sent as UDP to the Cryostream 800 device.
        self._commandsPort = 30305       

        # Folder containing two Cryostream 800 files:
        # [1] https://connect.oxcryo.com/ethernetcomms/OxcryoProperties.xml
        # [2] https://connect.oxcryo.com/ethernetcomms/Cryostream.xml
        # !!! Needs to be defined if inline functions are not used
        # oxCryoDataFolderPath = "/home/staff/gabriel/Development/sourcecode/Cryostream/cryostream800-Python2/oxcryoData/"

        # Path for OxCryo Properties XML File
        # File also available at https://connect.oxcryo.com/ethernetcomms/OxcryoProperties.xml
        # !!! Needs to be defined if inline functions are not used
        # self._oxcryoPropertiesFilepath = oxCryoDataFolderPath + "OxcryoProperties.xml"

        # Parses the XML file with the OxCryo properties and creates a dictionary
        # File also available at https://connect.oxcryo.com/ethernetcomms/Cryostream.xml
        #self._oxCryoProperties = self._buildOxCryoProperties(self._oxcryoPropertiesFilepath)

        # Inline Version, increases efficiency
        self._oxCryoProperties = self._buildOxCryoPropertiesInline()

        # Path for file with Cryostream Data
        # Stores the List of Commands
        # !!! Needs to be defined if inline functions are not used
        # self._cryostreamFilePath = oxCryoDataFolderPath + "Cryostream.xml" 

        # Dictionary which stores the List of Commands
        # For instance self.commandBook["Restart"], retrieves code 10.
        # Which is the code that needs to be sent as a command

        # If reading from file, less efficient
        # !!! Needs to be defined if inline functions are not used
        # self._commandBook = self._getCommandBook(self._cryostreamFilePath)

        # If not reading from file, more efficient, pre-calculated
        self._commandBook = self._getCommandBookInline()

        #print("Updating Status Information...")
        # Update Status:
        # 1) Retrieves the binary status packet from the network
        # 2) Parses the binary status packet
        # 3) Updates the last Status dictionary
        self._updateStatus() 

    # Method to print a Cryostream 800 object
    # Pending Implementation
    def __str__(self):
        s = ""
        s += "Model: Cryostream 800"
        return s

    #==================================
    #=== Parsing and Initialization ===
    #==================================

    # Populates a Dictionary called _oxCryoProperties with All Cryostream 800 Properties
    # ID, Name
    # 1002, Min Temp
    # 1003, Max Temp
    # 1031, Total Hours
    # Programming Use:
    # _oxCryoProperties[1003] would return the string "Max Temp"
    # File also available at: https://connect.oxcryo.com/ethernetcomms/OxcryoProperties.xml
    def _buildOxCryoProperties(self, oxcryoPropertiesXMLpath):

        try:
            # Parses XML and Add Entries to the Dictionary
            tree = ET.parse(oxcryoPropertiesXMLpath)
            root = tree.getroot()
            properties = root.find(".//LIST_OF_PROPERTIES")

            if properties is not None:

                tempDictionary = dict()

                for property_elem in properties.findall("PROPERTY"):
                    name = property_elem.get("name")
                    prop_id = int(property_elem.get("id"))
                    tempDictionary[prop_id] = name

                #print tempDictionary
                return tempDictionary

        except ET.ParseError:
            print("Invalid XML format")
            exit(1)

    # Populates a Dictionary called _oxCryoProperties with All Cryostream 800 Properties
    # This method avoids us to read from a file
    # ID, Name
    # 1002, Min Temp
    # 1003, Max Temp
    # 1031, Total Hours
    # Programming Use:
    # _oxCryoProperties[1003] would return the string "Max Temp"
    # File also available at: https://connect.oxcryo.com/ethernetcomms/OxcryoProperties.xml
    def _buildOxCryoPropertiesInline(self):


        tempDictionary = dict()

        tempDictionary = {2048: 'Phase remaining', 2500: 'Ambient pressure', 2501: 'Ambient humidity', 2502: 'Ambient temp', 2503: 'Live ADC 5', 2504: 'Live ADC 6', 2505: 'Live heater current 1', 2506: 'Live heater current 2', 2507: 'Live heater current 3', 2508: 'Live sensor current 1', 2509: 'Live sensor current 2', 2510: 'Live sensor current 3', 2511: 'Real time', 2512: 'Real date', 2513: 'Average evap heat', 2514: 'Unmapped gas temp', 2515: 'Coldhead state', 2516: 'Service state', 2517: 'Last regen date', 2518: 'Days since regen', 2519: 'Shield flow mode', 2520: 'Shield flow requested', 2600: 'Last run date', 2601: 'Last error date', 2602: 'Error status 1', 2603: 'Error status 2', 2604: 'Error status 3', 2605: 'Error status 4', 2606: 'Error gas heat I', 2607: 'Error gas heat V', 2608: 'Error evap heat I', 2609: 'Error evap heat V', 2610: 'Error suct heat I', 2611: 'Error suct heat V', 2612: 'Error ADC 5', 2613: 'Error ADC 6', 2614: 'Error SRB status', 2615: 'Error outer flow', 2616: 'Error selected gas', 2617: 'Error detected gas', 2618: 'Error AF status', 2619: 'Error CD fault', 2620: 'Error water temp', 2621: 'Error He supply', 2622: 'Error He return', 7000: 'Temp units', 7001: 'Keyboard sounds', 7002: 'Coldhead LEDs', 5000: 'Comms packet size', 5001: 'Comms packet id', 5002: 'Comms packet checksum', 3001: 'Stage 1 temp', 3002: 'Stage 1 set temp', 3003: 'Stage 1 heat', 3004: 'Stage 1 load', 3005: 'Stage 2 temp', 3006: 'Stage 2 set temp', 3007: 'Stage 2 heat', 3008: 'Stage 2 load', 1000: 'Device', 1001: 'Hardware', 1002: 'Min temp', 1003: 'Max temp', 1004: 'Control firmware', 1005: 'Peripherals', 1006: 'Smart mode', 1010: 'Test ADC 1', 1011: 'Test ADC 2', 1012: 'Test heater 1', 1013: 'Test heater 2', 1014: 'Test ADC 3', 1015: 'Test gas flow', 1016: 'Test EEPROM', 1017: 'Self-check', 1018: 'Test heater 3', 1019: 'Test ADC 4', 1020: 'ADC1 calibration R', 1021: 'ADC1 calibration SC', 1022: 'ADC2 calibration R', 1023: 'ADC2 calibration SC', 1024: 'ADC3 calibration R', 1025: 'ADC3 calibration SC', 1026: 'ADC4 calibration', 1027: 'Controller options', 1028: 'Controller number', 1029: 'Coldhead number', 1030: 'Commissioning date', 1031: 'Total hours', 1032: 'Default cool temp', 1033: 'Temp units', 1034: 'Last shutdown', 1035: 'Sensor 1 number', 1036: 'Sensor 2 number', 1037: 'Sensor 3 number', 1040: 'Live ADC 1', 1041: 'Live ADC 2', 1042: 'Live ADC 3', 1043: 'Live ADC 4', 1044: 'Live heater 1', 1045: 'Live heater 2', 1046: 'Live heater 3', 1050: 'Set temp', 1051: 'Sample temp', 1052: 'Temp error', 1053: 'Run mode', 1054: 'Phase id', 1055: 'Ramp rate', 1056: 'Target temp', 1057: 'Evap temp', 1058: 'Suct temp', 1059: 'Phase time remaining', 1060: 'Gas flow', 1061: 'Gas heat', 1062: 'Evap heat', 1063: 'Average suct heat', 1064: 'Back pressure', 1065: 'Alarm code', 1066: 'Run time', 1067: 'Evap shift', 1068: 'Turbo mode', 1069: 'Average gas heat', 1070: 'Suct heat', 1071: 'Suspended', 1072: 'Received', 1073: 'Missed', 1080: 'Last shutdown', 1081: 'Last run time', 1082: 'Error shutdown', 1083: 'Error run time', 1084: 'Error sample temp', 1085: 'Error set temp', 1086: 'Error temp 2', 1087: 'Error temp 3', 1088: 'Error heater 1', 1089: 'Error heater 2', 1090: 'Error heater 3', 1091: 'Error gas flow', 1092: 'Error back pressure', 1093: 'Error ADC1', 1094: 'Error ADC2', 1095: 'Error ADC3', 1096: 'Error ADC4', 1097: 'Error cryodrive speed', 1098: 'Error cryodrive state', 1100: 'FC Gas flow', 1101: 'FC Back pressure', 1102: 'FC Supply pressure', 1103: 'FC Valve opening', 1104: 'FC Firmware', 1105: 'FC Serial', 1106: 'FC Outer flow', 1107: 'FC Selected gas', 1108: 'FC Detected gas', 1109: 'FC Device type', 1110: 'FC Calibration', 1111: 'FC Outer valve', 1112: 'FC Flow set point', 1113: 'FC Outer set point', 1114: 'FC Protocol', 1115: 'FC Interrupt time', 1116: 'FC Interrupt state', 1117: 'FC Interrupt count', 1118: 'FC C1 counts', 1119: 'FC C2 counts', 1120: 'FC Flow counts', 1121: 'FC Shield counts', 1122: 'FC Back pressure counts', 1123: 'FC Flow zero', 1124: 'FC Shield zero', 1125: 'FC Back pressure zero', 1126: 'FC Gas detect zero', 1127: 'FC Flow calibration He', 1128: 'FC Flow calibration N2', 1129: 'FC Shield calibration He', 1130: 'FC Shield calibration N2', 1200: 'AF Serial', 1201: 'AF Firmware', 1202: 'AF LN counts', 1203: 'AF LN level', 1204: 'AF Calib low', 1205: 'AF Calib high', 1206: 'AF Head status', 1207: 'AF Refill level', 1208: 'AF Stop level', 1209: 'AF Mode', 1210: 'AF Solenoid status', 1211: 'AF Status', 1212: 'AF Time to fill', 1213: 'AF Calib status', 1214: 'AF Probe volts', 1215: 'AF Supply volts', 1216: 'AF Ref volts', 1217: 'AF Head temp', 1300: 'FP DHCP Config', 1301: 'FP IP Address 1', 1302: 'FP IP Address 2', 1303: 'FP Mask 1', 1304: 'FP Mask 2', 1305: 'FP Gateway 1', 1306: 'FP Gateway 2', 1307: 'FP DNS 1 1', 1308: 'FP DNS 1 2', 1309: 'FP DNS 2 1', 1310: 'FP DNS 2 2', 1311: 'FP MAC Address 1', 1312: 'FP MAC Address 2', 1313: 'FP MAC Address 3', 1314: 'FP Ethernet Firmware', 1315: 'FP Ethernet Settings', 1400: 'CD Serial', 1401: 'CD Firmware', 1402: 'CD Status', 1403: 'CD Saved state', 1404: 'CD Auto state', 1405: 'CD Fault state', 1406: 'CD State', 1407: 'CD Stepper state', 1408: 'CD High T trip', 1409: 'CD Low T trip', 1410: 'CD Temp', 1411: 'CD He return pressure', 1412: 'CD He supply pressure', 1413: 'CD Hours since service', 1414: 'CD Stepper 1 speed', 1415: 'CD Stepper 2 speed', 1416: 'CD PCSP 1', 1417: 'CD PCSP 2', 1418: 'CD Total hours', 1419: 'CD Boost speed 1', 1420: 'CD Boost time 1', 1421: 'CD Boost speed 2', 1422: 'CD Boost time 2', 1423: 'CD Steady speed 1', 1424: 'CD Steady speed 2', 1425: 'CD Boost count 1', 1426: 'CD Boost count 2', 1427: 'CD Trip time', 1428: 'CD Blowdown time', 1429: 'CD Blowdown space', 1430: 'CD Last trip', 1431: 'CD Low P warning standby', 1432: 'CD Low P warning standby run', 1433: 'CD Low P margin', 1434: 'CD Coldhead hours', 1435: 'CD Adsorber hours', 1500: 'PU Serial', 1501: 'PU Firmware', 1502: 'PU Status', 1503: 'PU Board temp', 1504: 'PU Pump temp', 1505: 'PU Set pressure', 1506: 'PU Delivery pressure', 1507: 'PU Pump speed', 1508: 'PU Pump drive', 1509: 'PU Pump current', 1510: 'PU Run mins lo', 1511: 'PU Run mins hi', 1512: 'PU Total mins lo', 1513: 'PU Total mins hi', 1514: 'PU Last alarm', 1515: 'PU Trip time', 1516: 'PU Supply voltage', 1517: 'PU Voltage band', 1518: 'PU Status', 1519: 'PU Total hours', 1600: 'FP Serial', 1601: 'FP Firmware', 1602: 'FP Screen saver time', 1603: 'FP Temp units', 1604: 'FP Favourite temp', 1605: 'FP Favourite rate', 1606: 'FP Shutdown timer', 1700: 'AP Firmware', 1701: 'AP Smart pressure', 1800: 'DAU Serial', 1801: 'DAU Firmware', 1802: 'DAU Status', 1803: 'DAU Alarm', 1804: 'DAU Frequency', 1805: 'DAU AC voltage', 1806: 'DAU DC voltage', 1807: 'DAU Current', 1808: 'DAU Temp', 1809: 'DAU Pressure', 1810: 'DAU Last alarm', 1811: 'DAU Run mins lo', 1812: 'DAU Run min hi', 1813: 'DAU Total hours', 1814: 'DAU Total mins lo', 1815: 'DAU Total mins hi', 1816: 'DAU Last run', 1817: 'DAU Days off', 1900: 'CRT Tc', 1901: 'CRT TcSet', 1902: 'CRT Status', 1903: 'CRT Stop', 6000: 'SRB Serial number', 6001: 'SRB Firmware', 6002: 'SRB Error', 6003: 'SRB Peripherals', 6004: 'SRB Supply voltage', 6005: 'SRB Supply frequency', 6006: 'SRB Voltage band', 6007: 'SRB Output voltage', 6008: 'SRB Output current', 6009: 'SRB AC output state', 6010: 'SRB DC output state', 4001: 'Manual heater 1', 4002: 'Manual heater 2', 4003: 'Manual heater 3', 4004: 'Manual flow', 4005: 'Manual shield flow', 4006: 'Manual coldhead speed', 4007: 'Manual coldhead temp', 4008: 'Manual control flags', 2000: 'Cryodrive state', 2001: 'Coldhead speed', 2002: 'Coldhead adjust', 2010: 'Coldhead temp', 2011: 'Shield temp', 2012: 'Vacuum gauge', 2013: 'Nozzle temp', 2014: 'Sample heat', 2015: 'Coldhead heat', 2016: 'Shield heat', 2017: 'Nozzle heat', 2018: 'Vacuum power', 2019: 'Average sample heat', 2020: 'Average nozzle heat', 2021: 'Autofill mode', 2022: 'Autofill fill interval', 2023: 'Autofill time to fill', 2024: 'Autofill fill delay', 2030: 'Sample holder temp', 2031: 'Cryostat temp', 2032: 'Sample holder present', 2033: 'Selected sensor', 2034: 'Phase time elapsed', 2035: 'Suct set temp', 2036: 'Nozzle set temp', 2037: 'Status 1', 2038: 'Status 2', 2039: 'Status 3', 2040: 'Status 4', 2041: 'Collar temp', 2042: 'Vacuum sensor', 2043: 'Outer flow', 2044: 'Alarm level', 2045: 'Plateau duration', 2046: 'Phase start temp', 2047: 'Phase elapsed'}

        return tempDictionary


    # Populates a Dictionary called _oxCryoProperties with All Cryostream 800 Properties
    # ID, Name
    # 1002, Min Temp
    # 1003, Max Temp
    # 1031, Total Hours
    # Programming Use:
    # _oxCryoProperties[1003] would return the string "Max Temp"
    # File also available at: https://connect.oxcryo.com/ethernetcomms/OxcryoProperties.xml
    def _parseBinaryStatusPacket(self, binaryStatusPacket):

        # Lists which stores the binary status packet retrieved from the internet
        # However we use the list format to be more acessible and able to navigate using indexes
        binaryStatusList = []

        for byte in binaryStatusPacket:
            binaryStatusList.append(byte)

        # Sanity Check - Currently at 1148 parameters
        if (len(binaryStatusList)%4) != 0:
            print("The number of elements on the status package from Cryostream 800 is")
            print("It should be a multiple of 4, if it is not, something is wrong.")
            print("Please, Please contact support.")
            sys.exit(1)

        # List that Stores tuples of data (cmdID, value)
        parsedStatusList = []

        # Iterate elements in groups of 4
        for i in range(0, len(binaryStatusList), 4):

            # Gets Current Group of 4 Elements
            group = binaryStatusList[i: (i + 4)]

            # For more details on this math, please visit
            # OxCryo Cryostream 800 Ethernet Communications Documentation
            # https://connect.oxcryo.com/ethernetcomms/status.html

            # Relative to the Command
            a = int(ord(group[0])) << 8  # Multiplies by 256
            b = int(ord(group[1])) & 0xFF

            # Relative to the Parameters
            c = int(ord(group[2])) << 8  # Multiplies by 256
            d = int(ord(group[3])) & 0xFF

            # By Definition
            # Check https://connect.oxcryo.com/ethernetcomms/status.html
            cmdId = a + b
            value = c + d

            # Temporary Tuple
            tempTuple = (cmdId, value)

            # Enable this line for EPICS debugging purposes
            #print(tempTuple, group,(a,b,c,d))

            #print(tempTuple)
            
            # append to the parsed status list
            parsedStatusList.append(tempTuple)
                    
        return parsedStatusList

    # Builds dictionary with the last status of the Cryostream 800
    def _buildLastStatus(self, lastBinaryStatusList, oxCryoProperties):

        # Empty Dictionary
        lastStatus = dict()

        # For every entry we look for the string relative to the code into oxCryoProperties
        # And for instance code 8288 temperature, 90F
        # we add lastStatus[8288] = 90 and lastStatus["Temperature"] = 90
        # This way you can can query using the code or the string

        # Iterates over the last binary status list to update the dictionary
        for item in lastBinaryStatusList:

            if  item[0] in oxCryoProperties:
                name = oxCryoProperties[item[0]]
                #print(name)
                lastStatus[name]    = item[1]
            else:
                name = ""
            
            lastStatus[item[0]] = item[1]

        # Returns the dictionary
        return lastStatus

    # Updates the last Status information in three steps
    # 1) Get Binary Packet from the Network
    # 2) Parse the binary status
    # 3) Update the dictionary on memory
    def _updateStatus(self):

        # IP is useful to verify if the broadcasted message on the subnetwork
        # It is really coming from our CS800 device and not other device.
        CS800sIP = self.getIP()
 
        # print("Retrieving Cryostream 800 Status Packet from the Network...")

        # Retrieves the binary status packet broadcasted to the subnetwork as UDP
        # Notice that the packet is still in binary format
        self._lastBinaryStatusPacket = self._getBinaryStatusPacket(CS800sIP)

        # print("Parsing Cryostream 800 binary status packet...")
        
        # Stores the parsed binary status packet in the form of list of tuples
        # list = [(11007, 97), (2515, 64), (2021, 65534),...]
        self._lastBinaryStatusList = self._parseBinaryStatusPacket(self._lastBinaryStatusPacket)

        # print("Updating last status Information on memory...")
        
        self._lastStatus = self._buildLastStatus(self._lastBinaryStatusList, self._oxCryoProperties) 

    # Deactivated while using _getCommandBookInline()
    """
    # Returns a list of Commands
    # File also available at: https://connect.oxcryo.com/ethernetcomms/Cryostream.xml
    def _getCommandBook(self, xml_file_path):

        try:

            # Parse the XML file
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            # Extract the list of commands
            listOfCommands = root.find("LIST_OF_COMMANDS")

            # Initialize a dictionary to store command information
            commandsDict = {}

            # Iterate over the commands and extract CommandID and Name
            for command in listOfCommands.findall("COMMAND"):
                commandInfo = command.attrib.get("id")
                # Use the 'Name' attribute as the key in the dictionary
                commandsDict[command.attrib.get("name")] = commandInfo

            # Used to build _getCommandBookInline()
            # print commandsDict

            return commandsDict

        except FileNotFoundError:
            print("The file does not exist." + xml_file_path)
            return None
        except ET.ParseError as e:
            print("Error parsing the XML file: " + e)
            return None
        except Exception as e:
            print("An error occurred: " + e)
            return None

    """

    # Returns a list of Commands, Used to Increase Efficiency in relation to _getCommandBook()
    # File also available at: https://connect.oxcryo.com/ethernetcomms/Cryostream.xml
    def _getCommandBookInline(self):

        commandsDict = dict()

        commandsDict = {'End': '15', 'Regen': '21', 'Turbo': '20', 'Run shield': '122', 'Resume': '18', 'Set Autofill mode': '202', 'Stop': '19', 'Plat': '12', 'Interrupt flow now': '121', 'Set parameter': '252', 'Cryopad': '7', 'Hold': '13', 'Set idle shield flow mode': '123', 'Restart': '10', 'Cool': '14', 'Close port': '3', 'Update firmware': '66', 'Ramp': '11', 'Purge': '16', 'Set Autofill stop level': '204', 'Logfile Viewer': '6', 'Set Autofill refill level': '203', 'Suspend': '17', 'Check for firmware updates': '5', 'Set flow interrupt time': '120'}

        return commandsDict

    #==========================================
    #=== Commands Generation and Submission ===
    #==========================================

    ###
    # Generates a list of 7 integers, based on 3 parameters supplied.
    # Each parameter becomes two numbers will be later converted to one by each.
    # Always representing values between 0 and 255.
    # The last parameters is the checksum parameter.
    # For more information: https://connect.oxcryo.com/ethernetcomms/commands.html

    def _getCommandsList(self, idCmd, param1, param2):

        # Calculating Command ID - Bytes 01 and 02

        idCmd_B1   = (idCmd >> 8)   #int [0-255]
        idCmd_B2   = (idCmd & 0xFF) #int [0-255]

        # Calculating Param 01 - Bytes 01 and 02

        param1_B1 = (param1 >> 8)   #int [0-255]
        param1_B2 = (param1 & 0xFF) #int [0-255]

        if param1_B1 >= 256:
            param1_B1 = abs(param1_B1 - 256)
        if param1_B2 >= 256:
            param1_B2 = abs(param1_B2 - 256)

        # Calculating Param 02 - Bytes 01 and 02

        param2_B1 = (param2 >> 8)   #int [0-255]
        param2_B2 = (param2 & 0xFF) #int [0-255]

        if param2_B1 >= 256:
            param2_B1 = abs(param2_B1 - 256)
        if param2_B2 >= 256:
            param2_B2 = abs(param2_B2 - 256)

        # Calculating CheckSum

        # Total of all first six parameters
        paramsSum = idCmd_B1 + idCmd_B2 + param1_B1 + param1_B2 + param2_B1 + param2_B2
                                          
        # Calculating CheckSum                
        checkSum = (paramsSum % 256) #int [0-255]

        # List for return of all 7 integers that will later become 7 bytes.
        intCommands = [idCmd_B1, idCmd_B2, param1_B1, param1_B2, param2_B1, param2_B2, checkSum]

        return intCommands

    # Generates 7 bytes based on a list of 7 integers
    def _binarizeCommand(self, cmdList):

        # Cryostream 800 requires 7 bytes as input to generate a binary command.
        if len(cmdList) != 7:
            print("Error in binarizeListOfCommands(): In order to create a binary command to the Cryojet 800, it is necessary to have a list of exactly 7 integers between 0 and 255, in order to generate a binary command of size 7 bytes.")
            sys.exit(1)

        # Convert the integers to binary and pack them into a single variable
        binary_data = struct.pack("7B", *cmdList)

        # For Inspection purposes only
        # Convert the binary data to a binary string
        # Python 3 Version:
        # binary_string = ''.join(format(byte, '08b') for byte in binary_data)
        # Python 2 Version: 
        binary_string = ''.join(format(ord(byte), '08b') for byte in binary_data)

        return binary_data

    # High Level Class to send a command based on cmdID, param1, and param2
    # For more information https://connect.oxcryo.com/ethernetcomms/commands.html
    def _launchCommand(self, command, p1, p2):

        command = int(command)
        p1 = int(p1)
        p2 = int(p2)

        # List of 7 Integers generated from parameters
        # print("Calculating list of 7 integers generated from parameters.")
        cmdList = self._getCommandsList(command, p1, p2)

        # Binary Command to be sent to the device
        # print("Generating Binary Command.")
        binary  = self._binarizeCommand(cmdList)

        # Open connection and sends the command
        # print("Sending Binary Command to the Cryostream 800.")
        self._submitBinaryCommand(binary)

    #===============
    #=== Network ===
    #===============

    # Function to capture status packets from Cryostream 800.
    # This device broadcasts a status packet every second on the network on port 30304.
    def _getBinaryStatusPacket(self, interestIP):

        # The maximum size of the buffer to receive the UDP packets.
        bufMax = 8192

        # The IP address to bind to. Using '0.0.0.0' to listen on all available network interfaces.
        # This allows the program to receive broadcast messages regardless of the specific local IP address of the machine.
        bindIP = '0.0.0.0'

        # The target port number where the Cryostream 800 broadcasts its status packet.
        targetPort = 30304

        # This is used to tell the socket which IP address and port to listen on.
        idBroadcast = (bindIP, targetPort)

        # Creating a UDP socket to handle the incoming UDP packets.
        # The socket is set up with the AF_INET address family (for IPv4) and the SOCK_DGRAM socket type (for UDP).
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        try:

            # Setting a socket option to enable the handling of broadcast packets.
            # This is necessary because the default behavior might be to ignore broadcast messages.
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Binding the socket to the address and port specified by idBroadcast.
            # This effectively tells the operating system that any UDP packets arriving on this port should be directed to this program.
            s.bind(idBroadcast)

            # Receiving data from the socket. This is a blocking call that waits for data to arrive.
            # 'm' contains the data of the received packet, and 'reportedAddress' contains the address of the sender.
            m, broadcasterNetworkInfo = s.recvfrom(bufMax)

            # broadcasterNetworkInfo variable should contain the IP and Port, Saving just the IP
            # Because the port we already know 30304
            broadcasterIP = broadcasterNetworkInfo[0]

            if(broadcasterIP == interestIP):
                return m
            else:
                print("The UDP packet captured from the subnetwork is coming from " + broadcasterIP + ".")
                print("You are trying to communicate with " + interestIP + ".")
                print("Please, call for help and check these things:")
                print("- Are you trying to connect to the right Cryostream 800 (" + interestIP + ")?")
                print("- Check IP settings on your Cryostream 800.")
                print("- The packet being broadcasted on the network is it coming from the expected device?")
                sys.exit(-1)

        except KeyboardInterrupt:

            # A way to exit the program gracefully if the user hits Ctrl+C (commonly used to signal program interruption).
            print("Exiting program.")

        except Exception as e:

            # Catching any other exceptions that could occur to avoid crashing and to log the error.
            #print(e)
            print("An error occurred: " + e)

        finally:

            # Ensuring that the socket is closed when we are done with it.
            # This is important to release the system resources associated with the socket.
            s.close()

    # Sends a binary command to the Cryostream 800
    def _submitBinaryCommand(self, bin):

        ip   = self.getIP()
        port = 30305

        # Creates an UDP Socket.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Required Delay - Pending Better Explanation.
        # time.sleep(3000/1000)

        s.sendto(bin, (ip, port))



    #=========================================
    #=== Kernel - Get Commands - Low Level ===
    #=========================================

    # Minimum Temperature (Return in K * 100)
    # ID #1002
    def getMinTemperature(self):
        attribute = "Min temp"
        return self._lastStatus[attribute]

    # Maximum Temperature (Return in K * 100)
    # ID #1003
    def getMaxTemperature(self):
        attribute = "Max temp"
        return self._lastStatus[attribute]        

    # Sample Temperature (Return in K * 100)
    # ID #1051
    def getSampleTemperature(self):
        attribute = "Sample temp"
        return self._lastStatus[attribute]

    # Returns which mode the Cryostream 800 is curretly running:
    # ID #1053  
    # [0] - Initializing
    # [1] - Initialization Failed
    # [2] - Ready
    # [3] - Running
    # [4] - Set up Mode
    # [5] - Shut down without error
    # [6] - Shut down with error
    def getRunMode(self):

        attribute    = "Run mode"
        runMode = self._lastStatus[attribute]

        if runMode == 0:
            message = "Initializing"
        elif runMode == 1:
            message = "Initialization Failed"
        elif runMode == 2:
            message = "Ready"
        elif runMode == 3:
            message = "Running"
        elif runMode == 4:
            message = "Set up Mode"
        elif runMode == 5:
            message = "Shut down without error"
        elif runMode == 6:
            message = "Shut down with error"
        else:
            message = "Unknown mode"

        return message

    # Target Temperature (Return in K * 100)
    # ID #1056
    def getTargetTemperature(self):
        attribute = "Target temp"
        return self._lastStatus[attribute]

    # Returns Gas flow
    # ID #1060
    def getGasFlow(self):
        attribute = "Gas flow"
        return self._lastStatus[attribute]

    # Returns "1" if Turbo Mode is Active.
    # Returns "0" if Turbo Mode is Inactive.
    # ID #1068
    def getTurboMode(self):
        attribute = "Turbo mode"
        return self._lastStatus[attribute] 

    # Returns Autofill Liquid Nitrogen (LN) level
    # ID #1203
    def getAutofillLNLevel(self):
        attribute = "AF LN level"
        return self._lastStatus[attribute]

    # Returns Autofill Mode:
    # ID #1209
    # List of Modes:
    # [0] - Manual
    # [1] - Auto
    # [2] - Scheduled
    def getAutofillMode(self):

        attribute    = "AF Mode"
        runMode = self._lastStatus[attribute]

        if runMode == 0:
            message = "Manual"
        elif runMode == 1:
            message = "Auto"
        elif runMode == 2:
            message = "Scheduled"
        else:
            message = "Unknown mode"

        return message 

    # Returns Outer flow
    # ID #2043
    def getOuterFlow(self):
        attribute = "Outer flow"
        return self._lastStatus[attribute]           



    #=====================================================
    #=== My Implementations - Get Commands - Low Level ===
    #=====================================================

    # Returns the IP of the machine set. (Cryostream 800).
    # ID #N/A
    def getIP(self):
        return self._ip

    # Returns port where status is broadcasted as UDP to all subnetwork
    # Port 30304
    def getStatusPort(self):
        return self._statusPort

    # Returns port where commands are sent as UDP to the Cryostream 800 device.
    # Port 30305
    def getCommandsPort(self):
        return self._commandsPort

    # Checks if Device is in "Ready" or "Running" State
    def _isReadyOrRunning(self):

        # Retrieving Run Mode
        runMode = self.getRunMode()

        if(runMode == "Ready"):
            return True
        if(runMode == "Running"):
            return True
        
        return False

    # Checks if Device is in "Running" State
    def _isRunning(self):

        # Retrieving Run Mode
        runMode = self.getRunMode()

        if(runMode == "Running"):
            return True
        else:
            return False

    #=========================================
    #=== Kernel - Set Commands - Low Level ===
    #=========================================

    # Restart cooler after shut down
    # Brings device to ready state
    # It does not start cooling by itself
    # Command ID: 10 (No parameters)
    def restart(self):
        code = self._commandBook["Restart"]
        self._launchCommand(code,0,0)
        time.sleep(2)

    # Hold current temperature indefinitely
    # Command ID: 13 (No parameters)
    def hold(self):
        code = self._commandBook["Hold"]
        self._launchCommand(code,0,0)

    # Change to new temperature as quickly as possible
    # Command ID: 14 (one parameter, temperature)
    def cool(self, targetTemp):
        code = self._commandBook["Cool"]
        # In order to send to the functions we must multiply the temperature by 100.
        targetTemp = targetTemp * 100
        self._launchCommand(code,targetTemp,targetTemp)

    # Ramp to 300 K at a specified rate and then shut down
    # Command ID: 15 (one parameter, rate)
    # Ramp rate between 1 to 360 K/hour.
    def end(self, rate):
        code = self._commandBook["End"]
        self._launchCommand(code,rate,rate)

    # Stop cooler immediately
    # Command ID: 19 (No parameters)
    def stop(self):
        code = self._commandBook["Stop"]
        self._launchCommand(code,0,0)       

    # Set Turbo Mode
    # Command ID: 20
    def setTurboMode(self, mode):
        code = self._commandBook["Turbo"]
        self._launchCommand(code,mode,mode)

    # Set Auto Fill Mode
    # Command ID: 202
    def setAutofillMode(self, afmode):
        code = self._commandBook["Set Autofill mode"]
        self._launchCommand(code,afmode,afmode)


    #==========================================
    #=== Kernel - Set Commands - High Level ===
    #==========================================

    #All commands in this section have confirmation
    #They are sent, status is updated and checked

    # Brings device to ready state
    # And confirms that device is in ready mode.
    # Important: It does not start cooling by itself
    # Command ID: 10 (No parameters)
    def restartWithConfirmation(self, maxRetries = 10):

        # Gets Code that represents "Restart" Mode 
        code = self._commandBook["Restart"]
        
        # Initialize Retry Count
        retries = 0

        #Loop until the desired mode is set or max retries reached
        while (retries < maxRetries):

            print("Restart: Attempt " + str(retries+1) + " out of " + str(maxRetries) + ".")

            # Sends command to bring machine to ready state (restart)
            self._launchCommand(code,0,0)

            # Waits for device to initialize and go to ready state
            time.sleep(4)

            # We update the status to check if the restart command was effective
            self._updateStatus()

            # Getting run mode information
            runMode = self.getRunMode()
            #print("runMode", runMode)
            # Command was effective
            if(runMode == "Ready"):
                return True
            # Command failed
            else:
                # New Attempt
                retries +=1

        print("It was not possible to restart device (Get back to Ready).")
        print("Something odd happened. Not your lucky day!")
        print("Please, try again!")        
        return False

    # Change to new temperature as quickly as possible
    # With network confirmation that the temperature was set
    # Command ID: 14 (one parameter, temperature)
    def coolWithConfirmation(self, targetTemp, maxRetries = 10):
        
        # Gets Code that represents "Cool" Mode        
        code = self._commandBook["Cool"]

        # Gets Temperature lower and higher device limits
        minTemp = self.getMinTemperature()/100
        maxTemp = self.getMaxTemperature()/100

        # Check if the setTemp is within the allowed interval
        if not (minTemp <= targetTemp <= maxTemp):
            print("Error: Temperature should be between [" + str(minTemp) + "," + str(maxTemp) + "]. You provided " + str(targetTemp) + ".")
            return False

        # In order to send to the functions we must multiply the temperature by 100.
        targetTemp = targetTemp * 100

        # Initialize Retry Count
        retries = 0

        #Loop until the desired mode is set or max retries reached
        while (retries < maxRetries):

            # Sends command to set target temperature
            self._launchCommand(code,targetTemp,targetTemp)

            # Waits a bit, so device status will be updated, usually every 1 second
            time.sleep(1)

            # We update the status to check if the restart command was effective
            self._updateStatus()

            # Getting run mode information
            targetTempFromDevice = self.getTargetTemperature()

            # Is Device Running (Cooling)
            running = self._isRunning()

            # Command was effective
            if(targetTempFromDevice == targetTemp and running == True):
                return True
            # Command was not effective
            else:
                retries+=1

        print("It was not possible to put device on cooling mode.")
        print("Running Mode: " + self.getRunMode())
        print("Target Temperature: " + targetTemp + " K.")
        print("Device Temperature: " + targetTempFromDevice + " K.")
        print("Something odd happened. Not your lucky day!")
        print("Please, try again!")
        return False


    # Stop cooler immediately with confirmation
    # Command ID: 19 (No parameters)
    def stopWithConfirmation(self, maxRetries = 10):

        # We could check if the device is already in stop mode
        # However it is cheaper to simply send the stop command
        code = self._commandBook["Stop"]

        # Initialize Retry Count
        retries = 0

        #Loop until the desired mode is set or max retries reached
        while (retries < maxRetries):

            print("Stop: Attempt " + str(retries+1) + " out of " + str(maxRetries) + ".")

            self._launchCommand(code,0,0)

            time.sleep(1)

            # We update the status to check if the stop command was effective
            self._updateStatus()

            # Getting run mode information
            runMode = self.getRunMode()

            # Command was effective
            if(runMode == "Shut down without error"):
                return True
            # Command failed
            else:
                #Go to next attempt
                retries +=1

        print("It was not possible to stop (Shutdown) device.")
        print("Something odd happened. Not your lucky day!")
        print("Please, try again!")
        
        return False

    # Set Turbo Mode With Confirmation
    # Command ID: 20
    def setTurboModeWithConfirmation(self, desiredMode, maxRetries = 10):

        # Gets Code that represents "Turbo" Mode
        code = self._commandBook["Turbo"]

        # Initialize Retry Count
        retries = 0

        #Loop until the desired mode is set or max retries reached
        while (retries < maxRetries):
        
            print("Turbo Mode: Attempt " + str(retries+1) + " out of " + str(maxRetries) + ".")

            # Saves Turbo Mode state before command is sent
            before = self.getTurboMode()

            # Sends command to set Turbo Mode to desired mode
            self._launchCommand(code,desiredMode,desiredMode)

            # Waits a bit, so device status will be updated.
            time.sleep(3)

            # We update the status to check if the turbo mode was set
            self._updateStatus()

            # Getting run mode information
            after = self.getTurboMode()

            # Cryostream 800 sometimes sets Turbo Mode as 2 or 3, which means Turbo Mode is On.
            # Turbo mode 2 or 3 means that is on and the device is taking control.
            if(before == 2 or before == 3):
                print("Device is in control, cant change settings!")
                return False
                #before = 1

            if(after == 2 or after == 3):
                print("Special Settings Set for Turbo Mode!")
                return False
                #after = 1

            print(before, desiredMode, after)

            # Turbo is Off, User Wants it Off, After Command is Still Off      
            if(before == 0 and desiredMode == 0 and after == 0):
                print("Turbo Mode Was Off, We Deactivated and it is still Off!")
                return True
            # Turbo is Off, User Wants it On, After Command is On   
            elif(before == 0 and desiredMode == 1 and after == 1):
                print("Turbo Mode Was Off, We Activated and now is On!")
                return True
            # Turbo is On, User Wants it Off, After Command is Off               
            elif(before == 1 and desiredMode == 0 and after == 0):
                print("Turbo Mode Was On, We Deactivated and now is Off!")
                return True
            # Turbo is On, User Wants it On, After Command is still On             
            elif(before == 1 and desiredMode == 1 and after == 1):
                print("Turbo Mode Was On, We Activated and it is Still On!")
                return True

            # Increment Retry Count
            retries +=1

        print("It was not possible to set Turbo Mode.")
        print("Something odd happened. Not your lucky day!")
        print("Please, try again!")
        
        return False

    # Set Turbo Mode With Confirmation
    # Command ID: 20
    def setAutofillModeWithConfirmation(self, desiredAutofillMode, maxRetries = 10):

        # Gets Code that represents "Turbo" Mode
        code = self._commandBook["Set Autofill mode"]

        # Initialize Retry Count
        retries = 0

        #Loop until the desired mode is set or max retries reached
        while (retries < maxRetries):
        
            print("Auto Fill Mode: Attempt " + str(retries+1) + " out of " + str(maxRetries) + ".")

            # Saves Turbo Mode state before command is sent
            before = self.getAutofillMode()

            # Sends command to set Turbo Mode to desired mode
            self._launchCommand(code,desiredAutofillMode,desiredAutofillMode)

            # Waits a bit, so device status will be updated.
            time.sleep(4)

            # We update the status to check if the turbo mode was set
            self._updateStatus()

            # Getting run mode information
            after = self.getAutofillMode()

            print(before, desiredAutofillMode, after)

            # Turbo is Off, User Wants it Off, After Command is Still Off      
            if(before == "Manual" and desiredAutofillMode == 0 and after == "Manual"):
                print("Auto Fill Mode Was Off, We Deactivated and it is still Off!")
                return True
            # Turbo is Off, User Wants it On, After Command is On   
            elif(before == "Manual" and desiredAutofillMode == 1 and after == "Auto"):
                print("Auto Fill Mode Was Off, We Activated and now is On!")
                return True
            # Turbo is On, User Wants it Off, After Command is Off               
            elif(before == "Auto" and desiredAutofillMode == 0 and after == "Manual"):
                print("Auto Fill Mode Was On, We Deactivated and now is Off!")
                return True
            # Turbo is On, User Wants it On, After Command is still On             
            elif(before == "Auto" and desiredAutofillMode == 1 and after == "Auto"):
                print("Auto Fill Mode Was On, We Activated and it is Still On!")
                return True

            # Increment Retry Count
            retries +=1

        print("It was not possible to set Auto Fill Mode.")
        print("Something odd happened. Not your lucky day!")
        print("Please, try again!")
        
        return False

    #======================================================
    #=== My Implementations - Set Commands - High Level ===
    #======================================================

    # Shutdown and Get Ready
    def shutdownAndGetReady(self):

        ready = False

        print("Attempt to Stop cooling...")
        result = self.stopWithConfirmation()
        
        if(result == False):
            print("Stop not set for some reason!")
        else:
            print("Cooling sucessfully stopped...")
            print("Cryostream 800 is not in Ready Mode!")
            print("Attempting to bring Cryostream 800 to Ready Mode!")
            ready = self.restartWithConfirmation()

        if(ready == True):
            print("Device is back in Ready Mode!")
            return True
        else:
            print("Device still in shutdown mode!")
            print("Use Restart (Get Ready) command to restore Ready state.")
            return False

    # Get Ready
    # Restores device to ready mode
    def getReady(self):

        # We assume that the device is not in ready mode
        ready = False

        # Calling function to get back to ready state with confirmation
        ready = self.restartWithConfirmation()

        # Successfull
        if(ready == True):
            print("Device is back in Ready Mode!")
            return True
        # Not Successfull
        else:
            print("Device still in shutdown mode!")
            print("Please, rerun this command.")
            return False    

    # Puts the Cryostream 800 in Ready State
    # Sets the Temperature and Cool (Go, Running)
    def getReadySetTargetTemperatureAndGo(self, temperature):

        # === Temperature Check - Float ===

        # Checks if the temperature is a float
        #print(temperature, type(temperature))
        isTemperatureFloat = self._isFloat(temperature)

        #print("isTemperatureFloat", isTemperatureFloat)

        # If input is not a float, aborts.
        if(isTemperatureFloat == True):
            #From String to Float, Same Variable
            temperature = float(temperature)
            #print(temperature, type(temperature))            
        else:
            print("Your temperature should be a float!")
            return False

        # === Temperature Check - Range ===
        
        # Checks if temperature is in range
        # Finds the Min and Max that device supports.
        minTemperature = self.getMinTemperature()
        maxTemperature = self.getMaxTemperature()
        
        # We need to multiply by 100, because the device uses dK
        # (8000, 100.1, 40000), otherwise this test would fail
        # Since 80K the device returns 8000, 400K, returns 40000
        isTemperatureInRange = self._isFloatInRange(minTemperature, temperature * 100, maxTemperature)

        # Temperature not in range
        if(isTemperatureInRange == False):
            print("Temperature not in device's range.")
            return False

        # === State Check ===

        # Checks if the machine is in "Ready" or "Running" mode
        isReadyOrRunning = self._isReadyOrRunning()

        # === Attempt to Get Device Ready ===

        # If not in "Ready" or "Running" mode, we need to put the machine back in a good state
        # before setting a temperature and sending a cool command
        if(isReadyOrRunning == False):
            print("Cryostream 800 is not in Ready or Running Mode!")
            print("Attempting to bring Cryostream 800 to Ready Mode!")
            isReadyOrRunning = self.restartWithConfirmation()

        # === If the Universe is aligned ===
        if (isReadyOrRunning == True and isTemperatureFloat == True and isTemperatureInRange == True):

                # Sending command to change target temperature on the device
                result = self.coolWithConfirmation(temperature)
                
                # Something went wrong and the temperature was not set
                if(result == False):
                    print("Temperature not set! Review your desired temperature!")
                    return False
                else:
                    print("Cooling, target temperature set to " + str(temperature) + " K.")
                    print("Confirmed by network confirmation on device status.")
                    return True

        else:
        # === If the Universe is not aligned ===
            print("It was not possible to bring Cryostream 800 to Ready Mode!")
            print("Please rerun Restart (Get Ready) command.")
            return False

    # Tentative of Emulation of Annealing Function
    # Stop, Restart (Get Ready) and Cool
    def softwareAnnealing(self, temperature = 100.0):

        # Shutdown
        stop = self.stopWithConfirmation()
        
        # We can only restart if the stop worked (True)
        if (stop == True):
            restart = self.restartWithConfirmation()
        else:
            # Stop failed
            return False

        if (restart == True):
            # Attempting to Cool
            cool = self.coolWithConfirmation(temperature)
        else:
            # Cool (Restart) failed
            return False

        return cool


    # Turbo Mode General Function
    # It has a different name, so does not get confused with setTurboMode
    def setTurboModeGeneral(self, turboMode):

        # Test if parameter is a int
        try:
            # Return True if int
            turboMode = int(turboMode)
        except ValueError:
            # Parameter is not an int
            return False

        # Check if the input is one of the valid choices
        # Already guaranteed it is an int
        if turboMode in [0, 1]:
            
            # Attempts to Set Turbo Mode On or Off
            result = self.setTurboModeWithConfirmation(turboMode)
            #print(turboMode, result)
            # User Feedback
            if(turboMode == 0 and result == True):
                print("Turbo Mode Set to Off.")
            # User Feedback
            if(turboMode == 1 and result == True):
                print("Turbo Mode Set to On.")
            # Could not set Turbo Mode
            if(result == False):
                print("Turbo Mode Not Set! Contact Support or Try Again!")
                print("Probably because: device is controlling the turbo")

            return result

        else:
            print("Invalid Turbo Mode. Please, enter [0] Set to Off, [1] Set to On.")
            return False

    # Auto Fill Mode General Function
    # It has a different name, so does not get confused with setAutofillMode
    def setAutofillModeGeneral(self, autoFillMode):

        # Test if parameter is a int
        try:
            # Return True if int
            autoFillMode = int(autoFillMode)
        except ValueError:
            # Parameter is not an int
            return False

        # Check if the input is one of the valid choices
        # Already guaranteed it is an int
        if autoFillMode in [0, 1]:
            
            # Attempts to Set Auto Fill Mode On or Off
            result = self.setAutofillModeWithConfirmation(autoFillMode)

            # User Feedback
            if(autoFillMode == 0 and result == True):
                print("Auto Fill was Set to Off.")
            # User Feedback
            if(autoFillMode == 1 and result == True):
                print("Auto Fill Mode Set to On.")
            # Could not set Turbo Mode
            if(result == False):
                print("Turbo Mode Not Set! Contact Support or Try Again!")

            return result

        else:
            print("Invalid Auto Fill Mode. Please, enter [0] Set to Off, [1] Set to On.")
            return False

    #=============================
    #=== Accessories Functions ===
    #=============================

    # Checks if an input is an int
    def _isInt(self, possibleInt):

        # Test if num is an int
        try:
            # If convertion is possible
            float(possibleInt)
            # Returns True
            return True
        except ValueError:
            # If convertion not possible
            return False

    # Checks if an input is a float
    def _isFloat(self, possibleFloat):

        # Test if num is a float
        try:
            # If convertion is possible
            float(possibleFloat)
            # Returns True
            return True
        except ValueError:
            # If convertion not possible
            return False

    # Checks if a float is in a range
    def _isFloatInRange(self, min, value, max):
        return min <= value <= max

    # Returns true if a given ip is alive - Python2 version
    def pingIP(self, ip):
        try:
            # Use the 'ping' command to check if the device is online
            process = subprocess.Popen(["ping", "-c", "1", ip], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            
            # Check the return code to determine if the ping was successful
            if process.returncode == 0:
                return True  # Device is online
            else:
                return False  # Device is not online
        except CalledProcessError:
            return False  # Ping command failed
        except Exception as e:
            print("An error occurred: {}".format(e))
            return False  # An error occurred (e.g., invalid IP address)

    #=======================
    #=== Terminal - Menu ===
    #=======================                              

    # Draws Cryostream Logo
    def terminal_drawLogo(self):

        # Clears the Terminal
        os.system('clear')

        # ASCII Art
        print("")
        print("   ______                      __")
        print("  / ____/______  ______  _____/ /_________  ____ _____ ___")
        print(" / /   / ___/ / / / __ \\/ ___/ __/ ___/ _ \\/ __ `/ __ `__ \\")
        print("/ /___/ /  / /_/ / /_/ (__  ) /_/ /  /  __/ /_/ / / / / / /")
        print("\\____/_/   \\__, /\\____/____/\\__/_/   \\___/\\__,_/_/ /_/ /_/")
        print("          /____/     by \033[1mBCSB 2023\033[0m @ ALS - Berkeley Labs.")
        print("                         Beamline 821-\033[1mCryostream 800 Ed.\033[0m")        
        print("")       

    def terminal_drawMenu(self):

        # Everytime we comeback to the dial menu, we update the status info
        self._updateStatus()

        # Checks if device is online or offline by pinging
        online = self.pingIP(self.getIP())

        # Sets Online or Offline message
        if online == True:
            onlineStatus = "Online"
        else:
            onlineStatus = "Offline"

        # Retrieves in which run mode the device is currently.
        runMode = self.getRunMode()

        # Menu Itself
        print("")
        print("Cryostream 800 (IP " + self.getIP() + ":" + str(self.getStatusPort()) + ") [\033[1m" + onlineStatus + "\033[0m]:")
        print("Run Mode (Status): [\033[1m" + runMode + "\033[0m]")
        print("\033[1m[0]\033[0m Info.")
        print("\033[1m[1]\033[0m Update Run Mode (Status).")            
        print("\033[1m[2]\033[0m Stop (Shutdown and Get Ready).")
        print("\033[1m[3]\033[0m Restart (Get Ready).")
        print("\033[1m[4]\033[0m Set Temperature and Go.")
        print("\033[1m[5]\033[0m Set Autofill Mode.")
        print("\033[1m[6]\033[0m Software Annealing.")
        print("\033[1m[7]\033[0m Set Turbo Mode [On, Off].")                                         
        print("\033[1m[8]\033[0m Exit.")

    # Gets User Input
    def terminal_getChoice(self):

        choice = raw_input("Enter your choice: ")

        # Choice Validation
        # Needs to be an integer to be able to enter the menu
        if( self._isInt(choice) == True):
            choice = int(choice)

        return choice

    # Terminal based interface for the Cryostream 800
    # It is an infinite loop showing options on the screen
    def terminal_displayMenu(self):

        # Userful for Profiling, so we do not count interface time.
        # sys.exit(0)
        
        # Draws Cryostream Logo on Menu
        self.terminal_drawLogo()

        #Loop
        while True:

            # Draws Menu
            self.terminal_drawMenu()

            # Get Users Input
            choice = self.terminal_getChoice()

            # Case 00 - Display info related to the device
            if choice == 0:

                self.terminal_displayInfo()


            # Case 01 - Updates Run Mode that appears on the opening screen
            elif choice == 1:

                # We just print a message on this choice, however since the dial menu is redraw
                # It updates the run mode information on screen
                print("Updating Run Mode")


            # Case 02 - Stop (Shutdown and Get Ready)
            elif choice == 2:

                self.terminal_shutdownAndGetReady()


            # Case 03 - Restart (Get Ready)
            elif choice == 3:

                self.terminal_getReady()


            # Case 04 - Get Ready, Set Target Temperature and Go
            elif choice == 4:

                self.terminal_getReadySetTargetTemperatureAndGo()


            # Case 05 - Set Auto Fill Mode
            elif choice == 5:

                self.terminal_setAutofillMode()


            # Case 06 - Software Annealing
            elif choice == 6:

                self.terminal_softwareAnnealing()


            # Case 07 - Set Turbo Mode [On, Off]
            elif choice == 7:

                self.terminal_setTurboModeGeneral()


            # Case 08 - Exit
            elif choice == 8:

                self.terminal_exit()


            # Case Others
            else:

                # User typed an invalid option
                print("Invalid choice. Please select a valid option [0-8].")

    #============================
    #=== Terminal - Functions ===
    #============================                         

    # Shows Cryostream 800 information on screen
    # Case 00 - Display info related to the device
    def terminal_displayInfo(self):

        # Update Status:
        # Get a new status packet from the device before showing info
        # 1) Retrieves the binary status packet from the network
        # 2) Parses the binary status packet
        # 3) Updates the last Status dictionary
        self._updateStatus()

        # Devices IP
        ip   = self.getIP()

        # Cryostream 800 Port - 10304 TCP
        port = str(self.getStatusPort())

        # Checks availability
        online = self.pingIP(ip)

        if online == True:
            onlineStatus = "(Online)"
        else:
            onlineStatus = "(Offline)"

        runMode = self.getRunMode()

        # Prepare variables into string format
        sampleTemperature = str(self.getSampleTemperature()/100.0)
        targetTemperature = str(self.getTargetTemperature()/100.0)
        minTemperature    = str(self.getMinTemperature()/100.0)
        maxTemperature    = str(self.getMaxTemperature()/100.0)
        autofillLNLevel   = str(float(self.getAutofillLNLevel()/100.0))
        autofillMode      = self.getAutofillMode()
        turboMode         = str(self.getTurboMode())

        
        if(turboMode == "1"):
            turboMode = "On"
        elif(turboMode == "0"):
            turboMode = "Off"
        else:
            turboMode = "On (Automatic)"

        # Display Information
        print("")
        print("Cryostream 800 [Status]:")
        print("Run Mode: [\033[1m" + runMode + "\033[0m]")
        print("IP: " + ip + ":" + port + " " + onlineStatus)
        print("Autofill Mode: " + autofillMode)
        print("Autofill LN Level: \033[1m" + autofillLNLevel + "%\033[0m")
        print("Sample Temperature: \033[1m" + sampleTemperature + " K" + "\033[0m")
        print("Target Temperature: \033[1m" + targetTemperature + " K" + "\033[0m")
        print("Min Temperature: " + minTemperature + " K")
        print("Max Temperature: " + maxTemperature + " K")
        print("Turbo Mode: \033[1m" + turboMode + "\033[0m")   



    # Case 01 - Updates Run Mode that appears on the opening screen
    # We just print a message on this choice, however since the dial menu is redraw
    # It updates the run mode information on screen



    # Case 02 - Stop (Shutdown and Get Ready)
    def terminal_shutdownAndGetReady(self):

        #Calls Advanved Function
        self.shutdownAndGetReady()



    # Bring the device back to "Ready" mode
    # Case 03 - Restart (Get Ready)
    def terminal_getReady(self):

        self.getReady()

    # Puts the Cryostream 800 in Ready State
    # Sets the Temperature and Cool
    # Case 04 - Get Ready, Set Target Temperature and Go
    def terminal_getReadySetTargetTemperatureAndGo(self):

        # Retrieving limits to assist the user with the range
        # Altough, we will also check inside the function
        minTemperature = self.getMinTemperature()
        maxTemperature = self.getMaxTemperature()

        # User types desired temperature
        targetTemperature = raw_input("Enter a target temperature in K between ["+str(minTemperature/100.0) + "," + str(maxTemperature/100.0) + "]: ")

        self.getReadySetTargetTemperatureAndGo(targetTemperature)



    # Sets Autofill Mode
    # Case 05 - Manual, Auto or Scheduled
    def terminal_setAutofillMode(self):

        # Prompt the user to enter the Auto Fill Mode
        print("Enter Auto Fill Mode:")
        print("[0] Set to Manual.")
        print("[1] Set to Auto.")

        # Captures user's choice
        afmode = raw_input("Enter your Auto Fill mode: ")

        self.setAutofillModeGeneral(afmode)


    # Functions that tries to emulate Annealing via Stop, Start and Cool.
    # Case 06 - Software Annealing
    def terminal_softwareAnnealing(self):

        #Stop, Get Ready and Cool
        self.softwareAnnealing()



    # Turbo Mode General Function
    # Case 07 - Set Turbo Mode [On, Off]
    def terminal_setTurboModeGeneral(self):

        # Prompt the user to enter the Auto Fill Mode
        print("Enter Turbo Mode:")
        print("[0] Set to Off.")
        print("[1] Set to On.")

        # Captures user's choice
        turboMode = raw_input("Enter your turbo mode choice: ")

        self.setTurboModeGeneral(turboMode)



    # Case 08 - Exit
    def terminal_exit(self):

        # Exits gracefully with zero code
        sys.exit(0)



  