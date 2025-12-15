#!/bin/bash
# Quick start script for FOFIS

echo "🚀 Запуск FOFIS локально..."
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Виртуальное окружение не найдено!"
    echo "Запустите сначала: ./setup.sh"
    echo ""
    read -p "Создать сейчас? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./setup.sh
    else
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Check if database exists
if [ ! -f "db.sqlite3" ]; then
    echo "📊 База данных не найдена, создаю..."
    python manage.py migrate
fi

# Check if C++ validator is compiled
if [ ! -f "cpp/trajectory_validator" ]; then
    echo "⚙️  C++ валидатор не скомпилирован, компилирую..."
    cd cpp
    make
    cd ..
fi

# Start server
echo ""
echo "✅ Запуск сервера..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Откройте в браузере:"
echo "   http://127.0.0.1:8000/"
echo ""
echo "🛑 Для остановки нажмите Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python manage.py runserver

