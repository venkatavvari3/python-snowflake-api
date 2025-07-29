@echo off
REM Build and deploy script for the FastAPI Snowflake application (Windows)

echo 🚀 Building and deploying FastAPI Snowflake application...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Run tests
echo 🧪 Running tests...
pytest

REM Build deployment package
echo 📦 Building deployment package...
if not exist "dist" mkdir dist
del /Q dist\*

REM Copy application files
xcopy app dist\app\ /E /I
copy requirements.txt dist\

REM Install dependencies in dist folder for Lambda
cd dist
pip install -r requirements.txt -t .
cd ..

REM Create deployment zip using PowerShell
echo 🗜️ Creating deployment package...
powershell -Command "Compress-Archive -Path 'dist\*' -DestinationPath 'lambda_deployment.zip' -Force"

echo ✅ Build complete! Deployment package: lambda_deployment.zip

REM Deploy with Terraform (optional)
if "%1"=="--deploy" (
    echo 🚀 Deploying with Terraform...
    cd terraform
    terraform init
    terraform plan
    terraform apply -auto-approve
    cd ..
    echo ✅ Deployment complete!
)

echo 🎉 Done!
