# DockTube Downloader

A beautiful web application to download YouTube videos in various formats and qualities.

## Features

- 🎥 Download videos in multiple qualities (4K, 1080p, 720p, etc.)
- 🎵 Download audio-only formats
- 📁 Choose custom download location
- 🎨 Modern, responsive UI
- 📱 Mobile-friendly design

## Free Deployment Options

### 1. Railway (Recommended - Easiest)

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Connect your GitHub repository
5. Railway will automatically detect it's a Python app
6. Deploy!

### 2. Render

**Steps:**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `python app.py`
7. Deploy!

### 3. Heroku (Free tier discontinued, but still works)

**Steps:**
1. Install Heroku CLI
2. Run these commands:
```bash
heroku login
heroku create your-app-name
git add .
git commit -m "Initial commit"
git push heroku main
```

### 4. PythonAnywhere

**Steps:**
1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Create free account
3. Go to "Web" tab
4. Click "Add a new web app"
5. Choose "Flask" and Python 3.11
6. Upload your files
7. Set up virtual environment and install requirements

### 5. Vercel

**Steps:**
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your repository
4. Set build command: `pip install -r requirements.txt`
5. Set output directory: `.`
6. Deploy!

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open http://localhost:5000
```

## Files Structure

```
YT-Video-Downloader/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # Heroku deployment config
├── runtime.txt        # Python version
└── README.md          # This file
```

## Important Notes

⚠️ **Legal Notice**: This tool is for personal use only. Respect YouTube's terms of service and copyright laws.

⚠️ **Download Location**: The web version will download files to the server's temporary directory. For local use, files will be saved to your specified folder.

## Troubleshooting

**Common Issues:**
1. **Port already in use**: Change port in `app.py` line 470
2. **yt-dlp errors**: Update yt-dlp with `pip install --upgrade yt-dlp`
3. **Deployment fails**: Check if all files are committed to Git

## Support

If you encounter any issues, check:
1. All dependencies are installed
2. Python version is 3.8+
3. Internet connection is stable
4. YouTube URL is valid

---

**தமிழ் விளக்கம்:**

இந்த YouTube வீடியோ டவுன்லோடர் பயன்பாட்டை இலவசமாக ஆன்லைனில் ஹோஸ்ட் செய்ய பல வழிகள் உள்ளன:

1. **Railway** - மிகவும் எளிதானது
2. **Render** - நல்ல விருப்பம்
3. **Heroku** - பழைய முறை
4. **PythonAnywhere** - பைத்தான் குறிப்பாக
5. **Vercel** - வேகமானது

மேலே உள்ள வழிகாட்டுதல்களைப் பின்பற்றி உங்கள் பயன்பாட்டை டிப்ளாய் செய்யலாம்! 