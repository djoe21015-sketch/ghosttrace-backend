import socket

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    587: "SMTP-SSL",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-ALT",
    8443: "HTTPS-ALT"
}

def grab_banner(domain, port):
    """
    Attempt to grab a service banner (safe, non-intrusive).
    """
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((domain, port))
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = sock.recv(1024).decode(errors="ignore")
        sock.close()
        return banner.strip()
    except Exception:
        return None


def run_port_scan(domain):
    """
    GhostTrace MAX Free Edition port scanner.
    Safe, fast, and non-intrusive.
    """
    results = {
        "domain": domain,
        "open_ports": [],
        "error": None
    }

    try:
        for port, service in COMMON_PORTS.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)

            try:
                result = sock.connect_ex((domain, port))
                if result == 0:
                    banner = grab_banner(domain, port)
                    results["open_ports"].append({
                        "port": port,
                        "service": service,
                        "banner": banner
                    })
            except Exception:
                pass
            finally:
                sock.close()

    except Exception as e:
        results["error"] = str(e)

    return results
