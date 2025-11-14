#!/bin/bash
# FOFIS Setup Script

echo "=========================================="
echo "FOFIS - Flight Corridor Monitoring System"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Check if g++ is installed
if ! command -v g++ &> /dev/null; then
    echo "Error: g++ is not installed. Please install g++ for C++ compilation."
    exit 1
fi

echo "✓ g++ found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Compile C++ validator
echo ""
echo "Compiling C++ validator..."
cd cpp
make
if [ $? -eq 0 ]; then
    echo "✓ C++ validator compiled successfully"
else
    echo "✗ Failed to compile C++ validator"
    exit 1
fi
cd ..

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p media/corridors
mkdir -p media/trajectories
mkdir -p static
echo "✓ Directories created"

# Run migrations
echo ""
echo "Setting up database..."
python manage.py makemigrations
python manage.py migrate
echo "✓ Database initialized"

# Success message
echo ""
echo "=========================================="
echo "✓ Setup completed successfully!"
echo "=========================================="
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then open: http://127.0.0.1:8000/"
echo ""
echo "For a quick start guide, see: QUICKSTART.md"
echo "For full documentation, see: README.md"
echo ""

