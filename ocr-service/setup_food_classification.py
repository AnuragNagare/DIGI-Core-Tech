#!/usr/bin/env python3
"""
Setup script for Food Classification Service
Installs dependencies and downloads required models
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and handle errors."""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("❌ Python 3.8+ is required")
        sys.exit(1)
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")

def install_dependencies():
    """Install required Python packages."""
    logger.info("Installing dependencies...")
    
    # Install PyTorch with CPU support
    torch_command = "pip install torch==2.1.0+cpu torchvision==0.16.0+cpu -f https://download.pytorch.org/whl/torch_stable.html"
    run_command(torch_command, "Installing PyTorch")
    
    # Install other requirements
    requirements_file = Path(__file__).parent / "food_requirements.txt"
    if requirements_file.exists():
        run_command(f"pip install -r {requirements_file}", "Installing food classification requirements")
    else:
        logger.warning("Requirements file not found, installing basic packages...")
        basic_packages = [
            "fastapi==0.104.1",
            "uvicorn==0.24.0", 
            "python-multipart==0.0.6",
            "Pillow==10.0.0",
            "opencv-python==4.8.0.74",
            "numpy==1.24.3",
            "requests==2.31.0",
            "python-dotenv==1.0.0"
        ]
        for package in basic_packages:
            run_command(f"pip install {package}", f"Installing {package}")

def create_environment_file():
    """Create .env file with default configuration."""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        logger.info("Creating .env file...")
        env_content = """# Food Classification Service Configuration
FOOD_SERVICE_PORT=8001
FOOD_SERVICE_HOST=0.0.0.0

# Model Configuration
MODEL_DEVICE=cpu
MODEL_CONFIDENCE_THRESHOLD=0.5

# API Configuration
CORS_ORIGINS=*
ALLOW_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        logger.info("✅ .env file created")
    else:
        logger.info("✅ .env file already exists")

def test_installation():
    """Test if the installation works."""
    logger.info("Testing installation...")
    
    test_script = """
import torch
import torchvision
from PIL import Image
import numpy as np
print("✅ PyTorch:", torch.__version__)
print("✅ Torchvision:", torchvision.__version__)
print("✅ Device available:", torch.cuda.is_available())
print("✅ CPU device:", torch.device('cpu'))
"""
    
    result = run_command(f'python -c "{test_script}"', "Testing installation")
    if result:
        logger.info("✅ Installation test passed")
        return True
    else:
        logger.error("❌ Installation test failed")
        return False

def create_startup_script():
    """Create a startup script for the service."""
    startup_script = Path(__file__).parent / "start_food_service.py"
    
    startup_content = '''#!/usr/bin/env python3
"""
Startup script for Food Classification Service
"""

import uvicorn
from food_service import app

if __name__ == "__main__":
    print("🍎 Starting Food Classification Service...")
    print("📱 Service will be available at: http://localhost:8001")
    print("🔍 Health check: http://localhost:8001/health")
    print("📚 API docs: http://localhost:8001/docs")
    print("\\nPress Ctrl+C to stop the service")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    )
'''
    
    with open(startup_script, 'w') as f:
        f.write(startup_content)
    
    # Make it executable
    os.chmod(startup_script, 0o755)
    logger.info("✅ Startup script created")

def main():
    """Main setup function."""
    logger.info("🍎 Setting up Food Classification Service...")
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create environment file
    create_environment_file()
    
    # Test installation
    if test_installation():
        logger.info("✅ Food Classification Service setup completed successfully!")
        
        # Create startup script
        create_startup_script()
        
        logger.info("\\n🚀 To start the service, run:")
        logger.info("   python start_food_service.py")
        logger.info("\\n📱 The service will be available at:")
        logger.info("   http://localhost:8001")
        logger.info("\\n🔍 Test the service:")
        logger.info("   curl http://localhost:8001/health")
        
    else:
        logger.error("❌ Setup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
