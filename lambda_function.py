import json
import boto3
import os
from datetime import datetime, timezone
from image_processor import ImageProcessor
import config
import requests

# Initialize AWS clients
s3_client = boto3.client('s3')

# Initialize image processor
# Note: watermark.png should be packaged with the Lambda deployment
WATERMARK_PATH = '/tmp/watermark.png'  # Will be copied here during deployment
processor = ImageProcessor(WATERMARK_PATH)

def lambda_handler(event, context):
    """
    Main Lambda handler for S3 trigger events
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse S3 event
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        print(f"Processing image: s3://{bucket_name}/{object_key}")
        
        # Download image from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        image_bytes = response['Body'].read()
        print(f"Downloaded image, size: {len(image_bytes)} bytes")
        
        # Process image
        processed_bytes = processor.process_image(
            image_bytes=image_bytes,
            target_ratio=config.TARGET_ASPECT_RATIO,
            watermark_opacity=config.WATERMARK_OPACITY
        )
        print(f"Processed image, new size: {len(processed_bytes)} bytes")
        
        # Generate output key (store in 'processed/' folder)
        filename = os.path.basename(object_key)
        name_without_ext = os.path.splitext(filename)[0]
        output_key = f"processed/{name_without_ext}_processed.jpg"
        
        # Upload processed image to destination bucket
        s3_client.put_object(
            Bucket=config.DESTINATION_BUCKET,
            Key=output_key,
            Body=processed_bytes,
            ContentType='image/jpeg',
            Metadata={
                'original-key': object_key,
                'processed-date': datetime.now(timezone.utc).isoformat()
            }
        )
        print(f"Uploaded to: s3://{config.DESTINATION_BUCKET}/{output_key}")
        
        # Send notification
        if config.ENABLE_NOTIFICATIONS and config.DISCORD_WEBHOOK_URL:
            send_notification_to_discord(bucket_name, object_key, output_key)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image processed successfully',
                'original': f's3://{bucket_name}/{object_key}',
                'processed': f's3://{config.DESTINATION_BUCKET}/{output_key}'
            })
        }
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        # Log error but don't fail completely
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing image',
                'error': str(e)
            })
        }

def send_notification_to_discord(source_bucket: str, source_key: str, output_key: str):
    """Send Discord notification about processed image"""
    try:
        message = f"""
					Image Processing Complete!

					Original Image: s3://{source_bucket}/{source_key}
					Processed Image: s3://{config.DESTINATION_BUCKET}/{output_key}
					Processing Date: {datetime.now(timezone.utc).isoformat()}

					The image has been:
					- Adjusted to 4:3 aspect ratio
					- Watermarked with logo
					- Saved to the processed bucket
					"""
        
        requests.post(config.DISCORD_WEBHOOK_URL, json={
            'content': message
        })
        print("Notification sent successfully")
    except Exception as e:
        print(f"Failed to send notification: {e}")