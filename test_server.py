import socket
import sys

def test_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('0.0.0.0', 5000))
    if result == 0:
        print("Port 5000 is in use")
        return False
    else:
        print("Port 5000 is available")
        return True
    sock.close()

if __name__ == "__main__":
    test_port()
