
import re
import socket
import ipaddress
from urllib.parse import urlparse

def validate_url(url: str):
    print(f"Testing: {url}")
    # 1. Injection Prevention (Strict Regex)
    if re.search(r'[;&|`$()<>]', url):
        print("  -> Blocked by Injection Check")
        return

    # 2. Protocol Validation
    if not (url.startswith("http://") or url.startswith("https://")):
        print("  -> Blocked by Protocol Check")
        return

    # 3. SSRF Protection (IP Blocking)
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            print("  -> Invalid Hostname")
            return

        # Resolve DNS
        # Mocking resolution for test safety/speed constraints in this env if needed, 
        # but here we'll try real resolution.
        # If localhost, it resolves to 127.0.0.1
        try:
            ip = socket.gethostbyname(hostname)
        except:
             print("  -> DNS Resolution Failed")
             return
             
        ip_obj = ipaddress.ip_address(ip)

        if ip_obj.is_private or ip_obj.is_loopback:
             print(f"  -> Blocked by SSRF Check (IP: {ip})")
             return
             
    except Exception as e:
        print(f"  -> Validation Exception: {e}")
        return
        
    print("  -> ALLOWED")

# Test Cases
validate_url("https://github.com/user/repo")
validate_url("http://localhost:8000/admin")
validate_url("http://127.0.0.1/config")
validate_url("https://github.com/user/repo; rm -rf /")
validate_url("https://github.com/user/repo|nc 1.2.3.4")
