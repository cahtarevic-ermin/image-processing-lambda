#!/bin/bash

echo "Building Lambda deployment package..."

# Clean previous build
rm -rf deployment/package
rm -f deployment/lambda.zip

# Create package directory
mkdir -p deployment/package

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -t deployment/package/

# Copy source code
echo "Copying source code..."
cp lambda_function.py deployment/package/
cp image_processor.py deployment/package/
cp config.py deployment/package/
cp watermark.png deployment/package/

# Create ZIP
echo "Creating ZIP file..."
cd deployment/package
zip -r ../lambda.zip . -q
cd ../..

echo "✅ Build complete: deployment/lambda.zip"
ls -lh deployment/lambda.zip
