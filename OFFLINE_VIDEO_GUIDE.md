# 🎬 Offline Video Management Guide

Complete guide for managing offline video files in your E-Learning Platform.

## Overview

The platform now supports offline video files stored on your server, giving you full control over your content without depending on YouTube or external services.

## Benefits of Offline Videos

✅ **Full Control** - Complete ownership of content  
✅ **No External Dependencies** - No YouTube account needed  
✅ **Better Security** - Videos can't be easily shared  
✅ **Custom Player** - Full control over playback  
✅ **Offline Access** - Works without internet (if cached)  
✅ **Brand Consistency** - No YouTube branding  

## Supported Video Formats

### Recommended Formats

**MP4 (H.264)**
- Best compatibility
- Works on all devices
- Good compression
- Recommended settings:
  - Codec: H.264
  - Resolution: 1080p (1920x1080)
  - Bitrate: 5-8 Mbps
  - Audio: AAC, 128-192 kbps

**WebM (VP9)**
- Modern format
- Better compression than MP4
- Good for web
- Chrome/Firefox support

**OGG (Theora)**
- Open source
- Firefox support
- Fallback option

### Format Recommendations

| Use Case | Format | Resolution | Bitrate |
|----------|--------|------------|---------|
| High Quality | MP4 | 1080p | 8 Mbps |
| Standard | MP4 | 720p | 5 Mbps |
| Mobile | MP4 | 480p | 2.5 Mbps |
| Low Bandwidth | MP4 | 360p | 1 Mbps |

## Upload Process

### Method 1: Django Admin

1. Go to Admin → Courses → Lessons
2. Create or edit a lesson
3. Click "Choose File" under Video file
4. Select your video file
5. Save

**File Size Limits:**
- Default: 100 MB per file
- Configurable in settings

### Method 2: Bulk Upload

```bash
# Copy videos to media folder
cp /path/to/videos/*.mp4 media/courses/videos/

# Update database
python manage.py shell
```

```python
from courses.models import Lesson

lesson = Lesson.objects.get(id=1)
lesson.video_file = 'courses/videos/intro.mp4'
lesson.save()
```

### Method 3: FTP/SSH

```bash
# Upload via SCP
scp video.mp4 user@server:/path/to/media/courses/videos/

# Set permissions
chmod 644 /path/to/media/courses/videos/video.mp4
```

## File Organization

### Directory Structure

```
media/
└── courses/
    ├── videos/           # Video files
    │   ├── course-1/
    │   │   ├── lesson-1.mp4
    │   │   ├── lesson-2.mp4
    │   │   └── lesson-3.mp4
    │   └── course-2/
    │       └── intro.mp4
    ├── thumbnails/       # Course images
    └── materials/        # Downloadable files
```

### Naming Convention

**Recommended:**
```
course-name_lesson-number_title.mp4

Examples:
python-basics_01_introduction.mp4
web-dev_05_css-fundamentals.mp4
```

**Avoid:**
- Special characters
- Spaces (use hyphens or underscores)
- Very long names

## Video Preparation

### Converting Videos

**Using FFmpeg:**

```bash
# Convert to MP4 (H.264)
ffmpeg -i input.avi -c:v libx264 -c:a aac -strict experimental output.mp4

# Compress large video
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a aac -b:a 128k output.mp4

# Change resolution to 720p
ffmpeg -i input.mp4 -vf scale=1280:720 -c:v libx264 -crf 23 output.mp4

# Create WebM version
ffmpeg -i input.mp4 -c:v libvpx-vp9 -c:a libopus output.webm
```

### Optimization

**Reduce File Size:**
```bash
# Good quality, smaller file
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -crf 28 \
  -preset slow \
  -c:a aac \
  -b:a 128k \
  output.mp4
```

**Create Multiple Qualities:**
```bash
# 1080p
ffmpeg -i source.mp4 -vf scale=1920:1080 -c:v libx264 -crf 23 1080p.mp4

# 720p
ffmpeg -i source.mp4 -vf scale=1280:720 -c:v libx264 -crf 23 720p.mp4

# 480p
ffmpeg -i source.mp4 -vf scale=854:480 -c:v libx264 -crf 23 480p.mp4
```

## Storage Management

### File Size Limits

**Configure in settings.py:**

```python
# Maximum upload size (in bytes)
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB

# For larger files
DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500 MB
```

**For nginx:**

```nginx
# /etc/nginx/nginx.conf
client_max_body_size 500M;
```

### Storage Backends

**Local Storage (Default):**
```python
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

**Amazon S3:**
```python
# Install: pip install django-storages boto3

AWS_ACCESS_KEY_ID = 'your-key'
AWS_SECRET_ACCESS_KEY = 'your-secret'
AWS_STORAGE_BUCKET_NAME = 'your-bucket'
AWS_S3_REGION_NAME = 'us-east-1'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

**Azure Blob Storage:**
```python
# Install: pip install django-storages[azure]

AZURE_ACCOUNT_NAME = 'your-account'
AZURE_ACCOUNT_KEY = 'your-key'
AZURE_CONTAINER = 'media'

DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
```

## Video Protection

### Security Features

The platform includes:

✅ **Watermark** - User email overlay  
✅ **No Download** - controlsList="nodownload"  
✅ **No Right-Click** - Disabled  
✅ **No PiP** - Picture-in-picture disabled  
✅ **Auto-Pause** - On tab switch  
✅ **Hotlink Protection** - Coming soon  

### Additional Protection

**Server-side (nginx):**

```nginx
location /media/courses/videos/ {
    # Require authentication
    auth_request /auth;
    
    # Disable directory listing
    autoindex off;
    
    # Prevent hotlinking
    valid_referers none blocked yourdomain.com *.yourdomain.com;
    if ($invalid_referer) {
        return 403;
    }
}
```

**Django Middleware:**

```python
# Check if user is enrolled before serving video
def serve_protected_video(request, path):
    # Verify enrollment
    # Serve video if authorized
    pass
```

## Performance Optimization

### CDN Integration

**Cloudflare:**
```
1. Add domain to Cloudflare
2. Enable video caching
3. Set long cache times for videos
```

**AWS CloudFront:**
```python
AWS_S3_CUSTOM_DOMAIN = 'd123456.cloudfront.net'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
```

### Video Compression

**Target Sizes:**
- 5-minute 1080p video: ~200-300 MB
- 5-minute 720p video: ~100-150 MB
- 5-minute 480p video: ~50-75 MB

**Compression Tools:**
- HandBrake (GUI)
- FFmpeg (CLI)
- Adobe Media Encoder
- Online: cloudconvert.com

### Streaming

**HLS (HTTP Live Streaming):**

```bash
# Convert to HLS
ffmpeg -i input.mp4 \
  -codec: copy \
  -start_number 0 \
  -hls_time 10 \
  -hls_list_size 0 \
  -f hls \
  output.m3u8
```

**DASH (Dynamic Adaptive Streaming):**

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -c:a aac \
  -b:v:0 800k \
  -s:v:0 640x360 \
  -b:v:1 1200k \
  -s:v:1 1280x720 \
  -f dash \
  output.mpd
```

## Troubleshooting

### Video Not Playing

**Check:**
1. File format supported (MP4 recommended)
2. File permissions correct (644)
3. MEDIA_URL configured correctly
4. Video codec supported (H.264)
5. File not corrupted

**Test:**
```bash
# Check if file exists
ls -lh media/courses/videos/video.mp4

# Test video
ffmpeg -v error -i video.mp4 -f null -
```

### Slow Loading

**Solutions:**
1. Compress video (reduce bitrate)
2. Use CDN
3. Enable server caching
4. Optimize nginx/Apache
5. Consider adaptive streaming

### Upload Fails

**Check:**
1. File size within limits
2. Enough disk space
3. Correct permissions on media folder
4. Web server timeout settings
5. Upload form encoding

## Best Practices

### 1. Consistent Format

Use MP4 (H.264) for all videos:
- Maximum compatibility
- Good compression
- Universal support

### 2. Optimize Before Upload

- Compress videos
- Use appropriate resolution
- Remove unnecessary audio tracks
- Strip metadata

### 3. Backup Strategy

```bash
# Daily backup
rsync -av media/courses/videos/ /backup/videos/

# To S3
aws s3 sync media/courses/videos/ s3://backup-bucket/videos/
```

### 4. Monitor Storage

```bash
# Check disk usage
du -sh media/courses/videos/

# Find large files
find media/courses/videos/ -type f -size +100M
```

### 5. Test Playback

- Test on different browsers
- Test on mobile devices
- Check loading speed
- Verify audio quality

## Cost Considerations

### Storage Costs

**Local Server:**
- 1 TB SSD: ~$100-200/month
- 10 TB HDD: ~$300-500/month

**Cloud Storage:**
- S3: $0.023/GB/month
- Azure: $0.018/GB/month
- Google Cloud: $0.020/GB/month

**Example:**
- 100 courses × 10 videos × 200 MB = 200 GB
- S3 cost: ~$4.60/month

### Bandwidth Costs

**Estimate:**
- 1000 students × 10 videos × 200 MB = 2 TB transfer
- S3 transfer: ~$180/month
- CDN (Cloudflare): Free tier available

## Maintenance

### Regular Tasks

**Weekly:**
- Check disk space
- Review failed uploads
- Test random videos

**Monthly:**
- Analyze usage statistics
- Optimize storage
- Update backups
- Review costs

**Quarterly:**
- Archive old courses
- Upgrade storage if needed
- Review security

## Quick Reference

### File Upload
```python
# In admin or via code
lesson.video_file = request.FILES['video']
lesson.save()
```

### Get Video URL
```python
# In template
{{ lesson.video_file.url }}

# In view
video_url = lesson.video_file.url if lesson.video_file else None
```

### Check Video Exists
```python
if lesson.video_file:
    print(f"Video available: {lesson.video_file.path}")
```

### Delete Video
```python
if lesson.video_file:
    lesson.video_file.delete()
```

---

**Your offline video system is ready!** 🎬✅
