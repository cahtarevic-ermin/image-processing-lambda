# 🖼️ Prism - Image Processing Lambda

Automatically process uploaded images with aspect ratio correction and watermark branding.

## What It Does

When you upload an image to your S3 bucket, this system automatically:
- ✅ Fixes the aspect ratio to 4:3 (configurable)
- ✅ Adds your branded watermark
- ✅ Saves the processed image to a separate bucket
- ✅ Sends a notification to Discord (optional)

## Quick Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Settings

Copy `.env.example` to `.env` and update with your values:

```bash
DESTINATION_BUCKET=your-processed-images-bucket
SOURCE_BUCKET=your-uploaded-images-bucket
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/TOKEN
ENABLE_NOTIFICATIONS=true
```

### 3. Add Your Watermark

Place your logo as `watermark.png` in the project root (PNG with transparency recommended).

### 4. Build & Deploy

```bash
# Build deployment package
./deployment/build.sh

# Deploy with Terraform (recommended)
cd ../image-processing-infra
terraform init
terraform apply
```

## Configuration

Edit `config.py` to customize processing:

```python
TARGET_ASPECT_RATIO = (4, 3)      # Image aspect ratio
WATERMARK_OPACITY = 0.3           # 0.0 (invisible) to 1.0 (solid)
WATERMARK_POSITION = 'center'     # center, bottom-right, bottom-left, top-right, top-left
OUTPUT_QUALITY = 90               # JPEG quality (1-100)
```

## File Structure

```
├── lambda_function.py       # Main entry point
├── image_processor.py       # Processing logic
├── config.py               # Settings
├── requirements.txt        # Dependencies
├── watermark.png          # Your logo
└── deployment/
    └── build.sh           # Build script
```

## Monitoring

**View logs:**
```bash
aws logs tail /aws/lambda/image-processor --follow
```

**Check processed images:**
```bash
aws s3 ls s3://your-destination-bucket/processed/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | Activate venv: `source venv/bin/activate` |
| Lambda timeout | Increase timeout to 120s in AWS Console |
| No watermark | Verify `watermark.png` exists and is RGBA format |
| Permission errors | Check Lambda IAM role has S3 read/write access |

## Tech Stack

- **Python 3.12** - Runtime
- **Pillow** - Image processing
- **boto3** - AWS SDK
- **AWS Lambda** - Serverless compute
- **S3** - Storage
- **Terraform** - Infrastructure (see [`image-processing-infra`](https://github.com/cahtarevic-ermin/image-processing-infra))

## Support

For infrastructure setup, see the companion repository: [`image-processing-infra`](https://github.com/cahtarevic-ermin/image-processing-infra)

**Need help?** Check CloudWatch logs or open an issue.
