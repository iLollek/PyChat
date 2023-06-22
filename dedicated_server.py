import socket
import os
import sys
import threading
from datetime import datetime
import requests

print(f'Starting Dedicated Server (Auth Required), this may take a while...\n')

addresses = {}
config = {}
s = socket.socket()
SEPERATOR = "<sep>"

if getattr(sys, 'frozen', False):
   program_directory = os.path.dirname(os.path.abspath(sys.executable))
else:
   program_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(program_directory)

def timestamp():
   now = datetime.now()
   timestamp = now.strftime("%H:%M:%S")
   return timestamp

def get_public_ip():
    response = requests.get("https://xcloud.ddns.net/rg")
    if response.status_code == 200:
        data = response.content
        data = data.decode()
        return data
    else:
        print("Error: Unable to retrieve public IP.")

# CHECK IF LOG FILE EXISTS; IF NOT, CREATE ONE!
if not os.path.isfile(os.path.join(program_directory, "log.txt")):
    content = f"[{timestamp()}] Created log.txt File!"
    
    with open(os.path.join(program_directory, "log.txt"), "w") as file:
        file.write(content)
else:
    pass

def log(logstring):
    global config
    if config["Log"] == "True":
        f = open(f'log.txt', 'a')
        f.write(f'[{timestamp()}] {logstring}')
        f.close()
    else:
        pass


# CHECK IF SERVERSETTINGS FILE EXISTS; IF NOT, CREATE ONE!
if not os.path.isfile(os.path.join(program_directory, "serversettings.txt")):
    content = """Name: Your SocketIO-Chatroom Name
Max_Clients: 12
Description: Your Server Description
Public: False
Log: True"""
    
    with open(os.path.join(program_directory, "serversettings.txt"), "w") as file:
        file.write(content)
        print(f"File 'serversettings.txt' created successfully!\n")
else:
    print(f"File 'serversettings.txt' already exists in the directory.\n")

with open("serversettings.txt") as f:
    for line in f:
       (key, val) = line.split(" : ")
       key = key.strip()
       val = val.strip()
       config[(key)] = val

print(f'Server Configuration:')
for key in config.keys():
    print(f'{key}: {config[key]}')

if config["Public"] == "True":
    print(f'\nSending Public Server Discovery Request to Authserver...')
    s.connect(("xcloud.ddns.net", 33399))
    connection_init = s.recv(256)
    s.send(f'SERVERDISCOVERYADD{SEPERATOR}{get_public_ip()}{SEPERATOR}{config["Name"]}{SEPERATOR}{config["Description"]}{SEPERATOR}{config["Max_Clients"]}'.encode())
    s.close()
    s = socket.socket()
    s.connect(("xcloud.ddns.net", 33399))
    connection_init = s.recv(256)
    s.send(f'SERVERDISCOVERYCHECKIFEXISTING{SEPERATOR}{get_public_ip()}'.encode())
    response = s.recv(256)
    response = response.decode()
    if response == "True":
        print(f'Server Discovery Successful!')
        log(f'Server Discovery Successful!')
    else:
        print(f'Server Discovery Failed - Did you forget to open Port 33399?')
        log(f'Server Discovery Failed - Did you forget to open Port 33399?')



















s = socket.socket()
s.bind(("192.168.178.79", 33398))
s.listen(1)
while True:
    conn,addr = s.accept()
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("[",current_time,"] %s:%s has connected." % addr)
    ip = "%s:%s"
    addresses[conn] = addr
    threading.Thread(target = handle_client, args = (conn,)).start()