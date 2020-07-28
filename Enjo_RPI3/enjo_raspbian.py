import os
import json
import socket
import http.client, urllib.parse
import re, uuid
import ssl
import subprocess

def init():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

# Variable
statusLed = ""
mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

# Return SSID Connected
def getSSID():
    output = subprocess.check_output("iwgetid -r", shell = True)
    ssid = str(output, encoding = 'utf-8')
    print("Connected Wifi SSID: " + ssid)
    return ssid

# Return Serial Number of Hardware
def getserial():
  # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"
    return cpuserial

# Return CPU temperature as a character string
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

# Return RAM information (unit=kb) in a list
# Index 0: total RAM
# Index 1: used RAM
# Index 2: free RAM
def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

# Return % of CPU used by user as a character string
def getCPUuse():
    return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
)))

# Return information about disk space as a list (unit included)
# Index 0: total disk space
# Index 1: used disk space
# Index 2: remaining disk space
# Index 3: percentage of disk used
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])

def getApiKeyControl(name, password, typeHub, token):
    # Params in POST Request
    params = urllib.parse.urlencode({"MAC": mac, "name": name, "password": password, "type": typeHub, "token": token})
    # Headers in POST Request
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    # Make a HTTP Connection
    conn = http.client.HTTPSConnection('enjo-iot.xyz', 443)
    # Send data to server
    conn.request('POST', '/add/control', params, headers)
    # Get response from server
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    res = data.decode('utf8').replace("'", '"')
    # Parse to JSON Object
    dataJson = json.loads(res)
    # Get API Key Control
    apiKeyControl = dataJson['hubID']
    print("API Key Control: ", apiKeyControl)
    # Close connection
    conn.close()
    # Return API Key Control
    return apiKeyControl

def addDeviceForHub(key, d):
    # Params in POST Request
    params = urllib.parse.urlencode(d)
    # Headers in POST Request
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    # Make a HTTP Connection
    conn = http.client.HTTPSConnection('enjo-iot.xyz', 443)
    # Send data to server
    conn.request('POST', '/hub/add/device/' + key, params, headers)
    # Get response from server
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    res = data.decode('utf8').replace("'", '"')
    # Parse to JSON Object
    dataJson = json.loads(res)
    # Get API Key Log
    deviceID = dataJson['deviceID']
    print("deviceID: ", deviceID)
    conn.close()
    return deviceID

def updateFieldToServer(key, deviceID, d):
    # Params in POST Request
    params = urllib.parse.urlencode(d)
    # Headers in POST Request
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    # Make a HTTP Connection
    conn = http.client.HTTPSConnection('enjo-iot.xyz', 443)
    # Send data to server
    conn.request('POST', '/update/control/' + key + '/' + deviceID, params, headers)
    # Get response from server
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    res = data.decode('utf8').replace("'", '"')
    # Parse to JSON Object
    dataJson = json.loads(res)
    # Get API Key Log
    message = dataJson['message']
    print("message: ", message)
    conn.close()

def getControlToHTTPServer(key, deviceID, field):
    # Headers in GET Request
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    # Make a HTTP Connection
    conn = http.client.HTTPSConnection('enjo-iot.xyz', 443)
    # Send data to server
    conn.request('GET', '/get/control/' + key + "/" + deviceID + "/" + field, headers)
    # Get response from server
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    res = data.decode('utf8').replace("'", '"')
    # Parse to JSON Object
    dataJson = json.loads(res)
    # Get API Key Log
    value = dataJson[field]
    print(field + ": " + value)
    conn.close()

def postLogDataToHTTPServer(key, name):
    # Params in POST Request
    RAM_stats = getRAMinfo()
    print("POST Key: ", key)
    tmp = {
        "deviceId": getserial(),
        "name": name,
        "ipAddress": IPAddr,
        "MAC": mac,
        "ssidConnected": getSSID(),
        "deviceCpuUsed": getCPUuse(),
        "deviceDiskSpace": getDiskSpace(),
        "deviceTemp": getCPUtemperature(),
        "deviceRAMInfo": round(int(RAM_stats[2]) / 1000, 1)
    }
    print(tmp)
    params = urllib.parse.urlencode(tmp)
    # Headers in POST Request
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    # Make a HTTP Connection
    conn = http.client.HTTPSConnection('enjo-iot.xyz', 443)
    # Send data to server
    print("URL POST: ",'/update/log/' + key)
    conn.request('POST', '/update/log/' + key, params, headers)
    # Get response from server
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    res = data.decode('utf8').replace("'", '"')
    # Get API Key Log
    print(res)
    conn.close()
