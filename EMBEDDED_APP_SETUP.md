# 🚀 Embedded Shopify App Setup Guide

This guide covers all the **non-code changes** required to convert your WhatsApp Launcher app into a fully functional embedded Shopify app.

## 📋 Table of Contents

1. [Shopify Partner Dashboard Setup](#shopify-partner-dashboard-setup)
2. [App Configuration](#app-configuration)
3. [Webhook Configuration](#webhook-configuration)
4. [Hosting Requirements](#hosting-requirements)
5. [SSL/HTTPS Setup](#sslhttps-setup)
6. [App Submission (Optional)](#app-submission-optional)
7. [Testing Checklist](#testing-checklist)

---

## 1. Shopify Partner Dashboard Setup

### Step 1: Create/Login to Partner Account

1. Go to [Shopify Partners](https://partners.shopify.com/)
2. Sign in or create a new partner account
3. Navigate to **Apps** → **Create app**

### Step 2: Create a New App

1. Click **"Create app"** → **"Custom app"**
2. Fill in the app details:
   - **App name**: `WhatsApp Launcher` (or your preferred name)
   - **App URL**: 
     - Development: `http://localhost:8000/embedded`
     - Production: `https://your-domain.com/embedded`
   - **Allowed redirection URL(s)**:
     - Development: `http://localhost:8000/auth/callback`
     - Production: `https://your-domain.com/auth/callback`
   - **Embedded app**: ✅ **Yes** (This is critical!)
   - **App setup**: Complete

### Step 3: Get Your API Credentials

After creating the app, you'll receive:
- **API Key** (Client ID)
- **API Secret Key** (Client Secret)

Save these credentials securely - you'll need them for your `.env` file.

---

## 2. App Configuration

### Step 1: Update Environment Variables

Create or update your `.env` file with the following:

```env
# Shopify App Credentials
SHOPIFY_API_KEY=your_api_key_from_partner_dashboard
SHOPIFY_API_SECRET=your_api_secret_from_partner_dashboard

# App URLs
APP_URL=http://localhost:8000  # For development
# APP_URL=https://your-domain.com  # For production

# Database Configuration (if using PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database
DB_BACKEND=file  # Use 'file' for development, 'postgres' for production

# Optional: Port configuration
PORT=8000
```

### Step 2: Configure App Scopes

In your Shopify Partner Dashboard:

1. Go to **App setup** → **Configuration**
2. Under **Scopes**, ensure these are selected:
   - ✅ `read_themes`
   - ✅ `write_themes`
   - ✅ `read_script_tags`
   - ✅ `write_script_tags`

These scopes allow your app to:
- Check theme compatibility
- Install the WhatsApp widget script tag on the storefront

### Step 3: Update app.toml

The `app.toml` file has been updated with the correct configuration. Make sure to:

1. Replace `your_shopify_api_key_here` with your actual API key
2. Update `dev_store_url` with your development store URL
3. Add your production domain to `redirect_urls` when deploying

---

## 3. Webhook Configuration

### Step 1: Register Webhooks in Partner Dashboard

1. Go to **App setup** → **Webhooks**
2. Click **"Create webhook"**
3. Configure the following webhook:

**App Uninstalled Webhook:**
- **Event**: `app/uninstalled`
- **Format**: JSON
- **URL**: `https://your-domain.com/webhooks/app/uninstalled`
- **API version**: `2024-01` (or latest)

### Step 2: Verify Webhook Endpoint

Your webhook endpoint is already implemented in `main.py`:
```python
@app.post("/webhooks/app/uninstalled")
```

This endpoint:
- Verifies the webhook signature using HMAC
- Removes the installation and configuration when the app is uninstalled
- Cleans up analytics data

### Step 3: Test Webhooks (Development)

For local development, use a tool like:
- **ngrok**: `ngrok http 8000` (creates a public URL)
- **Cloudflare Tunnel**: Free alternative to ngrok
- **Shopify CLI**: `shopify app dev` (handles tunneling automatically)

Update your webhook URL in Partner Dashboard to use the tunnel URL.

---

## 4. Hosting Requirements

### Required Features

Your hosting provider must support:

1. **HTTPS/SSL**: Mandatory for embedded apps
2. **Python 3.9+**: For running FastAPI
3. **Environment Variables**: For storing secrets
4. **Persistent Storage**: For database (file or PostgreSQL)
5. **Custom Domain**: For production (optional but recommended)

### Recommended Hosting Options

#### Option 1: Render (Recommended for Starters)
- ✅ Free tier available
- ✅ Automatic SSL
- ✅ Easy environment variable setup
- ✅ PostgreSQL support

**Setup:**
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python main.py`
4. Add environment variables in dashboard

#### Option 2: Railway
- ✅ Simple deployment
- ✅ Automatic SSL
- ✅ PostgreSQL included
- ✅ Free tier available

#### Option 3: Heroku
- ✅ Well-documented
- ✅ Add-ons available
- ⚠️ Requires credit card for some features

#### Option 4: DigitalOcean App Platform
- ✅ Good performance
- ✅ PostgreSQL support
- ⚠️ Paid service

#### Option 5: AWS/GCP/Azure
- ✅ Enterprise-grade
- ✅ Highly scalable
- ⚠️ More complex setup
- ⚠️ Higher cost

---

## 5. SSL/HTTPS Setup

### Why HTTPS is Required

Shopify embedded apps **require HTTPS** for security. The app will not work without SSL.

### Automatic SSL (Recommended)

Most modern hosting providers offer automatic SSL:
- **Render**: Automatic SSL with Let's Encrypt
- **Railway**: Automatic SSL
- **Heroku**: Automatic SSL
- **Cloudflare**: Free SSL with proxy

### Manual SSL Setup

If you need to set up SSL manually:

1. **Get SSL Certificate**:
   - Let's Encrypt (free)
   - Cloudflare (free with proxy)
   - Paid certificates from providers

2. **Configure Your Server**:
   - Update your FastAPI app to use HTTPS
   - Configure certificate paths
   - Update firewall rules

3. **Update Environment Variables**:
   ```env
   APP_URL=https://your-domain.com
   ```

---

## 6. App Submission (Optional)

If you want to publish your app to the Shopify App Store:

### Step 1: Complete App Listing

1. Go to **App listing** in Partner Dashboard
2. Fill in:
   - App name and description
   - Screenshots and videos
   - Pricing information
   - Support contact details
   - Privacy policy URL
   - Terms of service URL

### Step 2: App Review Requirements

Shopify requires:
- ✅ Privacy policy page
- ✅ Terms of service page
- ✅ Support contact information
- ✅ Proper error handling
- ✅ Security best practices
- ✅ No hardcoded credentials
- ✅ Proper webhook handling

### Step 3: Create Required Pages

Add these endpoints to your app:

```python
@app.get("/privacy")
async def privacy_policy():
    return templates.TemplateResponse("privacy.html", {"request": request})

@app.get("/terms")
async def terms_of_service():
    return templates.TemplateResponse("terms.html", {"request": request})
```

### Step 4: Submit for Review

1. Go to **App listing** → **Submit for review**
2. Fill out the review form
3. Wait for Shopify's review (typically 1-2 weeks)

---

## 7. Testing Checklist

### Pre-Deployment Testing

- [ ] **OAuth Flow**
  - [ ] App installation works
  - [ ] Redirect URL is correct
  - [ ] Access token is stored

- [ ] **Embedded App**
  - [ ] App loads in Shopify admin
  - [ ] Session token authentication works
  - [ ] Configuration form works
  - [ ] API endpoints respond correctly

- [ ] **Widget Installation**
  - [ ] Script tag is installed on storefront
  - [ ] Widget appears on store pages
  - [ ] Widget opens WhatsApp correctly
  - [ ] Pre-filled message works

- [ ] **Webhooks**
  - [ ] Uninstall webhook is received
  - [ ] Data is cleaned up on uninstall
  - [ ] Webhook signature verification works

- [ ] **Security**
  - [ ] HTTPS is enabled
  - [ ] Session tokens are verified
  - [ ] Webhook signatures are verified
  - [ ] No sensitive data in logs

### Post-Deployment Testing

- [ ] Test on a real Shopify store
- [ ] Verify widget works on mobile
- [ ] Check analytics tracking
- [ ] Test uninstall flow
- [ ] Verify error handling

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Invalid session token" Error

**Cause**: Session token verification failing

**Solutions**:
- Ensure `SHOPIFY_API_SECRET` is correct
- Check that App Bridge is initialized properly
- Verify the `host` parameter is passed correctly

#### 2. App Not Loading in Shopify Admin

**Cause**: CSP headers or iframe issues

**Solutions**:
- Verify CSP headers in `main.py` are correct
- Check that `embedded = true` in Partner Dashboard
- Ensure HTTPS is enabled

#### 3. Widget Not Appearing on Storefront

**Cause**: Script tag not installed

**Solutions**:
- Check script tags in Partner Dashboard → App setup → Script tags
- Verify `install_script_tag()` function is called
- Check browser console for JavaScript errors

#### 4. Webhook Not Receiving Events

**Cause**: Webhook URL incorrect or not accessible

**Solutions**:
- Verify webhook URL is publicly accessible
- Check webhook signature verification
- Use ngrok or similar tool for local testing

---

## 📚 Additional Resources

- [Shopify App Development Docs](https://shopify.dev/docs/apps)
- [App Bridge Documentation](https://shopify.dev/docs/apps/tools/app-bridge)
- [OAuth Documentation](https://shopify.dev/docs/apps/auth/oauth)
- [Webhook Documentation](https://shopify.dev/docs/apps/webhooks)
- [Shopify Partner Community](https://community.shopify.com/)

---

## ✅ Quick Start Checklist

1. [ ] Create Shopify Partner account
2. [ ] Create app in Partner Dashboard
3. [ ] Get API credentials
4. [ ] Update `.env` file
5. [ ] Configure app scopes
6. [ ] Set up webhooks
7. [ ] Deploy to hosting with HTTPS
8. [ ] Update app URLs in Partner Dashboard
9. [ ] Test installation flow
10. [ ] Test embedded app
11. [ ] Test widget on storefront

---

## 🎉 You're All Set!

Once you've completed these steps, your app should be fully functional as an embedded Shopify app. Users can install it from the Shopify admin and configure the WhatsApp widget directly from within Shopify.

For questions or issues, refer to the troubleshooting section or Shopify's documentation.

