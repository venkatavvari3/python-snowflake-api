#!/bin/bash

# Build and deploy script for the FastAPI Snowflake application

set -e

echo "🚀 Building and deploying FastAPI Snowflake application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
pytest

# Build deployment package
echo "📦 Building deployment package..."
mkdir -p dist
rm -rf dist/*

# Copy application files
cp -r app dist/
cp requirements.txt dist/

# Install dependencies in dist folder for Lambda
cd dist
pip install -r requirements.txt -t .
cd ..

# Create deployment zip
echo "🗜️ Creating deployment package..."
cd dist
zip -r ../lambda_deployment.zip . -x "*.pyc" "__pycache__/*" "*.git*"
cd ..

echo "✅ Build complete! Deployment package: lambda_deployment.zip"

# Deploy with Terraform (optional)
if [ "$1" = "--deploy" ]; then
    echo "🚀 Deploying with Terraform..."
    cd terraform
    terraform init
    terraform plan
    terraform apply -auto-approve
    cd ..
    echo "✅ Deployment complete!"
fi

echo "🎉 Done!"
