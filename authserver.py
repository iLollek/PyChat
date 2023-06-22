import os
import sys
import socket
import random
import threading
from datetime import datetime
import string
import re

users = {}
keys = {}

if getattr(sys, 'frozen', False):
   program_directory = os.path.dirname(os.path.abspath(sys.executable))
else:
   program_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(program_directory)

def timestamp():
   now = datetime.now()
   timestamp = now.strftime("%H:%M:%S")
   return timestamp

def generate_random_string(length):
    # Generate a random string of specified length
    letters_and_digits =  string.digits + string.ascii_letters
    random_string = ''.join(random.choices(letters_and_digits, k=length))
    return random_string

def index_users():
    with open("users.txt") as f:
        for line in f:
            (key, val) = line.split(" : ")
            key = key.strip()
            val = val.strip()
            users[(key)] = val
index_users()

def index_keys():
    with open("keys.txt") as f:
        for line in f:
            (key, val) = line.split(" : ")
            key = key.strip()
            val = val.strip()
            keys[(key)] = val
index_keys()

def write_keys():
    f = open(f'keys.txt', "a")
    for item in keys.keys():
        f.write(f'{item} : {keys[item]}\n')


def write_users():
    f = open(f'users.txt', "a")
    for item in users.keys():
        f.write(f'{item} : {users[item]}\n')


SEPERATOR = "<sep>"
servers = {}
addresses = {}
session_tokens = {}
last_logins = {}
s = socket.socket()

def add_server_to_discovery(ip, name, description, max_users):
    print(f"[{timestamp()}] {ip} wants to add themselves to the Discovery List (Public). Testing Eligibility...")

    # Check if port 33399 is open on the given IP address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)  # Set a timeout value for the connection attempt

    try:
        result = sock.connect_ex((ip, 33399))
        if result == 0:
            print(f"[{timestamp()}] {ip} is eligible. Adding to the Discovery List...")
            # Add the server to the Discovery List or perform other actions
            print(f"[{timestamp()}] Server details - IP: {ip}, Name: {name}, Description: {description}, Max Users: {max_users}")
            servers[ip] = {"name" : name, "description" : description, "max_users" : max_users}
        else:
            print(f"[{timestamp()}] {ip} is not eligible. Port 33399 is not open.")
    except socket.error as e:
        print(f"[{timestamp()}] Error occurred while checking port 33399: {str(e)}")
    finally:
        sock.close()

def check_if_server_in_discovery_list(ip):
    if str(ip) in servers.keys():
        return "True"
    else:
        return "False"

def validate_login(username, password, ip):
    login_success = False
    try:
        if users[username] == password:
            session_token = generate_random_string(32)
            conn.send(f'{session_token}'.encode())
            session_tokens[username] = session_token
            login_success = True
        else:
            conn.send(f'ERRLOGINFAIL'.encode())
    except KeyError:
        conn.send(f'ERRLOGINFAIL'.encode())
    sync = conn.recv(32)
    if login_success == True:
        try:
            last_login_ip = last_logins[username]
            conn.send(f'{last_login_ip}'.encode())
        except KeyError:
            conn.send(f'NOLASTLOGINIPAVAILABLE'.encode())
    else:
        conn.send(f'NOLASTLOGINIPAVAILABLE'.encode())
    last_logins[username] = ip

def check_if_username_exists(username):
    index_users()
    if username in users.keys():
        return True
    else:
        return False

def handle_client(conn):
    conn.send(f"Welcome to PyChat! If you're an Autoscanner reading this, feel free to Check it out on GitHub!".encode())
    request = conn.recv(1024).decode()
    parsed_request = request.split(SEPERATOR)

    command = parsed_request[0]

    if command == "SERVERDISCOVERYADD":
       ip = parsed_request[1]
       name = parsed_request[2]
       description = parsed_request[3]
       max_users = parsed_request[4]
       add_server_to_discovery(ip, name, description, max_users)
    elif command == "SERVERDISCOVERYCHECKIFEXISTING":
        ip = parsed_request[1]
        conn.send(check_if_server_in_discovery_list(ip).encode())
    elif command == "SERVERCHECKLOGIN":
        username = parsed_request[1]
        password = parsed_request[2]
        ip = parsed_request[3]
        validate_login(username, password, ip)
    elif command == "SERVERREGISTERACCOUNT":
        username = parsed_request[1]
        password = parsed_request[2]
        if check_if_username_exists(username) == True:
            conn.send(f'ERRUSEREXISTS'.encode())
        else:
            users[username] = password
            write_users()
            index_users()
            print(f'Registered Account {username} with Password {password}')
            conn.send(f'SUCCESS'.encode())
            


    conn.close()  # Close the connection after processing the request















s.bind(("192.168.178.79", 33399))
s.listen(10)
while True:
    conn,addr = s.accept()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("[",current_time,"] %s:%s has connected." % addr)
    ip = "%s:%s"
    addresses[conn] = addr
    threading.Thread(target = handle_client, args = (conn,)).start()