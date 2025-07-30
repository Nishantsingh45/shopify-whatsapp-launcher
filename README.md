# 🚀 Shopify WhatsApp Launcher App

A complete Shopify app that adds a floating WhatsApp widget to your store, allowing customers to contact you directly via WhatsApp with a pre-filled message. Built with Python, FastAPI, and modern web technologies.

## ✨ Features

- 🚀 **Easy Installation**: One-click installation via Shopify OAuth
- 📱 **Floating Widget**: Beautiful WhatsApp widget that appears on all store pages
- 💬 **Customizable Messages**: Set custom initial messages for customer conversations
- 📞 **Phone Number Configuration**: Easy setup with international phone number support
- 🎨 **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- 📊 **Analytics**: Track widget clicks and customer engagement
- 🔒 **Secure**: Proper OAuth implementation and webhook verification
- 🌐 **Embedded App**: Works seamlessly within Shopify admin interface

## 🛠️ Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd shopify-whatsapp-launcher

# Run the setup script
python setup.py
```

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Shopify app credentials
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

## 📋 Shopify App Configuration

### 1. Create a Shopify App

1. Go to your [Shopify Partner Dashboard](https://partners.shopify.com/)
2. Click "Create app" → "Custom app"
3. Fill in your app details:
   - **App name**: "WhatsApp Launcher"
   - **App URL**: `http://localhost:8000/embedded` (for development)
   - **Allowed redirection URL(s)**: `http://localhost:8000/auth/callback`
   - **Embedded**: Yes
   - **App setup**: Complete

### 2. Configure App Scopes

Required scopes:
- `read_themes` - To check theme compatibility
- `write_themes` - To inject widget code (if needed)
- `read_script_tags` - To manage script tags
- `write_script_tags` - To install the widget

### 3. Environment Variables

Update your `.env` file:

```env
SHOPIFY_API_KEY=your_shopify_api_key_here
SHOPIFY_API_SECRET=your_shopify_api_secret_here
APP_URL=http://localhost:8000

# For production:
# APP_URL=https://yourdomain.com
```

## 🚀 Installation & Usage

### For Development

1. **Start the app**:
   ```bash
   python main.py
   ```

2. **Install on a development store**:
   ```
   http://localhost:8000/install?shop=your-dev-store
   ```

3. **Configure WhatsApp settings**:
   - Enter your WhatsApp phone number (with country code)
   - Set your initial message
   - Save configuration

4. **Test the widget**:
   - Visit your store
   - Look for the floating WhatsApp icon
   - Click to test the functionality

### For Production

1. **Deploy to a hosting service** (Heroku, DigitalOcean, AWS, etc.)
2. **Update environment variables** with production URLs
3. **Configure webhooks** for app uninstallation
4. **Set up proper database** (PostgreSQL, MySQL, MongoDB)
5. **Enable HTTPS** for secure communications

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Shopify       │    │   Your App       │    │   Customer      │
│   Admin         │◄──►│   (FastAPI)      │    │   Store         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Database       │    │   WhatsApp      │
                       │   (JSON/SQL)     │    │   Chat          │
                       └──────────────────┘    └─────────────────┘
```

## 📡 API Endpoints

### Public Endpoints
- `GET /` - App information
- `GET /health` - Health check
- `GET /whatsapp-widget.js` - Widget JavaScript

### OAuth Endpoints
- `GET /install` - Start app installation
- `GET /auth/callback` - OAuth callback
- `GET /embedded` - Embedded app entry point

### Dashboard Endpoints
- `GET /dashboard` - Configuration dashboard (standalone)
- `POST /configure-whatsapp` - Save WhatsApp settings

### API Endpoints (for embedded app)
- `GET /api/config` - Get current configuration
- `POST /api/configure-whatsapp` - Save configuration
- `GET /api/analytics` - Get usage analytics
- `POST /api/widget-click` - Track widget clicks

### Webhook Endpoints
- `POST /webhooks/app/uninstalled` - Handle app uninstallation

## 🎨 Widget Customization

The widget supports various customization options:

```javascript
// Advanced widget configuration
const widget = new WhatsAppWidgetCustomizer({
    position: 'bottom-right',     // bottom-left, top-right, etc.
    size: 60,                     // Widget size in pixels
    backgroundColor: '#25D366',   // WhatsApp green
    hoverColor: '#128C7E',       // Darker green on hover
    showTooltip: true,           // Show tooltip on hover
    tooltipText: 'Chat with us!', // Custom tooltip text
    animation: true              // Enable hover animations
});
```

## 📊 Analytics & Monitoring

The app tracks:
- Widget click counts
- First and last click timestamps
- Installation dates
- Configuration updates

Access analytics via the embedded app dashboard or API endpoint.

## 🔒 Security Features

- **OAuth 2.0**: Secure Shopify app installation
- **HMAC Verification**: Webhook signature verification
- **JWT Tokens**: Session token validation for embedded apps
- **Input Validation**: Phone number and message validation
- **CORS Protection**: Proper CORS configuration

## 🗄️ Database Schema

### Development (JSON File)
```json
{
  "installations": {
    "shop-name.myshopify.com": {
      "access_token": "...",
      "shop": "shop-name.myshopify.com",
      "installed_at": "2024-01-01T00:00:00"
    }
  },
  "whatsapp_configs": {
    "shop-name.myshopify.com": {
      "phone_number": "+1234567890",
      "initial_message": "Hi! I'm interested in your products.",
      "updated_at": "2024-01-01T00:00:00"
    }
  },
  "analytics": {
    "shop-name.myshopify.com": {
      "widget_clicks": 42,
      "first_click": "2024-01-01T00:00:00",
      "last_click": "2024-01-02T00:00:00"
    }
  }
}
```

### Production (SQL)
```sql
-- App installations
CREATE TABLE installations (
    shop VARCHAR(255) PRIMARY KEY,
    access_token VARCHAR(255) NOT NULL,
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- WhatsApp configurations
CREATE TABLE whatsapp_configs (
    shop VARCHAR(255) PRIMARY KEY,
    phone_number VARCHAR(50) NOT NULL,
    initial_message TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shop) REFERENCES installations(shop)
);

-- Analytics
CREATE TABLE analytics (
    shop VARCHAR(255) PRIMARY KEY,
    widget_clicks INTEGER DEFAULT 0,
    first_click TIMESTAMP,
    last_click TIMESTAMP,
    FOREIGN KEY (shop) REFERENCES installations(shop)
);
```

## 🚀 Deployment Options

### Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
heroku config:set SHOPIFY_API_KEY=your_key
heroku config:set SHOPIFY_API_SECRET=your_secret
heroku config:set APP_URL=https://your-app-name.herokuapp.com
git push heroku main
```

### DigitalOcean App Platform
```yaml
# app.yaml
name: whatsapp-launcher
services:
- name: web
  source_dir: /
  github:
    repo: your-username/shopify-whatsapp-launcher
    branch: main
  run_command: python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: SHOPIFY_API_KEY
    value: your_key
  - key: SHOPIFY_API_SECRET
    value: your_secret
  - key: APP_URL
    value: https://your-app.ondigitalocean.app
```

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## 🐛 Troubleshooting

### Common Issues

1. **"App not installed" error**
   - Ensure you've completed the OAuth flow
   - Check that your API credentials are correct

2. **Widget not appearing**
   - Verify the script tag was installed
   - Check browser console for JavaScript errors
   - Ensure WhatsApp configuration is saved

3. **"Invalid session token" error**
   - This happens in embedded apps - ensure you're using the correct session token
   - Try refreshing the Shopify admin page

4. **Phone number validation fails**
   - Include country code (e.g., +1 for US)
   - Remove spaces and special characters except +

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and code comments
- **Issues**: Open a GitHub issue for bugs or feature requests
- **Email**: [your-email@domain.com]
- **Discord**: [Your Discord server link]

## 🎯 Roadmap

- [ ] Advanced widget customization options
- [ ] Multiple WhatsApp numbers support
- [ ] Scheduled messages
- [ ] Customer conversation history
- [ ] Integration with Shopify customer data
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

---

Made with ❤️ for the Shopify community