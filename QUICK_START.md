# ⚡ Quick Start Guide

Get your embedded Shopify app up and running in 5 minutes!

## 🚀 Quick Setup Steps

### 1. Shopify Partner Dashboard (2 minutes)

1. Go to [partners.shopify.com](https://partners.shopify.com)
2. Create/Login to your account
3. Click **"Create app"** → **"Custom app"**
4. Fill in:
   - **App name**: WhatsApp Launcher
   - **App URL**: `http://localhost:8000/embedded` (for now)
   - **Redirect URL**: `http://localhost:8000/auth/callback`
   - **Embedded**: ✅ Yes
5. Copy your **API Key** and **API Secret**

### 2. Environment Setup (1 minute)

Create a `.env` file in the project root:

```env
SHOPIFY_API_KEY=your_api_key_here
SHOPIFY_API_SECRET=your_api_secret_here
APP_URL=http://localhost:8000
```

### 3. Run the App (1 minute)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

### 4. Test Installation (1 minute)

1. Open: `http://localhost:8000/install?shop=your-dev-store.myshopify.com`
2. Complete OAuth flow
3. Configure WhatsApp settings
4. Test the widget on your storefront!

---

## 🌐 For Production Deployment

### Option 1: Render (Easiest)

1. Push code to GitHub
2. Connect to [Render](https://render.com)
3. Add environment variables
4. Deploy!

### Option 2: Railway

1. Push code to GitHub
2. Connect to [Railway](https://railway.app)
3. Add environment variables
4. Deploy!

### After Deployment

1. Update Partner Dashboard:
   - **App URL**: `https://your-domain.com/embedded`
   - **Redirect URL**: `https://your-domain.com/auth/callback`
2. Update `.env`:
   ```env
   APP_URL=https://your-domain.com
   ```
3. Redeploy

---

## 📚 Need More Help?

- **Detailed Setup**: See `EMBEDDED_APP_SETUP.md`
- **Code Changes**: See `CHANGES_SUMMARY.md`
- **Shopify Docs**: [shopify.dev/docs/apps](https://shopify.dev/docs/apps)

---

## ✅ Checklist

- [ ] Partner account created
- [ ] App created in Partner Dashboard
- [ ] API credentials saved
- [ ] `.env` file configured
- [ ] App running locally
- [ ] OAuth flow tested
- [ ] Widget tested on storefront
- [ ] (Optional) Deployed to production

---

**That's it!** Your embedded Shopify app is ready! 🎉

