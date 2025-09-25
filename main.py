from fastapi import FastAPI, Request, Form, HTTPException, Header
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import hmac
import hashlib
import base64
import json
import requests
import jwt
from datetime import datetime
from urllib.parse import urlencode, parse_qs, unquote
from typing import Optional

load_dotenv()

app = FastAPI()

# Add CORS middleware for embedded app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Shopify App Configuration
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
SHOPIFY_SCOPES = "read_themes,write_themes,read_script_tags,write_script_tags"
APP_URL = os.getenv("APP_URL", "http://localhost:8000")

# Database
from database import db

def verify_shopify_webhook(data, hmac_header):
    """Verify Shopify webhook signature"""
    calculated_hmac = base64.b64encode(
        hmac.new(
            SHOPIFY_API_SECRET.encode('utf-8'),
            data,
            digestmod=hashlib.sha256
        ).digest()
    ).decode()
    return hmac.compare_digest(calculated_hmac, hmac_header)

def verify_shopify_request(request: Request):
    """Verify embedded app request from Shopify"""
    shop = request.query_params.get("shop")
    hmac_param = request.query_params.get("hmac")
    
    if not shop or not hmac_param:
        return None
    
    # Create query string without hmac for verification
    query_params = dict(request.query_params)
    query_params.pop("hmac", None)
    query_params.pop("signature", None)
    
    # Sort parameters and create query string
    sorted_params = sorted(query_params.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    
    # Calculate HMAC
    calculated_hmac = hmac.new(
        SHOPIFY_API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    if hmac.compare_digest(calculated_hmac, hmac_param):
        return shop
    return None

def verify_session_token(session_token: str):
    """Verify Shopify session token for embedded apps"""
    try:
        # Handle development tokens
        if session_token.startswith("dev-token-"):
            shop = session_token.replace("dev-token-", "")
            return shop
        
        if session_token == "dev-token" or session_token == "fallback-token":
            # For development, extract shop from request context if available
            return None
        
        # Decode without verification first to get the shop
        unverified = jwt.decode(session_token, options={"verify_signature": False})
        shop = unverified.get("dest", "").replace("https://", "").replace("/admin", "")
        
        # Verify with secret
        payload = jwt.decode(
            session_token,
            SHOPIFY_API_SECRET,
            algorithms=["HS256"],
            audience=SHOPIFY_API_KEY
        )
        
        return shop
    except jwt.InvalidTokenError:
        return None

@app.get("/")
async def root():
    return {"message": "Shopify WhatsApp Launcher App"}

@app.get("/install")
async def install(shop: str):
    """Shopify app installation endpoint"""
    if not shop:
        raise HTTPException(status_code=400, detail="Shop parameter required")
    
    # Build authorization URL
    params = {
        "client_id": SHOPIFY_API_KEY,
        "scope": SHOPIFY_SCOPES,
        "redirect_uri": f"{APP_URL}/auth/callback",
        "state": shop
    }
    
    # auth_url = f"https://{shop}.myshopify.com/admin/oauth/authorize?" + urlencode(params)
    auth_url = f"https://{shop}.com/admin/oauth/authorize?" + urlencode(params)
    return RedirectResponse(url=auth_url)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle Shopify OAuth callback"""
    query_params = dict(request.query_params)
    
    if "error" in query_params:
        raise HTTPException(status_code=400, detail="Authorization denied")
    
    shop = query_params.get("shop")
    code = query_params.get("code")
    
    if not shop or not code:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    # Exchange code for access token
    token_data = {
        "client_id": SHOPIFY_API_KEY,
        "client_secret": SHOPIFY_API_SECRET,
        "code": code
    }
    
    response = requests.post(
        f"https://{shop}/admin/oauth/access_token",
        json=token_data
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    
    access_token = response.json()["access_token"]
    
    # Store installation
    db.save_installation(shop, access_token)
    
    return RedirectResponse(url=f"/dashboard?shop={shop}")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, shop: str):
    """Main dashboard for WhatsApp configuration"""
    installation = db.get_installation(shop)
    if not installation:
        return RedirectResponse(url=f"/install?shop={shop}")
    
    current_config = db.get_whatsapp_config(shop) or {}
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "shop": shop,
        "config": current_config
    })

@app.get("/embedded", response_class=HTMLResponse)
async def embedded_app(request: Request):
    """Embedded app entry point"""
    shop = request.query_params.get("shop")
    
    if not shop:
        raise HTTPException(status_code=400, detail="Shop parameter required")
    
    # Verify the request is from Shopify
    verified_shop = verify_shopify_request(request)
    if not verified_shop:
        raise HTTPException(status_code=401, detail="Invalid request")
    
    # Check if app is installed
    installation = db.get_installation(shop)
    if not installation:
        # Redirect to installation
        return templates.TemplateResponse("install_embedded.html", {
            "request": request,
            "shop": shop,
            "api_key": SHOPIFY_API_KEY,
            "app_url": APP_URL
        })
    
    current_config = db.get_whatsapp_config(shop) or {}
    
    return templates.TemplateResponse("embedded_dashboard.html", {
        "request": request,
        "shop": shop,
        "config": current_config,
        "api_key": SHOPIFY_API_KEY,
        "app_url": APP_URL
    })

@app.post("/api/configure-whatsapp")
async def api_configure_whatsapp(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """API endpoint for embedded app WhatsApp configuration"""
    # Get session token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        # Fallback: try to get shop from request body for development
        try:
            form_data = await request.json()
            shop = form_data.get("shop")
            if shop and db.get_installation(shop):
                # Allow for development/testing
                pass
            else:
                raise HTTPException(status_code=401, detail="Missing session token")
        except:
            raise HTTPException(status_code=401, detail="Missing session token")
    else:
        session_token = authorization.replace("Bearer ", "")
        shop = verify_session_token(session_token)
        
        if not shop:
            # Try to get shop from request body as fallback
            try:
                form_data = await request.json()
                shop = form_data.get("shop")
                if not shop or not db.get_installation(shop):
                    raise HTTPException(status_code=401, detail="Invalid session token")
            except:
                raise HTTPException(status_code=401, detail="Invalid session token")
    
    installation = db.get_installation(shop)
    if not installation:
        raise HTTPException(status_code=401, detail="App not installed")
    
    # Get form data
    form_data = await request.json()
    phone_number = form_data.get("phone_number")
    initial_message = form_data.get("initial_message")
    
    if not phone_number or not initial_message:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Validate phone number (basic validation)
    if not phone_number.replace("+", "").replace("-", "").replace(" ", "").isdigit():
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    # Store configuration
    db.save_whatsapp_config(shop, phone_number, initial_message)
    
    # Install script tag in Shopify store
    await install_script_tag(shop)
    
    return JSONResponse({"success": True, "message": "Configuration saved successfully"})

@app.get("/api/config")
async def get_config(request: Request, authorization: Optional[str] = Header(None)):
    """Get current WhatsApp configuration for embedded app"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing session token")
    
    session_token = authorization.replace("Bearer ", "")
    shop = verify_session_token(session_token)
    
    if not shop:
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    config = db.get_whatsapp_config(shop) or {}
    return JSONResponse(config)

@app.get("/api/config-fallback")
async def get_config_fallback(shop: str):
    """Fallback endpoint to get configuration when App Bridge is not available"""
    if not shop:
        raise HTTPException(status_code=400, detail="Shop parameter required")
    
    # Verify the shop has the app installed
    installation = db.get_installation(shop)
    if not installation:
        raise HTTPException(status_code=401, detail="App not installed")
    
    config = db.get_whatsapp_config(shop) or {}
    return JSONResponse(config)

@app.post("/configure-whatsapp")
async def configure_whatsapp(
    shop: str = Form(...),
    phone_number: str = Form(...),
    initial_message: str = Form(...)
):
    """Configure WhatsApp settings"""
    installation = db.get_installation(shop)
    if not installation:
        raise HTTPException(status_code=401, detail="App not installed")
    
    # Validate phone number (basic validation)
    if not phone_number.replace("+", "").replace("-", "").replace(" ", "").isdigit():
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    # Store configuration
    db.save_whatsapp_config(shop, phone_number, initial_message)
    
    # Install script tag in Shopify store
    await install_script_tag(shop)
    
    return RedirectResponse(url=f"/dashboard?shop={shop}&success=1", status_code=303)

async def install_script_tag(shop: str):
    """Install script tag in Shopify store"""
    installation = db.get_installation(shop)
    if not installation:
        return
    
    access_token = installation["access_token"]
    
    script_tag_data = {
        "script_tag": {
            "event": "onload",
            "src": f"{APP_URL}/whatsapp-widget.js?shop={shop}"
        }
    }
    
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    # Check if script tag already exists
    response = requests.get(
        f"https://{shop}/admin/api/2023-10/script_tags.json",
        headers=headers
    )
    
    existing_scripts = response.json().get("script_tags", [])
    widget_script_exists = any(
        script.get("src", "").startswith(f"{APP_URL}/whatsapp-widget.js")
        for script in existing_scripts
    )
    
    if not widget_script_exists:
        requests.post(
            f"https://{shop}/admin/api/2023-10/script_tags.json",
            headers=headers,
            json=script_tag_data
        )

@app.get("/whatsapp-widget.js")
async def whatsapp_widget(shop: str):
    """Serve WhatsApp widget JavaScript"""
    config = db.get_whatsapp_config(shop)
    
    if not config:
        return ""
    
    phone_number = config["phone_number"].replace("+", "").replace("-", "").replace(" ", "")
    initial_message = config["initial_message"]
    
    js_code = f"""
(function() {{
    // Create WhatsApp widget
    const whatsappWidget = document.createElement('div');
    whatsappWidget.id = 'whatsapp-widget';
    whatsappWidget.innerHTML = `
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background-color: #25D366;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            transition: transform 0.3s ease;
        " onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="white">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
            </svg>
        </div>
    `;
    
    whatsappWidget.onclick = function() {{
        const message = encodeURIComponent("{initial_message}");
        const whatsappUrl = `https://wa.me/{phone_number}?text=${{message}}`;
        window.open(whatsappUrl, '_blank');
    }};
    
    document.body.appendChild(whatsappWidget);
}})();
"""
    
    return HTMLResponse(content=js_code, media_type="application/javascript")

@app.post("/api/widget-click")
async def widget_click(request: Request):
    """Track widget clicks for analytics"""
    try:
        data = await request.json()
        shop = data.get("shop")
        if shop:
            db.log_widget_click(shop)
        return JSONResponse({"success": True})
    except Exception:
        return JSONResponse({"success": False})

@app.get("/api/analytics")
async def get_analytics(request: Request, authorization: Optional[str] = Header(None)):
    """Get analytics data for embedded app"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing session token")
    
    session_token = authorization.replace("Bearer ", "")
    shop = verify_session_token(session_token)
    
    if not shop:
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    analytics = db.get_analytics(shop)
    return JSONResponse(analytics)

@app.post("/webhooks/app/uninstalled")
async def app_uninstalled(request: Request, x_shopify_hmac_sha256: str = Header(None)):
    """Handle app uninstallation webhook"""
    body = await request.body()
    
    if not verify_shopify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    try:
        data = json.loads(body)
        shop = data.get("domain")
        if shop:
            db.remove_installation(shop)
    except Exception as e:
        print(f"Error handling uninstall webhook: {e}")
    
    return JSONResponse({"success": True})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
