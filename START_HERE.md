# 🚀 FOFIS - Start Here!

Welcome to the **Flight Corridor Monitoring System (FOFIS)**!

## ⚡ Quick Start (5 Minutes)

### 1. Run the Setup Script

```bash
cd /Users/ivan/PycharmProjects/FOFIS
chmod +x setup.sh
./setup.sh
```

### 2. Start the Server

```bash
source venv/bin/activate
python manage.py runserver
```

### 3. Open Your Browser

Go to: **http://127.0.0.1:8000/**

### 4. Upload Sample Files

1. Find the table at the bottom of the page
2. Drag `sample_data/corridor.txt` to the "Corridor File" dropzone
3. Drag `sample_data/trajectory.txt` to the "Trajectory File" dropzone
4. Wait a few seconds for processing

### 5. Start Playback

1. Click on the row in the table
2. Click the **▶ Play** button (top-right)
3. Watch the aircraft fly!

---

## 📚 Documentation Guide

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[QUICKSTART.md](QUICKSTART.md)** | Quick setup guide | **Start here for setup** |
| **[README.md](README.md)** | Complete documentation | Detailed usage and API |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Overview of what's included | See what you have |
| **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** | Technical details | Understand the system |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System architecture | Learn the design |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Production deployment | Deploy to production |

---

## 🎯 What You Can Do

### Immediate Actions
✅ Run the application locally  
✅ Upload sample files  
✅ Watch playback animation  
✅ Test different speeds  
✅ Try violation scenarios  
✅ Explore the admin interface  

### Next Steps
🔧 Create your own corridor files  
🔧 Add custom trajectories  
🔧 Customize the UI  
🔧 Deploy to production  
🔧 Add new features  

---

## 🛠️ Key Commands

```bash
# Setup
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Run development server
python manage.py runserver

# Run tests
python manage.py test

# Create admin user
python manage.py createsuperuser

# Access admin interface
# Go to http://127.0.0.1:8000/admin/

# Compile C++ validator
cd cpp && make && cd ..
```

---

## 📁 Important Files

```
FOFIS/
├── setup.sh                    ← Run this first!
├── manage.py                   ← Django management
├── requirements.txt            ← Dependencies
│
├── 📚 Documentation
│   ├── START_HERE.md          ← You are here!
│   ├── QUICKSTART.md          ← Quick setup
│   ├── README.md              ← Full docs
│   ├── PROJECT_SUMMARY.md     ← Overview
│   ├── PROJECT_OVERVIEW.md    ← Technical details
│   ├── ARCHITECTURE.md        ← System design
│   └── DEPLOYMENT.md          ← Production guide
│
├── 📂 fofis_project/          ← Django settings
├── 📂 monitoring/             ← Main app
├── 📂 templates/              ← Frontend
├── 📂 cpp/                    ← C++ validator
└── 📂 sample_data/            ← Test files
```

---

## 🎓 Learning Path

### Day 1: Setup & Basics
1. Run `setup.sh`
2. Start server
3. Upload sample files
4. Test playback
5. Read QUICKSTART.md

### Day 2: Understanding
1. Read README.md
2. Explore admin interface
3. Run unit tests
4. Review PROJECT_OVERVIEW.md
5. Try creating custom files

### Day 3: Customization
1. Modify UI (templates/index.html)
2. Add new API endpoints
3. Create more test scenarios
4. Read ARCHITECTURE.md

### Week 2: Production
1. Review DEPLOYMENT.md
2. Set up PostgreSQL
3. Configure for production
4. Deploy to server

---

## ❓ Common Questions

### Q: Where do I upload files?
**A:** At the bottom of the main page, in the table. Look for the dropzones.

### Q: How do I start playback?
**A:** Click on a row in the table, then click the Play button (top-right).

### Q: Where are my uploaded files stored?
**A:** In the `media/` directory (created automatically).

### Q: How do I create custom corridor/trajectory files?
**A:** See the "File Formats" section in README.md for specifications.

### Q: Can I deploy this to production?
**A:** Yes! See DEPLOYMENT.md for complete instructions.

### Q: Where can I see metrics?
**A:** In the table (mean deviation, mean speed) or in the admin interface.

### Q: How do I delete a flight case?
**A:** Click the "Delete" button in the table row.

### Q: What if processing fails?
**A:** Check the "processing_error" field in the admin interface for details.

---

## 🐛 Troubleshooting

### Issue: Setup script fails
```bash
# Check Python version (need 3.8+)
python3 --version

# Check g++ is installed
g++ --version

# Install manually if needed
pip install -r requirements.txt
```

### Issue: Server won't start
```bash
# Delete database and recreate
rm db.sqlite3
python manage.py migrate
```

### Issue: Files won't upload
```bash
# Create directories
mkdir -p media/corridors media/trajectories

# Check permissions
chmod 755 media
```

### Issue: Map doesn't load
- Check internet connection (Leaflet loads from CDN)
- Open browser console to see JavaScript errors

### Issue: C++ validator not working
```bash
cd cpp
make clean
make
chmod +x trajectory_validator
```

---

## 💡 Tips & Tricks

1. **Multiple Flight Cases**: You can upload multiple corridor/trajectory pairs
2. **Speed Control**: Use the dropdown to change playback speed (up to 16×)
3. **Time Jumping**: Drag the time slider to jump to any point in the flight
4. **Admin Interface**: Create a superuser to access advanced management
5. **Sample Data**: Start with the provided samples before creating your own
6. **Browser DevTools**: Open console (F12) to see detailed logs

---

## 🌟 Features Highlights

- ✅ **Drag & Drop Upload**: Just drop your files!
- ✅ **Automatic Processing**: No manual steps needed
- ✅ **Real-time Visualization**: See corridors immediately
- ✅ **Smooth Animation**: 60 FPS playback
- ✅ **Variable Speed**: From 1× to 16× playback
- ✅ **3D Calculations**: Accurate distance with altitude
- ✅ **Multiple Cases**: Manage many flight pairs
- ✅ **Metrics Display**: Deviation and speed analysis
- ✅ **C++ Integration**: High-performance validation
- ✅ **REST API**: Full programmatic access

---

## 📞 Getting Help

1. **Documentation**: Check the relevant .md file
2. **Browser Console**: Press F12 to see errors
3. **Django Logs**: Check terminal output
4. **Admin Interface**: View processing errors
5. **Unit Tests**: Run `python manage.py test`

---

## 🎉 You're Ready!

Everything you need is in this directory. Just run the setup script and start exploring!

```bash
./setup.sh
source venv/bin/activate
python manage.py runserver
```

Then open: **http://127.0.0.1:8000/**

Enjoy using FOFIS! 🚁✈️

---

**FOFIS** - Flight Corridor Monitoring System  
*Professional aircraft trajectory analysis made easy*

