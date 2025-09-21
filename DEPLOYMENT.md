# 🚀 Deployment Guide for Streamlit Cloud

This guide will help you deploy the Kolam Art Studio application to Streamlit Cloud with proper API key management.

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Gemini API Key**: Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

## 🌐 Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. **Ensure all files are committed to GitHub:**
   ```bash
   git add .
   git commit -m "Add Kolam Art Studio application"
   git push origin main
   ```

2. **Required files in your repository:**
   ```
   your-repo/
   ├── main.py
   ├── requirements.txt
   ├── kolam_generator.py
   ├── kolam_recognition.py
   ├── kolam_editor.py
   ├── gemini_integration.py
   ├── config.py
   └── README.md
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with your GitHub account**
3. **Click "New app"**
4. **Configure your app:**
   - **Repository**: Select your GitHub repository
   - **Branch**: Select `main` (or your default branch)
   - **Main file path**: `main.py`
   - **App URL**: Choose a unique URL (e.g., `your-username-kolam-art-studio`)

### Step 3: Configure API Key (Choose One Method)

#### Method 1: Using Streamlit Secrets (Recommended for Production)

1. **In your Streamlit Cloud dashboard:**
   - Go to your app's settings
   - Click on "Secrets"
   - Add the following secret:

   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

2. **Redeploy your app** after adding the secret

#### Method 2: Using App Settings (Recommended for Testing)

1. **Deploy your app first**
2. **Navigate to your deployed app**
3. **Go to the Settings page**
4. **Enter your API key in the app interface**
5. **Click "Save API Key"**

### Step 4: Verify Deployment

1. **Check that your app loads without errors**
2. **Navigate to the Settings page**
3. **Verify API key status shows "✅ Gemini API Connected"**
4. **Test AI features:**
   - Upload a Kolam image for analysis
   - Try the AI Analysis page
   - Test design suggestions

## 🔧 Configuration Options

### App Settings in Streamlit Cloud

You can also configure these optional settings in your Streamlit Cloud dashboard:

```toml
[theme]
primaryColor = "#2E86AB"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"

[browser]
gatherUsageStats = false
```

### Custom Domain (Optional)

If you have a custom domain:
1. Go to your app settings in Streamlit Cloud
2. Add your custom domain
3. Update your DNS settings as instructed

## 🔒 Security Best Practices

### For API Keys:
- ✅ **Do**: Use Streamlit secrets for production
- ✅ **Do**: Never commit API keys to your repository
- ✅ **Do**: Use different API keys for development and production
- ❌ **Don't**: Share your API key publicly
- ❌ **Don't**: Hard-code API keys in your source code

### For Repository:
- ✅ **Do**: Keep your repository private if it contains sensitive information
- ✅ **Do**: Use `.gitignore` to exclude sensitive files
- ✅ **Do**: Regularly update dependencies for security patches

## 🐛 Troubleshooting

### Common Issues:

1. **"Gemini API not configured" error:**
   - Check that your API key is correctly set in Streamlit secrets
   - Verify the key is valid by testing it locally
   - Redeploy your app after adding secrets

2. **App fails to start:**
   - Check that all dependencies are in `requirements.txt`
   - Verify that `main.py` is in the root directory
   - Check the Streamlit Cloud logs for specific errors

3. **AI features not working:**
   - Ensure your API key has proper permissions
   - Check that you're using the correct Gemini API endpoint
   - Verify your API key quota hasn't been exceeded

### Getting Help:

1. **Check Streamlit Cloud logs:**
   - Go to your app dashboard
   - Click on "Logs" to see detailed error messages

2. **Test locally first:**
   - Run the app locally to ensure it works
   - Use the same configuration as your cloud deployment

3. **Streamlit Community:**
   - Visit [discuss.streamlit.io](https://discuss.streamlit.io) for community support

## 📊 Monitoring and Analytics

### Streamlit Cloud Analytics:
- View app usage statistics in your dashboard
- Monitor performance and error rates
- Track user engagement

### API Usage Monitoring:
- Monitor your Gemini API usage in Google AI Studio
- Set up usage alerts to avoid quota limits
- Track costs and optimize usage

## 🔄 Updates and Maintenance

### Updating Your App:
1. **Make changes to your local code**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Update app features"
   git push origin main
   ```
3. **Streamlit Cloud will automatically redeploy**

### Dependency Updates:
1. **Update `requirements.txt` with new versions**
2. **Commit and push changes**
3. **App will automatically redeploy with new dependencies**

## 🎯 Performance Optimization

### For Better Performance:
- Use Streamlit caching for expensive operations
- Optimize image processing for faster uploads
- Implement lazy loading for large datasets
- Use session state efficiently

### Resource Limits:
- Streamlit Cloud has memory and CPU limits
- Monitor your app's resource usage
- Optimize code if you hit limits

---

**🎉 Congratulations!** Your Kolam Art Studio is now deployed on Streamlit Cloud and ready to share with the world!

**Share your app:** Once deployed, you can share your app URL with others to explore the beautiful world of Kolam art with AI.
