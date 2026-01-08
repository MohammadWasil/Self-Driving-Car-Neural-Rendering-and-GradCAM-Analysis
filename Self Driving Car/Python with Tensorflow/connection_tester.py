import socket

HOST = "192.168.0.233"   # Windows host from WSL2
PORT = 25001

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)

try:
    print("Connecting to Unity...")
    sock.connect((HOST, PORT))
    print("CONNECTED")

    while True:
        # Send steering, throttle (example)
        message = "0.5,1.0\n"
        sock.sendall(message.encode("utf-8"))
        print("Sent:", message.strip())

        # Optional: receive response
        try:
            data = sock.recv(1024)
            if data:
                print("Received:", data.decode().strip())
        except socket.timeout:
            pass

except KeyboardInterrupt:
    print("Closing connection")

except Exception as e:
    print("ERROR:", e)

finally:
    sock.close()
