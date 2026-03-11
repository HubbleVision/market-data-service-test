#!/usr/bin/env python3
"""Port scanner to find running services"""
import socket

ports = [8000, 8080, 3000, 5000, 9000, 4000, 7000, 8888, 9090, 5001]
print("Scanning ports...")
for port in ports:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    if result == 0:
        print(f'Port {port} is open')
    sock.close()
print('Scan complete')
