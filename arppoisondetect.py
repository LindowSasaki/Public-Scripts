from scapy.all import Ether, ARP, srp, sniff, conf
from colorama import init, Fore

init()

GREEN = Fore.GREEN
RED = Fore.RED
BLUE = Fore.BLUE
MAGENTA = Fore.MAGENTA
RESET = Fore.RESET

def get_mac(ip):
    # Returns the MAC address of an "IP"
    p = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip)
    result = srp(p, timeout=3, verbose=False)[0]
    return result[0][1].hwsrc

def process(packet):
    # Check if ARP packet
    if packet.haslayer(ARP):
        # Reply
        if packet[ARP].op == 2:
            try:
                # Get the real MAC address of the sender
                real_mac = get_mac(packet[ARP].psrc)

                # Get the MAC from the packet sent back
                response_mac = packet[ARP].hwsrc

                # If different print under ARP poisoning attack
                if real_mac != response_mac:
                    print(f'{RED}[!] ARP Poisoning detected, Real MAC: {real_mac.upper()}, Fake MAC: {response_mac.upper()}{RESET}')
            except IndexError:
                # This happens due to either particular firewall rules or for other reason the real MAC cannot be found
                pass

if __name__ == "__main__":
    import sys
    try:
        iface = sys.argv[1]
    except IndexError:
        iface = conf.iface
    sniff(store=False, prn=process, iface=iface)