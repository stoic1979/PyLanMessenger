import socket

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def get_ip_prefix(ip):
    l = ip.split(".")
    return "%s.%s.%s" % (l[0], l[1], l[2])


if __name__ == "__main__":
    ip = "192.168.1.9"
    print get_ip_prefix(ip)
