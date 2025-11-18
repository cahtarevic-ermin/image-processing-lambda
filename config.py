"""
Configuration settings for image processing Lambda
"""
import os
from dotenv import load_dotenv

load_dotenv()

# S3 Configuration
DESTINATION_BUCKET = os.environ.get('DESTINATION_BUCKET', 'my-processed-images')
SOURCE_BUCKET = os.environ.get('SOURCE_BUCKET', 'my-uploaded-images')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')

# Image Processing Settings
TARGET_ASPECT_RATIO = (4, 3)
WATERMARK_OPACITY = 0.3
WATERMARK_POSITION = 'center'  # Options: center, bottom-right, bottom-left, top-right, top-left
WATERMARK_MARGIN = 20

# Output Settings
OUTPUT_FORMAT = 'JPEG'
OUTPUT_QUALITY = 90

# Notification Settings
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
ENABLE_NOTIFICATIONS = os.environ.get('ENABLE_NOTIFICATIONS', 'false').lower() == 'true'

# Logging
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
