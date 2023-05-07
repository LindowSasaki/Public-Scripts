#!/usr/bin/python

# One time run script to check and harden a linux machine

import subprocess
import os
from colorama import Fore,init
import re
import fileinput



# Reset color each time so I don't have to manually type reset after each string
init(autoreset=True)

def hardening_script():
    sudo_permissions = True

    if subprocess.check_output(['whoami']) == "root":
        print(Fore.CYAN + "Script is executing as root, be careful")
    else:
        print(Fore.CYAN + "Script is not executing as root, or with sudo permissions.")

    if "(ALL : ALL) ALL" in str(subprocess.check_output(["sudo", "-l"])):
        print(Fore.CYAN + "Current account has sudo permissions, moving on")
    else:
        print(Fore.RED + "Current account does not have sudo permissions, script will not be able to make changes to certain files")
        sudo_permissions = False



    # Print the chmod output of shadow and passwd files to check permissions, shadow should be 640 and passwd should be 644
    # It is more important that the shadow file cannot be read by anyone on the system, otherwise everyones password hashes would be viewable
    if oct(os.stat("/etc/shadow").st_mode)[-3:] != "640":
        print(Fore.YELLOW + "Shadow file has interesting permissions:")
        oct(os.stat("/etc/shadow").st_mode)[-3:]
    else:
        print(Fore.GREEN + "Shadow file has expected permissions of chmod 640")

    if oct(os.stat("/etc/passwd").st_mode)[-3:] != "644":
        print(Fore.YELLOW + "Passwd file has interesting permissions:")
        oct(os.stat("/etc/passwd").st_mode)[-3:]
    else:
        print(Fore.GREEN + "Passwd file has expected permissions of chmod 644")

    if oct(os.stat("/etc/group").st_mode)[-3:] != "644":
        print(Fore.YELLOW + "Groups file has interesting permissions:")
        oct(os.stat("/etc/group").st_mode)[-3:]
    else:
        print(Fore.GREEN + "Groups file has expected permissions of chmod 644")



    # Check sudo version, taking advantage of substring here to check versioning, if changed to 13:20, can mistake 1.9.11p for 1.9.1rc1 or other vulnerable version
    sudo_version = str(subprocess.check_output(['sudo', '-V'], universal_newlines=True))
    sudo_version = sudo_version[13:19].split(".")
    if sudo_version[1] == "8":
        print(Fore.YELLOW + "Legacy sudo version detected, it is highly recommended to update distro")
        if sudo_version[2] != "32":
            print(Fore.RED + "Legacy version is not to most updated version 1.8.32 and is vulnerable to Baron Samedit")
    elif "b" in sudo_version[2] or "p" in sudo_version[2] or "r" in sudo_version[2]:
        if int(sudo_version[2][1]) <= 5:
            print(Fore.RED + f"Sudo version 1.9.{sudo_version[2][1]} is a vulnerable version, consider updating to patch vulnerability Baron Samedit")
    elif int(sudo_version[2]) <= 5:
        print(Fore.RED + f"Sudo version 1.9.{sudo_version[2]} is a vulnerable version, consider updating to patch vulnerability Baron Samedit")
    else:
        print(Fore.GREEN + f"Current sudo version does not have any known vulnerabilities")



    # Check the kernel version and if it is vulnerable to Dirty Pipe/Cow or just old 
    uname = subprocess.run(['uname', '-r'],check=True, capture_output=True)
    kernel_version = subprocess.run(['awk', '-F-', '{print $1}'], input=uname.stdout, capture_output=True).stdout.decode('utf-8').strip()
    kernel_split = kernel_version.split(".")
    if kernel_split[0] == "5":
        if kernel_split[1] == "10" and kernel_split[2] < "102":
            print(Fore.RED + f"Kernel version {kernel_version} is vulnerable to Dirty Pipe Exploit")
        elif kernel_split[1] == "15" and kernel_split[2] < "25":
            print(Fore.RED + f"Kernel version {kernel_version} is vulnerable to Dirty Pipe Exploit")
        elif kernel_split[1] == "16" and kernel_split[2] < "11":
            print(Fore.RED + f"Kernel version {kernel_version} is vulnerable to Dirty Pipe Exploit")
        else: 
            print(Fore.YELLOW + f"Current Kernel Version {kernel_version} is not vulnerable to Dirty Pipe, but consider upgrading to kernel 6 or later")
    elif kernel_split[0] == "4" or kernel_split == "3":
        print(Fore.RED + f"Linux Kernel version {kernel_version} is significantly out of date, and is probably vulnerable to Dirty Cow vulnerability")
    elif kernel_split[0] == "6":
        print(Fore.GREEN + f"Linux Kernel version {kernel_version} is more or less up to date and not vulnerable")
    else:
        print(Fore.RED + f"If you are seeing this, what the hell kernel version is this: {kernel_version}")



    # SSH changes to /etc/ssh/sshd_config file
    if os.path.exists("/etc/ssh/sshd_config"):
        print(Fore.GREEN + "SSH config file found, attempting to make changes now")
        with open("/etc/ssh/sshd_config", "r") as file:
            filedata = file.read()
        
            filedata = filedata.replace("#Port 22", "Port 22222")
            filedata = filedata.replace("#SyslogFacility AUTH", "SyslogFacility AUTH")
            filedata = filedata.replace("#LogLevel INFO", "LogLevel INFO")
            filedata = filedata.replace("#LoginGraceTime 2m", "LoginGracetime 1m")
            filedata = filedata.replace("#PermitRootLogin prohibit-password", "PermitRootLogin no")
            filedata = filedata.replace("#StrictModes yes", "StrictModes yes")
            filedata = filedata.replace("#MaxAuthTries 6", "MaxAuthTires 3")
            filedata = filedata.replace("#MaxSessions 10", "MaxSessions 3")

        with open("/etc/ssh/sshd_config", "w") as file:
            file.write(filedata)
            print(Fore.GREEN + "Successfully made changes to SSH file, now restarting SSH service")
            os.system("sudo service ssh restart")
            # Check netstat to see if successful



    # Install fail2ban
    if os.path.exists("/etc/fail2ban/jail.conf"):
        print(Fore.GREEN + "Fail2ban is already installed on the system")
    else:
        print(Fore.CYAN + "Attempting to install Fail2ban on the system")
        os.system("sudo apt-get install fail2ban -y")
        if os.path.exists("/etc/fail2ban/jail.conf"):
            print(Fore.GREEN + "Successfully installed Fail2ban")
        else:
            print(Fore.RED + "Could not install Fail2ban on the system, maybe try yum install fail2ban?")



    # Take an MD5sum of the filesystem
    if os.path.exists("/usr/bin/hashdeep"):
        try:
            print(Fore.CYAN + "Hashdeep already installed on computer, computing hashes now")
            os.system("hashdeep -r -c md5 / > md5hashes.txt")
            print(Fore.GREEN + "Successfully computed hashes for file system")
        except: 
            print(Fore.RED + "Ran into an exception while hashing file system")
    else: 
        print(Fore.CYAN + "Hashdeep not detected on machine, attempting to install now")
        try:
            os.system("sudo apt install hashdeep")
            print(Fore.GREEN + "Successfully installed hashdeep, proceeding to hash file system")
        except:
            print(Fore.RED + "Could not install hashdeep")


    # SELinux 
    selinux_installed = False
    if "install ok" not in str(subprocess.check_output(['dpkg', '-s', 'policycoreutils'])):
        print(Fore.CYAN + "SELinux is not installed, attempting to install now.")
        os.system("sudo apt install policycoreutils -y")
        if "install ok" not in str(subprocess.check_output(['dpkg', '-s', 'policycoreutils'])):
            print(Fore.RED + "Could not successfully install SELinux automatically, please try manually")
        else: 
            print(Fore.GREEN + "Successfully installed SELinux, proceeding to check config/status")
            selinux_installed = True
    else:
        print(Fore.GREEN + "SELinux is already installed, checking config/status")
        selinux_installed = True
        
    if selinux_installed:
        if "Disabled" in str(subprocess.check_output(['getenforce'])):
            print(Fore.YELLOW + "SELinux is not set to enforced, attempting to enforce now.")
            if os.path.exists("/etc/selinux/config"):
                print(Fore.GREEN + "SELinux config file found, attempting to make changes now")
                with open("/etc/selinux/config", "r") as file:
                    filedata = file.read()
                    if "SELINUX=disabled" in filedata:
                        filedata = filedata.replace("SELINUX=disabled", "SELINUX=enforcing")
                    elif "SELINUX=permissive" in filedata:
                        filedata = filedata.replace("SELINUX=permissive", "SELINUX=enforcing")
                    else: 
                        print(Fore.CYAN + "Config is already set to enforcing, restart the machine then check again.")
        else:
            print(Fore.GREEN + "SELinux is already enforced, moving on.")



    # Detect presense of particular commands inside of history file
    detected_history = False
    for user in os.listdir("/home/"):
        with open(f"/home/{user}/.bash_history", "r") as file:
            filedata = file.read()
            if "passwd" in filedata:
                print(f"{Fore.YELLOW}Detectd password change in {user}'s history file")
                detected_history = True
            if "wget" in filedata:
                print(f"{Fore.YELLOW}Detected a wget command in {user}'s history file")
                detected_history = True
    if detected_history == False:
        print(f"{Fore.GREEN}No suspicious commands found inside {user}'s history file(s)")

    # This upgrades the system if ran with enough permissions and distro upgrade needed
    #if distro_upgrade_required == True and sudo_permissions == True:
    #    print(Fore.CYAN + "Due to sudo being outdated, attempting distro upgrade")
    #    os.system("sudo apt-get update -y && sudo apt-get upgrade -y")
    #else: 
    #    print(Fore.RED + "Could not update the system at this time, please try sudo apt-get update and sudo apt-get upgrade manually")



    # Turn on firewall, firewall logging, and basic rule for ssh over 22222
    ufwenabled = False
    if "inactive" in str(subprocess.check_output(['ufw', 'status'])):
        print(f"{Fore.YELLOW}UFW is inactive, enabling now")
        os.system("ufw enable")
        if "active" in str(subprocess.check_output(['ufw', 'status'])):
            print(f"{Fore.GREEN}Successfully enabled UFW")
            ufwenabled = True
        else: 
            print(f"{Fore.YELLOW}Could not automatically enable UFW")
    else:
        print(f"{Fore.CYAN}UFW already enabled")
        ufwenabled = True
    
    # Required to have rsyslog be active before enabling UFW logs
    if "active (running)" in str(subprocess.check_output(['service', 'rsyslog', 'status'])):
        print(Fore.CYAN + "ryslog service is active and running, moving on to enable UFW logging")
    else:
        print(Fore.YELLOW + "rsyslog service is not running, attempting to start now")
        os.system("service rsyslog start")
        if "active (running)" in str(subprocess.check_output(['service', 'rsyslog', 'status'])):
            print(f"{Fore.GREEN}Successfully start rsyslog, moving onto UFW logging")
        else: 
            print(f"{Fore.YELLOW}Could not start rsyslog service automatically, UFW logging cannot be enabled")

    # UFW logs can be found at /var/log/ufw* and stored as gz files
    if "Logging: off" in str(subprocess.check_output(['ufw', 'status', 'verbose'])):
        print(f"{Fore.YELLOW}UFW is logging is off, enabling now")
        os.system("ufw logging medium")
        if "Logging: on" in str(subprocess.check_output(['ufw', 'status', 'verbose'])):
            print(f"{Fore.GREEN}Successfully enabled UFW logging")
        else: 
            print(f"{Fore.YELLOW}Could not automatically enable UFW logging")
    else: 
        print(f"{Fore.CYAN}UFW logging is already enabled")
    
    if ufwenabled:
        print(Fore.CYAN + "Enabling port 22222 (SSH alternate) through UFW")
        os.system("ufw allow 22222")

    #App Armor
    apparmor_installed = False
    if os.path.exists("/etc/apparmor.d/"):
        print(Fore.GREEN + "App Armor is already installed on the system")
        apparmor_installed = True
    else:
        print(Fore.CYAN + "Attempting to install App Armor on the system")
        os.system("sudo apt install apparmor-profiles -y")
        if os.path.exists("/etc/apparmor.d/"):
            print(Fore.GREEN + "Successfully installed App Armor")
            apparmor_installed = True
        else:
            print(Fore.RED + "Could not install App Armor on the system")

    if apparmor_installed:
        if "Active: active" not in str(subprocess.check_output(['systemctl', 'status', 'apparmor'])):
            print(Fore.YELLOW + "App Armor is not active, attempting to activate now")
            os.system("systemctl start apparmor")
            if "Active: active" not in str(subprocess.check_output(['systemctl', 'status', 'apparmor'])):
                print(Fore.RED + "Could not Active App Armor")
            else:
                print(Fore.GREEN + "Successfully activated App Armor")
        else:
            print(Fore.GREEN + "App Armor is Active on the system, profiles will have to be manually checked ")
        
if __name__ == "__main__":
    hardening_script()