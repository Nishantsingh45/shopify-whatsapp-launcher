# 🚀 Deploying Shopify WhatsApp Launcher to Render.com

This guide will help you deploy your Shopify WhatsApp Launcher app to Render.com.

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Render.com Account**: Sign up at [render.com](https://render.com)
3. **Shopify Partner Account**: With your app credentials

## 🔧 Step 1: Prepare Your Repository

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Shopify WhatsApp Launcher"
   git branch -M main
   git remote add origin https://github.com/yourusername/shopify-whatsapp-launcher.git
   git push -u origin main
   ```

2. **Ensure these files are in your repository**:
   - ✅ `render.yaml` (deployment configuration)
   - ✅ `requirements.txt` (Python dependencies)
   - ✅ `runtime.txt` (Python version)
   - ✅ `main.py` (main application)
   - ✅ `Dockerfile` (optional, for Docker deployment)
   - ✅ `.gitignore` (to exclude sensitive files)

## 🌐 Step 2: Deploy to Render.com

### Option A: Using render.yaml (Recommended)

1. **Connect GitHub to Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub account
   - Select your repository

2. **Render will automatically detect the `render.yaml` file**

3. **Set Environment Variables**:
   - In the Render dashboard, go to your service
   - Navigate to "Environment" tab
   - Add these variables:
     ```
     SHOPIFY_API_KEY=ddd93446f7bd182a7b47b037bd41125a
     SHOPIFY_API_SECRET=3b87af5dbc3fefb290e4dbea6ae4ed40
     APP_URL=https://your-app-name.onrender.com
     ```

### Option B: Manual Web Service Creation

1. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   - **Name**: `shopify-whatsapp-launcher`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

3. **Set Environment Variables** (same as above)

## 🔑 Step 3: Update Shopify App Settings

1. **Go to your Shopify Partner Dashboard**
2. **Update App URLs**:
   - **App URL**: `https://your-app-name.onrender.com/embedded`
   - **Allowed redirection URLs**: `https://your-app-name.onrender.com/auth/callback`

3. **Update Webhooks** (optional):
   - **App uninstalled**: `https://your-app-name.onrender.com/webhooks/app/uninstalled`

## 📊 Step 4: Configure Persistent Storage

Render.com provides persistent disks for data storage:

1. **In your service settings**:
   - Go to "Disks" tab
   - Add a new disk:
     - **Name**: `app-data`
     - **Mount Path**: `/app/data`
     - **Size**: `1 GB` (free tier)

2. **The app is already configured to use this path for the database**

## 🧪 Step 5: Test Your Deployment

1. **Check Health Endpoint**:
   ```
   https://your-app-name.onrender.com/health
   ```

2. **Test Installation**:
   ```
   https://your-app-name.onrender.com/install?shop=your-dev-store
   ```

3. **Test Embedded App**:
   ```
   https://your-app-name.onrender.com/embedded?shop=your-dev-store.myshopify.com
   ```

## 🔒 Step 6: Security Considerations

1. **Environment Variables**: Never commit API keys to your repository
2. **HTTPS**: Render.com provides free SSL certificates
3. **Webhooks**: Ensure webhook verification is enabled in production

## 📈 Step 7: Monitoring and Logs

1. **View Logs**:
   - Go to your service in Render dashboard
   - Click "Logs" tab to see real-time logs

2. **Monitor Performance**:
   - Check the "Metrics" tab for performance data
   - Set up alerts if needed

## 🚀 Step 8: Custom Domain (Optional)

1. **Add Custom Domain**:
   - Go to "Settings" → "Custom Domains"
   - Add your domain (e.g., `whatsapp-launcher.yourdomain.com`)
   - Update DNS records as instructed

2. **Update Shopify App Settings** with your custom domain

## 🔄 Step 9: Continuous Deployment

Render.com automatically deploys when you push to your main branch:

1. **Make changes locally**
2. **Commit and push**:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```
3. **Render automatically deploys the changes**

## 🐛 Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check `requirements.txt` for correct dependencies
   - Verify Python version in `runtime.txt`

2. **App Won't Start**:
   - Check logs for error messages
   - Ensure `PORT` environment variable is handled correctly

3. **Database Issues**:
   - Verify persistent disk is mounted at `/app/data`
   - Check file permissions

4. **Shopify OAuth Issues**:
   - Ensure APP_URL matches your Render service URL
   - Verify redirect URLs in Shopify Partner Dashboard

### Debug Commands:

```bash
# Check service status
curl https://your-app-name.onrender.com/health

# View recent logs
# (Available in Render dashboard)
```

## 💡 Pro Tips

1. **Free Tier Limitations**:
   - Services sleep after 15 minutes of inactivity
   - Consider upgrading for production use

2. **Database Backup**:
   - Regularly backup your `app_data.json` file
   - Consider upgrading to PostgreSQL for production

3. **Performance**:
   - Monitor response times
   - Consider caching for better performance

## 📞 Support

If you encounter issues:
1. Check Render.com documentation
2. Review application logs
3. Test locally first
4. Contact Render support if needed

---

🎉 **Congratulations!** Your Shopify WhatsApp Launcher app is now live on Render.com!

Your app will be available at: `https://your-app-name.onrender.com`