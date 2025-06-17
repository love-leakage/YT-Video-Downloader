from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Seal YouTube Downloader</title>
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
    }
    
    .container {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .custom-input {
      @apply w-full outline-none bg-transparent;
      transition: all 0.3s ease;
    }
    
    .custom-input:focus {
      @apply border-indigo-500;
    }
    
    .custom-button {
      @apply w-full py-3 rounded-lg flex items-center justify-center transition-all duration-300 transform;
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
      @apply grid grid-cols-1 md:grid-cols-2 gap-3;
    }
    
    .format-option {
      @apply flex items-center bg-gray-50 rounded-lg p-4 shadow-sm transition-all duration-300 cursor-pointer;
      border: 2px solid transparent;
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
      @apply flex flex-col;
    }
    
    .format-quality {
      @apply text-sm font-medium text-gray-600;
    }
    
    .format-type {
      @apply text-xs text-gray-500;
    }
    
    .title-container {
      @apply flex justify-center items-center mb-8;
    }
    
    .title-icon {
      @apply text-6xl text-indigo-500;
    }
    
    .title-text {
      @apply text-3xl font-bold text-gray-800 ml-3;
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
      @apply text-xl font-semibold text-gray-800 mb-4 text-center;
    }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
  <div class="container p-8 rounded-3xl shadow-2xl w-full max-w-4xl">
    <div class="title-container">
      <span class="material-icons title-icon">cloud_download</span>
      <h2 class="title-text">Seal Downloader</h2>
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
        {% set has_4k = formats|selectattr('height', '>=', 2160)|list %}
        {% if has_4k %}
        <div class="mb-4">
          <h4 class="text-sm font-medium text-gray-600 mb-2">4K Quality</h4>
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
        {% set has_1080p = formats|selectattr('height', '>=', 1080)|selectattr('height', '<', 2160)|list %}
        {% if has_1080p %}
        <div class="mb-4">
          <h4 class="text-sm font-medium text-gray-600 mb-2">Full HD</h4>
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
        {% set has_720p = formats|selectattr('height', '>=', 720)|selectattr('height', '<', 1080)|list %}
        {% if has_720p %}
        <div class="mb-4">
          <h4 class="text-sm font-medium text-gray-600 mb-2">HD</h4>
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
        {% set lower_qualities = formats|selectattr('height', '<', 720)|selectattr('vcodec', '!=', 'none')|list %}
        {% if lower_qualities %}
        <div class="mb-4">
          <h4 class="text-sm font-medium text-gray-600 mb-2">Standard Quality</h4>
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
          {% for f in formats %}
            {% if f.get('vcodec', 'none') == 'none' and f.get('acodec', 'none') != 'none' %}
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
            {% endif %}
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
                    info_dict = ydl.extract_info(video_url, download=False)
                    if not info_dict:
                        return render_template_string(HTML_TEMPLATE, error="Could not fetch video information. Please check the URL.")
                    
                    formats = info_dict.get("formats", [])
                    if not formats:
                        return render_template_string(HTML_TEMPLATE, error="No formats available for this video.")
                    
                    # Sort formats by quality
                    formats.sort(key=lambda x: (
                        x.get('height', 0) or 0,
                        x.get('filesize_approx', 0) or 0
                    ), reverse=True)
                    
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
        
        # Create the directory if it doesn't exist
        try:
            os.makedirs(save_path, exist_ok=True)
        except Exception as e:
            return f"Error creating directory: {str(e)}", 500
        
        ydl_opts = {
            "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
            "format": format_id,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(video_url, download=True)
                if not info_dict:
                    return "Could not fetch video information", 400
                
                video_file = ydl.prepare_filename(info_dict)
                if not os.path.exists(video_file):
                    return "Download failed", 500
                
                return send_file(video_file, as_attachment=True)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))