from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DockTube Downloader</title>
  <link rel="icon" type="image/png" href="https://img.icons8.com/fluency/48/000000/download.png">
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
  <style>
    :root {
      --primary-color: #4F46E5;
      --primary-hover: #4338CA;
      --success-color: #10B981;
      --success-hover: #059669;
    }
    
    body {
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
      min-height: 100vh;
    }
    
    .container {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      margin: 1rem;
    }
    
    .custom-input {
      @apply w-full outline-none bg-transparent;
      transition: all 0.3s ease;
      font-size: 16px; /* Prevent zoom on iOS */
    }
    
    .custom-input:focus {
      @apply border-indigo-500;
    }
    
    .custom-button {
      @apply w-full py-3 rounded-lg flex items-center justify-center transition-all duration-300 transform;
      font-size: 16px; /* Prevent zoom on iOS */
    }
    
    .custom-button:hover {
      transform: translateY(-1px);
    }
    
    .custom-button-blue {
      background: var(--primary-color);
      color: white;
    }
    
    .custom-button-blue:hover {
      background: var(--primary-hover);
    }
    
    .custom-button-green {
      background: var(--success-color);
      color: white;
    }
    
    .custom-button-green:hover {
      background: var(--success-hover);
    }
    
    .format-section {
      @apply mb-6;
    }
    
    .format-section-title {
      @apply text-lg font-semibold text-gray-700 mb-3 flex items-center;
    }
    
    .format-grid {
      @apply grid grid-cols-1 gap-3;
    }
    
    @media (min-width: 768px) {
      .format-grid {
        @apply grid-cols-2;
      }
    }
    
    .format-option {
      @apply flex items-center bg-gray-50 rounded-lg p-3 shadow-sm transition-all duration-300 cursor-pointer;
      border: 2px solid transparent;
      min-height: 60px;
    }
    
    .format-option:hover {
      @apply bg-indigo-50 transform -translate-y-1;
    }
    
    .format-option.selected {
      @apply border-indigo-500 bg-indigo-50;
    }
    
    .format-option input[type="radio"] {
      @apply hidden;
    }
    
    .format-info {
      @apply flex flex-col w-full;
    }
    
    .format-quality {
      @apply text-sm font-medium text-gray-600;
    }
    
    .format-type {
      @apply text-xs text-gray-500;
    }
    
    .title-container {
      @apply flex justify-center items-center mb-6;
      flex-direction: column;
    }
    
    @media (min-width: 640px) {
      .title-container {
        flex-direction: row;
        margin-bottom: 2rem;
      }
    }
    
    .title-icon {
      @apply text-4xl text-indigo-500;
    }
    
    @media (min-width: 640px) {
      .title-icon {
        @apply text-6xl;
      }
    }
    
    .title-text {
      @apply text-2xl font-bold text-gray-800 mt-2;
    }
    
    @media (min-width: 640px) {
      .title-text {
        @apply text-3xl ml-3 mt-0;
      }
    }

    .folder-input-group {
      @apply relative;
    }

    .folder-button {
      @apply absolute right-2 top-1/2 transform -translate-y-1/2 bg-gray-100 p-2 rounded-lg hover:bg-gray-200 transition-colors;
    }
    
    .quality-badge {
      @apply px-2 py-1 rounded-full text-xs font-medium;
    }
    
    .quality-4k {
      @apply bg-purple-100 text-purple-800;
    }
    
    .quality-1080p {
      @apply bg-blue-100 text-blue-800;
    }
    
    .quality-720p {
      @apply bg-green-100 text-green-800;
    }
    
    .quality-480p {
      @apply bg-yellow-100 text-yellow-800;
    }
    
    .quality-360p {
      @apply bg-orange-100 text-orange-800;
    }
    
    .quality-240p {
      @apply bg-red-100 text-red-800;
    }
    
    .audio-quality {
      @apply bg-indigo-100 text-indigo-800;
    }

    .error-message {
      @apply bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4;
    }
    
    .video-title {
      @apply text-lg font-semibold text-gray-800 mb-4 text-center;
    }
    
    @media (min-width: 640px) {
      .video-title {
        @apply text-xl;
      }
    }
    
    /* Mobile-specific improvements */
    @media (max-width: 640px) {
      .container {
        margin: 0.5rem;
        padding: 1rem;
      }
      
      .format-option {
        padding: 0.75rem;
        min-height: 50px;
      }
      
      .format-quality {
        font-size: 0.875rem;
      }
      
      .format-type {
        font-size: 0.75rem;
      }
    }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
  <div class="container p-8 rounded-3xl shadow-2xl w-full max-w-4xl">
    <div class="title-container">
      <span class="material-icons title-icon">cloud_download</span>
      <h2 class="title-text">DockTube Downloader</h2>
    </div>

    {% if error %}
    <div class="error-message" role="alert">
      <span class="block sm:inline">{{ error }}</span>
    </div>
    
    <!-- Helpful tips for common errors -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <h4 class="text-blue-800 font-medium mb-2 flex items-center">
        <span class="material-icons mr-2 text-sm">lightbulb</span>
        Troubleshooting Tips
      </h4>
      <ul class="text-blue-700 text-sm space-y-1">
        {% if "403" in error or "Forbidden" in error %}
        <li>• Try a different YouTube video that is publicly available</li>
        <li>• Check if the video is age-restricted or region-blocked</li>
        <li>• Ensure the video is not private or unlisted</li>
        <li>• Some videos may be restricted due to copyright or content policies</li>
        {% elif "404" in error %}
        <li>• Verify the YouTube URL is correct and the video exists</li>
        <li>• Check if the video has been removed or made private</li>
        <li>• Try copying the URL directly from YouTube</li>
        {% elif "unavailable" in error.lower() %}
        <li>• The video may have been removed or made private</li>
        <li>• Try a different video that is publicly accessible</li>
        <li>• Check if the video requires authentication</li>
        {% else %}
        <li>• Ensure you're using a valid YouTube URL</li>
        <li>• Try refreshing the page and entering the URL again</li>
        <li>• Check your internet connection</li>
        <li>• Some videos may be temporarily unavailable</li>
        {% endif %}
      </ul>
    </div>
    {% endif %}

    <form action="/" method="post" class="space-y-6">
      <div class="flex items-center border-2 border-gray-200 rounded-lg px-4 py-2 focus-within:border-indigo-500 transition-all duration-300">
        <span class="material-icons text-gray-500 mr-2">link</span>
        <input type="url" name="video_url" placeholder="Enter YouTube URL" required class="custom-input" value="{{ video_url if video_url else '' }}" />
      </div>
      <button type="submit" class="custom-button custom-button-blue">
        <span class="material-icons mr-2">download</span> Fetch Formats
      </button>
    </form>

    {% if formats %}
    {% if video_title %}
    <div class="video-title">
      {{ video_title }}
    </div>
    {% endif %}
    
    <!-- Debug: Show total formats count -->
    <div class="text-sm text-gray-500 mb-4 text-center">
      Total formats available: {{ formats|length }}
    </div>
    
    <form action="/download" method="post" class="mt-8">
      <input type="hidden" name="video_url" value="{{ video_url }}">
      
      <!-- Only show Video+Audio and Audio formats -->
      <div class="format-section">
        <h3 class="format-section-title">
          <span class="material-icons mr-2">grid_view</span>
          Video + Audio Quality Variations
        </h3>
        <div class="format-grid">
          {% for f in formats|video_audio_formats %}
          <label class="format-option" onclick="selectFormat(this)">
            <input type="radio" name="format_id" value="{{ f['format_id'] }}" required>
            <div class="format-info">
              <div class="flex items-center justify-between mb-1">
                <span class="format-quality font-medium">
                  {% if f.get('height') %}{{ f.get('height') }}p{% else %}N/A{% endif %}
                  {% if f.get('format_note') %} - {{ f.get('format_note') }}{% endif %}
                </span>
                <span class="quality-badge">
                  Video+Audio
                </span>
              </div>
              <span class="format-type text-xs text-gray-600">
                {{ f['ext'] }} - {{ f.get('filesize_approx', 'N/A')|filesizeformat }}
              </span>
            </div>
          </label>
          {% endfor %}
        </div>
      </div>
      <div class="format-section">
        <h3 class="format-section-title">
          <span class="material-icons mr-2">music_note</span>
          Audio Quality Variations
        </h3>
        <div class="format-grid">
          {% for f in formats|audio_formats %}
          <label class="format-option" onclick="selectFormat(this)">
            <input type="radio" name="format_id" value="{{ f['format_id'] }}" required>
            <div class="format-info">
              <div class="flex items-center justify-between mb-1">
                <span class="format-quality font-medium">
                  {{ f.get('format_note', 'Audio') }}
                </span>
                <span class="quality-badge audio-quality">Audio</span>
              </div>
              <span class="format-type text-xs text-gray-600">
                {{ f['ext'] }} - {{ f.get('filesize_approx', 'N/A')|filesizeformat }}
              </span>
            </div>
          </label>
          {% endfor %}
        </div>
      </div>

      <button type="submit" class="custom-button custom-button-green mt-6">
        <span class="material-icons mr-2">file_download</span> Download Selected Format
      </button>
    </form>
    {% endif %}
  </div>

  <script>
    function selectFormat(label) {
      document.querySelectorAll('.format-option').forEach(opt => {
        opt.classList.remove('selected');
      });
      label.classList.add('selected');
      label.querySelector('input[type="radio"]').checked = true;
    }
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            video_url = request.form["video_url"]
            
            # Validate URL
            if not video_url or not video_url.startswith(('http://', 'https://')):
                return render_template_string(HTML_TEMPLATE, error="Please enter a valid YouTube URL")
            
            # Define extraction strategies
            extraction_strategies = [
                # Strategy 1: Full headers with aggressive retries
                {
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                    'format': 'best',
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Charset': 'utf-8',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0'
                    },
                    'extractor_retries': 5,
                    'retries': 5,
                    'fragment_retries': 5,
                    'skip_unavailable_fragments': True,
                    'ignoreerrors': False,
                    'nocheckcertificate': True,
                    'geo_bypass': True,
                    'geo_bypass_country': "US"
                },
                # Strategy 2: Mobile user agent
                {
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                    'format': 'best',
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                    },
                    'retries': 3,
                    'fragment_retries': 3,
                    'skip_unavailable_fragments': True,
                    'nocheckcertificate': True,
                },
                # Strategy 3: Firefox user agent
                {
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                    'format': 'best',
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    },
                    'retries': 3,
                    'nocheckcertificate': True,
                },
                # Strategy 4: Safari user agent
                {
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                    'format': 'best',
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                    },
                    'retries': 3,
                    'nocheckcertificate': True,
                },
                # Strategy 5: Ultra minimal approach
                {
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                    'format': 'best',
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                        'Accept': '*/*',
                    },
                    'retries': 2,
                    'nocheckcertificate': True,
                }
            ]
            
            # Try multiple extraction strategies
            info_dict = None
            last_error = None
            
            for i, strategy in enumerate(extraction_strategies):
                try:
                    print(f"Trying extraction strategy {i+1}...")
                    with yt_dlp.YoutubeDL(strategy) as ydl:
                        info_dict = ydl.extract_info(video_url, download=False)
                        if info_dict:
                            print(f"Extraction strategy {i+1} succeeded")
                            break
                except yt_dlp.utils.DownloadError as e:
                    last_error = e
                    error_str = str(e)
                    print(f"Extraction strategy {i+1} failed: {error_str}")
                    
                    # Check for specific error types
                    if "403" in error_str or "Forbidden" in error_str:
                        print(f"Strategy {i+1}: 403 Forbidden error")
                    elif "404" in error_str:
                        print(f"Strategy {i+1}: 404 Not Found error")
                    elif "Video unavailable" in error_str:
                        print(f"Strategy {i+1}: Video unavailable")
                    elif "Private video" in error_str:
                        print(f"Strategy {i+1}: Private video")
                    elif "Age-restricted" in error_str:
                        print(f"Strategy {i+1}: Age-restricted video")
                    
                    continue
                except Exception as e:
                    last_error = e
                    print(f"Extraction strategy {i+1} failed with exception: {e}")
                    continue
            
            if not info_dict:
                error_msg = str(last_error) if last_error else "Unknown error"
                
                if "403" in error_msg or "Forbidden" in error_msg:
                    return render_template_string(HTML_TEMPLATE, error="Access denied (403). This video may be restricted, age-restricted, or unavailable in your region. Try a different video or check if the video is publicly available.")
                elif "404" in error_msg:
                    return render_template_string(HTML_TEMPLATE, error="Video not found (404). Please check the URL and ensure the video is publicly available.")
                elif "Video unavailable" in error_msg:
                    return render_template_string(HTML_TEMPLATE, error="This video is unavailable. It may have been removed, made private, or is not accessible.")
                elif "Private video" in error_msg:
                    return render_template_string(HTML_TEMPLATE, error="This is a private video and cannot be downloaded.")
                elif "Age-restricted" in error_msg:
                    return render_template_string(HTML_TEMPLATE, error="This video is age-restricted and cannot be downloaded without authentication.")
                elif "Sign in" in error_msg or "login" in error_msg.lower():
                    return render_template_string(HTML_TEMPLATE, error="This video requires authentication. Please try a different publicly available video.")
                else:
                    return render_template_string(HTML_TEMPLATE, error=f"Could not fetch video information. The video may be restricted or unavailable. Error: {error_msg}")
            
            formats = info_dict.get("formats", [])
            if not formats:
                return render_template_string(HTML_TEMPLATE, error="No formats available for this video.")
            
            # Filter out formats without format_id and ensure we have valid formats
            formats = [f for f in formats if f.get('format_id')]
            
            # Only keep Video+Audio and Audio-only formats
            video_audio_formats = []
            audio_formats = []
            for f in formats:
                vcodec = f.get('vcodec', 'none')
                acodec = f.get('acodec', 'none')
                # Video+Audio: both codecs present and not 'none'
                if vcodec != 'none' and acodec != 'none':
                    video_audio_formats.append(f)
                # Audio only: vcodec is 'none', acodec is not 'none'
                elif vcodec == 'none' and acodec != 'none':
                    audio_formats.append(f)
            # Merge for template context
            formats = video_audio_formats + audio_formats
            # Sort: Video+Audio by height, Audio by abr
            video_audio_formats.sort(key=lambda x: (x.get('height', 0) or 0, x.get('filesize_approx', 0) or 0), reverse=True)
            audio_formats.sort(key=lambda x: (x.get('abr', 0) or 0, x.get('filesize_approx', 0) or 0), reverse=True)
            
            # Debug: Print format count and details
            print(f"Total formats found: {len(formats)}")
            print("Sample formats:")
            for f in formats[:20]:  # Print first 20 formats for debugging
                print(f"Format: {f.get('format_id')} - {f.get('height')}p - {f.get('ext')} - vcodec: {f.get('vcodec')} - acodec: {f.get('acodec')} - note: {f.get('format_note', 'N/A')}")
            
            return render_template_string(HTML_TEMPLATE,
                                        formats=formats,
                                        video_url=video_url,
                                        video_title=info_dict.get('title', 'Unknown Title'),
                                        video_audio_formats=video_audio_formats,
                                        audio_formats=audio_formats)
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error=f"An error occurred: {str(e)}")
    return render_template_string(HTML_TEMPLATE)

@app.route("/download", methods=["POST"])
def download():
    try:
        video_url = request.form["video_url"]
        format_id = request.form["format_id"]
        
        # Validate inputs
        if not all([video_url, format_id]):
            return "Missing required parameters", 400
        
        # Use temporary directory for deployed platforms
        temp_dir = tempfile.mkdtemp()
        
        # Define download strategies with more aggressive configurations
        download_strategies = [
            # Strategy 1: Full headers with aggressive retries
            {
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "format": format_id,
                "quiet": False,
                "no_warnings": False,
                "http_headers": {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Charset': 'utf-8',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                },
                "extractor_retries": 5,
                "retries": 5,
                "fragment_retries": 5,
                "skip_unavailable_fragments": True,
                "ignoreerrors": False,
                "nocheckcertificate": True,
                "geo_bypass": True,
                "geo_bypass_country": "US"
            },
            # Strategy 2: Mobile user agent
            {
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "format": format_id,
                "quiet": False,
                "no_warnings": False,
                "http_headers": {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                },
                "retries": 3,
                "fragment_retries": 3,
                "skip_unavailable_fragments": True,
                "nocheckcertificate": True,
            },
            # Strategy 3: Firefox user agent
            {
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "format": format_id,
                "quiet": False,
                "no_warnings": False,
                "http_headers": {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                "retries": 3,
                "nocheckcertificate": True,
            },
            # Strategy 4: Safari user agent
            {
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "format": format_id,
                "quiet": False,
                "no_warnings": False,
                "http_headers": {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                },
                "retries": 3,
                "nocheckcertificate": True,
            },
            # Strategy 5: Edge user agent
            {
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "format": format_id,
                "quiet": False,
                "no_warnings": False,
                "http_headers": {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                },
                "retries": 3,
                "nocheckcertificate": True,
            },
            # Strategy 6: Fallback to best format with simple headers
            {
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "format": "best",
                "quiet": False,
                "no_warnings": False,
                "http_headers": {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                },
                "retries": 3,
                "nocheckcertificate": True,
            },
            # Strategy 7: Ultra minimal approach
            {
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "format": "best[height<=720]",
                "quiet": False,
                "no_warnings": False,
                "http_headers": {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'Accept': '*/*',
                },
                "retries": 2,
                "nocheckcertificate": True,
            }
        ]
        
        # Try multiple download strategies
        download_success = False
        last_error = None
        
        for i, strategy in enumerate(download_strategies):
            try:
                print(f"Trying download strategy {i+1}...")
                with yt_dlp.YoutubeDL(strategy) as ydl:
                    # First extract info to get filename
                    info_dict = ydl.extract_info(video_url, download=False)
                    if not info_dict:
                        print(f"Strategy {i+1}: Could not extract info")
                        continue
                    
                    # Try to download the video
                    ydl.download([video_url])
                    
                    # Find the downloaded file
                    video_file = ydl.prepare_filename(info_dict)
                    if not os.path.exists(video_file):
                        # Try to find the file in temp directory
                        files = os.listdir(temp_dir)
                        if files:
                            video_file = os.path.join(temp_dir, files[0])
                        else:
                            print(f"Strategy {i+1}: No file found after download")
                            continue
                    
                    # Get filename for download
                    filename = os.path.basename(video_file)
                    
                    # Send file and clean up
                    try:
                        response = send_file(
                            video_file, 
                            as_attachment=True,
                            download_name=filename,
                            mimetype='application/octet-stream'
                        )
                        download_success = True
                        return response
                    finally:
                        # Clean up temporary file
                        try:
                            os.remove(video_file)
                            os.rmdir(temp_dir)
                        except:
                            pass
                            
            except yt_dlp.utils.DownloadError as e:
                last_error = e
                error_str = str(e)
                print(f"Strategy {i+1} failed: {error_str}")
                
                # Check for specific error types
                if "403" in error_str or "Forbidden" in error_str:
                    print(f"Strategy {i+1}: 403 Forbidden error")
                elif "404" in error_str:
                    print(f"Strategy {i+1}: 404 Not Found error")
                elif "Video unavailable" in error_str:
                    print(f"Strategy {i+1}: Video unavailable")
                elif "Private video" in error_str:
                    print(f"Strategy {i+1}: Private video")
                elif "Age-restricted" in error_str:
                    print(f"Strategy {i+1}: Age-restricted video")
                
                continue
            except Exception as e:
                last_error = e
                print(f"Strategy {i+1} failed with exception: {e}")
                continue
        
        # If all strategies failed, provide specific error messages
        if not download_success:
            error_msg = str(last_error) if last_error else "Unknown error"
            
            if "403" in error_msg or "Forbidden" in error_msg:
                return "Access denied (403). This video may be restricted, age-restricted, or unavailable in your region. Try a different video or check if the video is publicly available.", 403
            elif "404" in error_msg:
                return "Video not found (404). Please check the URL and ensure the video is publicly available.", 404
            elif "Video unavailable" in error_msg:
                return "This video is unavailable. It may have been removed, made private, or is not accessible.", 400
            elif "Private video" in error_msg:
                return "This is a private video and cannot be downloaded.", 400
            elif "Age-restricted" in error_msg:
                return "This video is age-restricted and cannot be downloaded without authentication.", 400
            elif "Sign in" in error_msg or "login" in error_msg.lower():
                return "This video requires authentication. Please try a different publicly available video.", 400
            else:
                return f"All download strategies failed. The video may be restricted or unavailable. Last error: {error_msg}", 500
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

# Add a custom filter for file size formatting
@app.template_filter('filesizeformat')
def filesizeformat(value):
    if value == 'N/A':
        return value
    try:
        value = float(value)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if value < 1024:
                return f"{value:.1f} {unit}"
            value /= 1024
        return f"{value:.1f} TB"
    except:
        return 'N/A'

# Add a custom filter for safe height comparison
@app.template_filter('has_height')
def has_height(format_dict, min_height=None, max_height=None):
    height = format_dict.get('height')
    
    # If no height filter is specified, include all formats with any height
    if min_height is None and max_height is None:
        return height is not None
    
    # If height is None, exclude it
    if height is None:
        return False
    
    # Check min height
    if min_height is not None and height < min_height:
        return False
    
    # Check max height
    if max_height is not None and height >= max_height:
        return False
    
    return True

# Add a custom filter to get video formats with height
@app.template_filter('video_formats_with_height')
def video_formats_with_height(formats, min_height=None, max_height=None):
    filtered_formats = []
    for f in formats:
        # Check if it's a video format (has video codec)
        if f.get('vcodec', 'none') != 'none':
            height = f.get('height')
            
            # For lower qualities (min_height is None), include formats with any height below max_height
            if min_height is None and max_height is not None:
                if height is not None and height < max_height:
                    filtered_formats.append(f)
            # For specific height ranges (like 1080p: 1080 <= height < 2160)
            elif min_height is not None and max_height is not None:
                if height is not None and min_height <= height < max_height:
                    filtered_formats.append(f)
            # For 4K and above (only min_height specified)
            elif min_height is not None and max_height is None:
                if height is not None and height >= min_height:
                    filtered_formats.append(f)
            # If no height filter, include all video formats with height
            else:
                if height is not None:
                    filtered_formats.append(f)
    
    # Sort by height for better organization
    filtered_formats.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
    return filtered_formats

# Add a custom filter to get audio formats
@app.template_filter('audio_formats')
def audio_formats(formats):
    audio_formats_list = []
    for f in formats:
        # Audio-only formats (no video codec, but has audio codec)
        if f.get('vcodec', 'none') == 'none' and f.get('acodec', 'none') != 'none':
            audio_formats_list.append(f)
        # Also include formats with both video and audio but marked as audio
        elif f.get('format_note', '').lower().find('audio') != -1:
            audio_formats_list.append(f)
        # Include formats with audio codec and no video codec
        elif f.get('acodec', 'none') != 'none' and f.get('vcodec', 'none') == 'none':
            audio_formats_list.append(f)
    return audio_formats_list

# Add a filter to get all video formats (for debugging)
@app.template_filter('all_video_formats')
def all_video_formats(formats):
    return [f for f in formats if f.get('vcodec', 'none') != 'none']

# Add a filter to get formats by quality range
@app.template_filter('formats_by_quality')
def formats_by_quality(formats, quality_range):
    quality_ranges = {
        '4k': (2160, None),
        '1080p': (1080, 2160),
        '720p': (720, 1080),
        '480p': (480, 720),
        '360p': (360, 480),
        '240p': (240, 360),
        '144p': (144, 240)
    }
    
    if quality_range not in quality_ranges:
        return []
    
    min_height, max_height = quality_ranges[quality_range]
    return video_formats_with_height(formats, min_height, max_height)

# Add a custom filter to get only Video+Audio formats
@app.template_filter('video_audio_formats')
def video_audio_formats(formats):
    return [f for f in formats if f.get('vcodec', 'none') != 'none' and f.get('acodec', 'none') != 'none']

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))