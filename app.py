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
    {% endif %}

    <form action="/" method="post" class="space-y-6">
      <div class="flex items-center border-2 border-gray-200 rounded-lg px-4 py-2 focus-within:border-indigo-500 transition-all duration-300">
        <span class="material-icons text-gray-500 mr-2">link</span>
        <input type="url" name="video_url" placeholder="Enter YouTube URL" required class="custom-input" value="{{ video_url if video_url else '' }}" />
      </div>
      <div class="folder-input-group">
        <div class="flex items-center border-2 border-gray-200 rounded-lg px-4 py-2 focus-within:border-indigo-500 transition-all duration-300">
          <span class="material-icons text-gray-500 mr-2">folder</span>
          <input type="text" name="save_path" id="save_path" placeholder="Select Download Location" value="{{ save_path if save_path else 'downloads' }}" required class="custom-input" readonly />
          <button type="button" class="folder-button" onclick="selectFolder()">
            <span class="material-icons">folder_open</span>
          </button>
        </div>
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
      <input type="hidden" name="save_path" id="download_path" value="{{ save_path }}">
      
      <!-- Video Formats -->
      <div class="format-section">
        <h3 class="format-section-title">
          <span class="material-icons mr-2">videocam</span>
          Video Formats
        </h3>
        
        <!-- 4K Quality -->
        {% set has_4k = formats|video_formats_with_height(2160, None)|list %}
        {% if has_4k %}
        <div class="mb-4">
          <h4 class="text-sm font-medium text-gray-600 mb-2">4K Quality ({{ has_4k|length }} formats)</h4>
          <div class="format-grid">
            {% for f in has_4k %}
            <label class="format-option" onclick="selectFormat(this)">
              <input type="radio" name="format_id" value="{{ f['format_id'] }}" required>
              <div class="format-info">
                <div class="flex items-center justify-between">
                  <span class="format-quality">{{ f.get('height', 'N/A') }}p</span>
                  <span class="quality-badge quality-4k">4K</span>
                </div>
                <span class="format-type">{{ f['ext'] }} - {{ f.get('filesize_approx', 'N/A')|filesizeformat }}</span>
              </div>
            </label>
            {% endfor %}
          </div>
        </div>
        {% endif %}

        <!-- 1080p Quality -->
        {% set has_1080p = formats|video_formats_with_height(1080, 2160)|list %}
        {% if has_1080p %}
        <div class="mb-4">
          <h4 class="text-sm font-medium text-gray-600 mb-2">Full HD ({{ has_1080p|length }} formats)</h4>
          <div class="format-grid">
            {% for f in has_1080p %}
            <label class="format-option" onclick="selectFormat(this)">
              <input type="radio" name="format_id" value="{{ f['format_id'] }}" required>
              <div class="format-info">
                <div class="flex items-center justify-between">
                  <span class="format-quality">{{ f.get('height', 'N/A') }}p</span>
                  <span class="quality-badge quality-1080p">1080p</span>
                </div>
                <span class="format-type">{{ f['ext'] }} - {{ f.get('filesize_approx', 'N/A')|filesizeformat }}</span>
              </div>
            </label>
            {% endfor %}
          </div>
        </div>
        {% endif %}

        <!-- 720p Quality -->
        {% set has_720p = formats|video_formats_with_height(720, 1080)|list %}
        {% if has_720p %}
        <div class="mb-4">
          <h4 class="text-sm font-medium text-gray-600 mb-2">HD ({{ has_720p|length }} formats)</h4>
          <div class="format-grid">
            {% for f in has_720p %}
            <label class="format-option" onclick="selectFormat(this)">
              <input type="radio" name="format_id" value="{{ f['format_id'] }}" required>
              <div class="format-info">
                <div class="flex items-center justify-between">
                  <span class="format-quality">{{ f.get('height', 'N/A') }}p</span>
                  <span class="quality-badge quality-720p">720p</span>
                </div>
                <span class="format-type">{{ f['ext'] }} - {{ f.get('filesize_approx', 'N/A')|filesizeformat }}</span>
              </div>
            </label>
            {% endfor %}
          </div>
        </div>
        {% endif %}

        <!-- Lower Qualities -->
        {% set lower_qualities = formats|video_formats_with_height(None, 720)|list %}
        {% if lower_qualities %}
        <div class="mb-4">
          <h4 class="text-sm font-medium text-gray-600 mb-2">Standard Quality ({{ lower_qualities|length }} formats)</h4>
          <div class="format-grid">
            {% for f in lower_qualities %}
            <label class="format-option" onclick="selectFormat(this)">
              <input type="radio" name="format_id" value="{{ f['format_id'] }}" required>
              <div class="format-info">
                <div class="flex items-center justify-between">
                  <span class="format-quality">{{ f.get('height', 'N/A') }}p</span>
                  <span class="quality-badge quality-{{ f.get('height', 0) }}p">{{ f.get('height', 'N/A') }}p</span>
                </div>
                <span class="format-type">{{ f['ext'] }} - {{ f.get('filesize_approx', 'N/A')|filesizeformat }}</span>
              </div>
            </label>
            {% endfor %}
          </div>
        </div>
        {% endif %}
      </div>

      <!-- Audio Formats -->
      <div class="format-section">
        <h3 class="format-section-title">
          <span class="material-icons mr-2">audiotrack</span>
          Audio Formats
        </h3>
        <div class="format-grid">
          {% for f in formats|audio_formats %}
          <label class="format-option" onclick="selectFormat(this)">
            <input type="radio" name="format_id" value="{{ f['format_id'] }}" required>
            <div class="format-info">
              <div class="flex items-center justify-between">
                <span class="format-quality">{{ f.get('format_note', '') }}</span>
                <span class="quality-badge audio-quality">Audio</span>
              </div>
              <span class="format-type">{{ f['ext'] }} - {{ f.get('filesize_approx', 'N/A')|filesizeformat }}</span>
            </div>
          </label>
          {% endfor %}
        </div>
      </div>

      <!-- Debug: Show all formats if no formats are displayed -->
      {% set total_displayed = (has_4k|length) + (has_1080p|length) + (has_720p|length) + (lower_qualities|length) + (formats|audio_formats|length) %}
      {% if total_displayed == 0 %}
      <div class="format-section">
        <h3 class="format-section-title">
          <span class="material-icons mr-2">bug_report</span>
          All Available Formats (Debug)
        </h3>
        <div class="format-grid">
          {% for f in formats %}
          <label class="format-option" onclick="selectFormat(this)">
            <input type="radio" name="format_id" value="{{ f['format_id'] }}" required>
            <div class="format-info">
              <div class="flex items-center justify-between">
                <span class="format-quality">{{ f.get('height', 'N/A') }}p - {{ f.get('format_note', '') }}</span>
                <span class="quality-badge audio-quality">{{ f.get('vcodec', 'none') }}/{{ f.get('acodec', 'none') }}</span>
              </div>
              <span class="format-type">{{ f['ext'] }} - {{ f.get('filesize_approx', 'N/A')|filesizeformat }}</span>
            </div>
          </label>
          {% endfor %}
        </div>
      </div>
      {% endif %}

      <!-- Alternative: Show all formats in a simple list -->
      {% if total_displayed < 3 %}
      <div class="format-section">
        <h3 class="format-section-title">
          <span class="material-icons mr-2">list</span>
          All Available Formats
        </h3>
        <div class="format-grid">
          {% for f in formats %}
          <label class="format-option" onclick="selectFormat(this)">
            <input type="radio" name="format_id" value="{{ f['format_id'] }}" required>
            <div class="format-info">
              <div class="flex items-center justify-between">
                <span class="format-quality">{{ f.get('height', 'N/A') }}p - {{ f.get('format_note', '') }}</span>
                <span class="quality-badge {% if f.get('vcodec', 'none') != 'none' %}quality-{{ f.get('height', 0) }}p{% else %}audio-quality{% endif %}">
                  {% if f.get('vcodec', 'none') != 'none' %}{{ f.get('height', 'N/A') }}p{% else %}Audio{% endif %}
                </span>
              </div>
              <span class="format-type">{{ f['ext'] }} - {{ f.get('filesize_approx', 'N/A')|filesizeformat }}</span>
            </div>
          </label>
          {% endfor %}
        </div>
      </div>
      {% endif %}

      <!-- Comprehensive Format Display -->
      <div class="format-section">
        <h3 class="format-section-title">
          <span class="material-icons mr-2">grid_view</span>
          All Formats ({{ formats|length }} available)
        </h3>
        <div class="format-grid">
          {% for f in formats %}
          <label class="format-option" onclick="selectFormat(this)">
            <input type="radio" name="format_id" value="{{ f['format_id'] }}" required>
            <div class="format-info">
              <div class="flex items-center justify-between">
                <span class="format-quality">
                  {% if f.get('height') %}{{ f.get('height') }}p{% else %}N/A{% endif %} 
                  {% if f.get('format_note') %}- {{ f.get('format_note') }}{% endif %}
                </span>
                <span class="quality-badge {% if f.get('vcodec', 'none') != 'none' %}quality-{{ f.get('height', 0) }}p{% else %}audio-quality{% endif %}">
                  {% if f.get('vcodec', 'none') != 'none' %}
                    {% if f.get('height', 0) >= 2160 %}4K
                    {% elif f.get('height', 0) >= 1080 %}1080p
                    {% elif f.get('height', 0) >= 720 %}720p
                    {% elif f.get('height', 0) >= 480 %}480p
                    {% elif f.get('height', 0) >= 360 %}360p
                    {% elif f.get('height', 0) >= 240 %}240p
                    {% else %}{{ f.get('height', 'N/A') }}p{% endif %}
                  {% else %}Audio{% endif %}
                </span>
              </div>
              <span class="format-type">
                {{ f['ext'] }} - {{ f.get('filesize_approx', 'N/A')|filesizeformat }}
                {% if f.get('vcodec', 'none') != 'none' and f.get('acodec', 'none') != 'none' %} (Video+Audio){% endif %}
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

    function selectFolder() {
      // Create a temporary input element
      const input = document.createElement('input');
      input.type = 'file';
      input.webkitdirectory = true;
      input.directory = true;
      
      input.onchange = function(e) {
        if (e.target.files.length > 0) {
          const path = e.target.files[0].path;
          document.getElementById('save_path').value = path;
          document.getElementById('download_path').value = path;
        }
      };
      
      input.click();
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
            save_path = request.form["save_path"]
            
            # Validate URL
            if not video_url or not video_url.startswith(('http://', 'https://')):
                return render_template_string(HTML_TEMPLATE, error="Please enter a valid YouTube URL")
            
            with yt_dlp.YoutubeDL() as ydl:
                try:
                    # Configure yt-dlp to get all available formats with proper headers
                    ydl.params.update({
                        'quiet': False,
                        'no_warnings': False,
                        'extract_flat': False,
                        'format': 'best',
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                            'Accept-Encoding': 'gzip,deflate',
                            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                            'Keep-Alive': '115',
                            'Connection': 'keep-alive',
                        }
                    })
                    
                    info_dict = ydl.extract_info(video_url, download=False)
                    if not info_dict:
                        return render_template_string(HTML_TEMPLATE, error="Could not fetch video information. Please check the URL.")
                    
                    formats = info_dict.get("formats", [])
                    if not formats:
                        return render_template_string(HTML_TEMPLATE, error="No formats available for this video.")
                    
                    # Filter out formats without format_id and ensure we have valid formats
                    formats = [f for f in formats if f.get('format_id')]
                    
                    # Include all formats that have either video or audio codec
                    valid_formats = []
                    for f in formats:
                        vcodec = f.get('vcodec', 'none')
                        acodec = f.get('acodec', 'none')
                        
                        # Include if it has video codec (not 'none')
                        if vcodec != 'none':
                            valid_formats.append(f)
                        # Include if it has audio codec (not 'none') and no video
                        elif acodec != 'none':
                            valid_formats.append(f)
                        # Include if it has format_note indicating it's a valid format
                        elif f.get('format_note'):
                            valid_formats.append(f)
                    
                    formats = valid_formats
                    
                    # Sort formats by quality (height first, then filesize)
                    formats.sort(key=lambda x: (
                        x.get('height', 0) or 0,
                        x.get('filesize_approx', 0) or 0
                    ), reverse=True)
                    
                    # Debug: Print format count and details
                    print(f"Total formats found: {len(formats)}")
                    print("Sample formats:")
                    for f in formats[:20]:  # Print first 20 formats for debugging
                        print(f"Format: {f.get('format_id')} - {f.get('height')}p - {f.get('ext')} - vcodec: {f.get('vcodec')} - acodec: {f.get('acodec')} - note: {f.get('format_note', 'N/A')}")
                    
                    return render_template_string(HTML_TEMPLATE, 
                                                formats=formats, 
                                                video_url=video_url, 
                                                save_path=save_path,
                                                video_title=info_dict.get('title', 'Unknown Title'))
                except yt_dlp.utils.DownloadError as e:
                    return render_template_string(HTML_TEMPLATE, error=f"Error: {str(e)}")
                except Exception as e:
                    return render_template_string(HTML_TEMPLATE, error=f"An error occurred: {str(e)}")
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error=f"An error occurred: {str(e)}")
    return render_template_string(HTML_TEMPLATE)

@app.route("/download", methods=["POST"])
def download():
    try:
        video_url = request.form["video_url"]
        save_path = request.form["save_path"]
        format_id = request.form["format_id"]
        
        # Validate inputs
        if not all([video_url, save_path, format_id]):
            return "Missing required parameters", 400
        
        # Use temporary directory for deployed platforms
        temp_dir = tempfile.mkdtemp()
        
        ydl_opts = {
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "format": format_id,
            "quiet": False,
            "no_warnings": False,
            "http_headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': '115',
                'Connection': 'keep-alive',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # First extract info to get filename
                info_dict = ydl.extract_info(video_url, download=False)
                if not info_dict:
                    return "Could not fetch video information", 400
                
                # Download the video
                ydl.download([video_url])
                
                # Find the downloaded file
                video_file = ydl.prepare_filename(info_dict)
                if not os.path.exists(video_file):
                    # Try to find the file in temp directory
                    files = os.listdir(temp_dir)
                    if files:
                        video_file = os.path.join(temp_dir, files[0])
                    else:
                        return "Download failed - file not found", 500
                
                # Get filename for download
                filename = os.path.basename(video_file)
                
                # Send file and clean up
                try:
                    return send_file(
                        video_file, 
                        as_attachment=True,
                        download_name=filename,
                        mimetype='application/octet-stream'
                    )
                finally:
                    # Clean up temporary file
                    try:
                        os.remove(video_file)
                        os.rmdir(temp_dir)
                    except:
                        pass
                        
            except yt_dlp.utils.DownloadError as e:
                return f"Download error: {str(e)}", 500
            except Exception as e:
                return f"An error occurred: {str(e)}", 500
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
    return audio_formats_list

# Add a filter to get all video formats (for debugging)
@app.template_filter('all_video_formats')
def all_video_formats(formats):
    return [f for f in formats if f.get('vcodec', 'none') != 'none']

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))