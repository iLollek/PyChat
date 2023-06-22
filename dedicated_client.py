from tkinter import Tk, Label, Entry, Button, messagebox
from functools import partial
import os
import sys
import socket
import requests
import hashlib
import re

if getattr(sys, 'frozen', False):
   program_directory = os.path.dirname(os.path.abspath(sys.executable))
else:
   program_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(program_directory)

AUTH_SERVER = "xcloud.ddns.net"
AUTH_SERVER_PORT = 33399
DEDICATED_SERVER_PORT = 33398
SEPERATOR = "<sep>"

def check_first_run():
    if os.path.isfile("SystemData/lastuser.txt"):
        # File exists, indicating it's not the first run
        return False
    else:
        # File doesn't exist, indicating it's the first run
        return True

def validate_username(username):
    # Define the regular expression pattern for allowed characters
    pattern = r'^[A-Za-z0-9]{1,16}$'

    # Check if the username matches the pattern
    if re.match(pattern, username):
        return True  # Valid username
    else:
        return False  # Invalid username

def hash_password(password):
    # Encode the password string as UTF-8
    password_bytes = password.encode('utf-8')

    # Hash the password using SHA-256 algorithm
    hashed_bytes = hashlib.sha256(password_bytes).digest()

    # Convert the hashed bytes to a hexadecimal string
    hashed_password = hashed_bytes.hex()

    return hashed_password

def create_systemfiles():
    os.makedirs("SystemData")
    f = open(f'SystemData\\lastuser.txt', "w")
    f.close()
    f = open(f'SystemData\\session.token', "w")
    f.close()

def get_public_ip():
    response = requests.get("https://xcloud.ddns.net/rg")
    if response.status_code == 200:
        data = response.content
        data = data.decode()
        return data
    else:
        print("Error: Unable to retrieve public IP.")

def show_message_box(title, body):
    # Create a Tkinter window (optional if you already have a Tkinter window created)
    window = Tk()
    window.withdraw()  # Hide the window to only show the message box

    # Show the message box with the given title and body
    messagebox.showinfo(title, body)

    # Destroy the Tkinter window (optional if you already have a Tkinter window created)
    window.destroy()

def validateLogin(username, password):
    if check_first_run() == True:
        s = socket.socket()
        # Get the entered username and password
        username_value = username.get()
        password_value = password.get()
        if validate_username(username_value) == False:
            show_message_box("Invalid Username Provided!", "Usernames are only allowed to Contain Characters Ranging from A-Z & 0-9 and are allowed to have a Maximum Length of 16 Characters. Please try again.")
            sys.exit()
        print("Username:", username_value)
        print("Password:", password_value)
        print("Password (Hashed):", hash_password(password_value))
        s.connect((AUTH_SERVER, AUTH_SERVER_PORT))
        s.recv(256)
        s.send(f'SERVERREGISTERACCOUNT{SEPERATOR}{username_value}{SEPERATOR}{hash_password(password_value)}'.encode())
        reply = s.recv(256)
        reply = reply.decode()
        if reply == "SUCCESS":
            show_message_box("PyChat Account Registering Success!", f'Your Account with the Name "{username_value}" has been successfully Registered!')
            create_systemfiles()
            sys.exit()
        else:
            show_message_box("PyChat Account Registering Failed!", f'"{username_value}" is already taken.')
            sys.exit()
    else:
        s = socket.socket()
        # Get the entered username and password
        username_value = username.get()
        password_value = password.get()


        print("Username:", username_value)
        print("Password:", password_value)
        print("Password (Hashed):", hash_password(password_value))

        # Clear the username and password entry boxes
        username.delete(0, 'end')
        password.delete(0, 'end')

        s.connect((AUTH_SERVER, AUTH_SERVER_PORT))
        s.recv(256)
        s.send(f'SERVERCHECKLOGIN{SEPERATOR}{username_value}{SEPERATOR}{hash_password(password_value)}{SEPERATOR}{get_public_ip()}'.encode())
        token = s.recv(1024)
        token = token.decode()
        if token == "ERRLOGINFAIL":
            show_message_box("Login Failed!", "Wrong Username & Password Combo Provided.")
            login_success = False
        else:
            login_success = True
            f = open(f'SystemData\\session.token', "w")
            f.write(token)
            f.close()
        s.send(f'OK'.encode())
        last_login_ip = s.recv(256)
        last_login_ip = last_login_ip.decode()
        print(f'Last Login from {last_login_ip}')
        s.close()
        if login_success == True:
            show_message_box("Login Successful!", f"Session Token Received, Starting Main Program.\nLast Login attempt from: {last_login_ip}")
            f = open("SystemData\\lastuser.txt", "w")
            f.write(username_value)
            f.close()
            tkWindow.destroy()


def login_window():
    global loginButton
    global tkWindow
    global validateLogin
    # Create a tkinter window
    tkWindow = Tk()  
    tkWindow.geometry('206x75')  
    tkWindow.title('PyChat')

    # Read the last logged-in user from "lastuser.txt"
    try:
        with open("SystemData\\lastuser.txt", "r") as file:
            last_user = file.read().strip()
    except FileNotFoundError:
        last_user = ""

    # Username label and text entry box
    usernameLabel = Label(tkWindow, text="Username")
    usernameLabel.grid(row=0, column=0)
    username = Entry(tkWindow)
    username.grid(row=0, column=1)
    username.insert(0, last_user)  # Populate the username entry box with the last logged-in user (if available)

    # Password label and password entry box
    passwordLabel = Label(tkWindow, text="Password")
    passwordLabel.grid(row=1, column=0)
    password = Entry(tkWindow, show='*')
    password.grid(row=1, column=1)

    validateLogin = partial(validateLogin, username, password)

    # Login button
    if check_first_run() == True:
        loginButton = Button(tkWindow, text="Register", command=validateLogin)
        loginButton.grid(row=4, column=0)
    else:
        loginButton = Button(tkWindow, text="Login", command=validateLogin)
        loginButton.grid(row=4, column=0)

    # Run the tkinter event loop
    tkWindow.mainloop()

if check_first_run() == True:
    show_message_box("Register a PyChat Account", "Thank you for Downloading PyChat! Please Register a PyChat Account. Usernames only allow Characters from A-Z and 0-9.")
    login_window()
else:
    login_window()