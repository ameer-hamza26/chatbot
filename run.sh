#!/bin/bash

# Script to run the backend directly

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3.11 -m venv venv || python3.12 -m venv venv || python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 13 ]; then
    echo "Warning: Python 3.13+ detected. PyTorch may not have official support yet."
    echo "If installation fails, consider recreating venv with Python 3.11 or 3.12:"
    echo "  rm -rf venv && python3.11 -m venv venv  # or python3.12"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY"
    echo "Example: echo 'OPENAI_API_KEY=your_key_here' > .env"
    exit 1
fi

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip

# Install torch - try multiple methods for Python 3.13 compatibility
echo "Installing PyTorch..."
TORCH_INSTALLED=false

# Try nightly CPU build (may support Python 3.13)
if pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cpu 2>/dev/null; then
    echo "✓ PyTorch installed from nightly CPU build"
    TORCH_INSTALLED=true
else
    # Try nightly CUDA build (may support Python 3.13)
    if pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu121 2>/dev/null; then
        echo "✓ PyTorch installed from nightly CUDA build"
        TORCH_INSTALLED=true
    else
        # Try standard CPU build
        if pip install torch --index-url https://download.pytorch.org/whl/cpu 2>/dev/null; then
            echo "✓ PyTorch installed from standard CPU build"
            TORCH_INSTALLED=true
        else
            # Try standard PyPI (may work for older Python versions)
            if pip install torch 2>/dev/null; then
                echo "✓ PyTorch installed from PyPI"
                TORCH_INSTALLED=true
            fi
        fi
    fi
fi

if [ "$TORCH_INSTALLED" = false ]; then
    echo "❌ Error: PyTorch installation failed!"
    echo "PyTorch may not support Python 3.13 yet."
    echo "Solution: Recreate venv with Python 3.11 or 3.12:"
    echo "  rm -rf venv"
    echo "  python3.11 -m venv venv  # or python3.12"
    echo "  Then run this script again."
    exit 1
fi

# Install other dependencies
pip install -r requirements.txt

# Run the backend
echo "Starting backend server..."
echo "Access the API at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload



