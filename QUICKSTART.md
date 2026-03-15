# Quick Start Guide - Glassmorphism Edition

Get your beautiful system monitor running in 2 minutes!

---

## ⚡ Super Quick Start

### Windows
1. Double-click `install.bat`
2. Double-click `run.bat`
3. Done! 🎉

### Linux/Mac
```bash
./install.sh
./run.sh
```

---

## 🎨 What You'll See

### Top Section - Perfectly Aligned Circles
Four beautiful glassmorphism circles showing:
- 🖥️ **CPU** - Processor usage
- 💾 **Memory** - RAM usage
- 💿 **Disk** - Storage usage
- 🎮 **GPU** - Graphics card (if available)

**Colors mean:**
- Light blue (0-50%): Everything is fine ✅
- Sky blue (50-75%): Moderate usage ⚠️
- Royal blue (75-100%): High usage 🔥

### Middle Section - Glass Info Cards
Five elegant cards showing:
- ⬆️ **Upload** - Network upload speed
- ⬇️ **Download** - Network download speed
- 🌡️ **Temperature** - System temperature
- ⚙️ **Processes** - Number of running programs
- ⏱️ **Uptime** - How long system has been running

### Bottom Section - Detailed Tabs
📊 **Overview** - Beautiful charts with real-time data
⚙️ **Processes** - See and manage all running programs
🌐 **Network** - Network interfaces and statistics
💾 **Storage** - All your drives and their space
ℹ️ **System Info** - Complete hardware information

---

## 🎯 Common Tasks

### Task 1: Check System Performance
Just look at the circles!
- All light blue? Everything is perfect ✅
- Some sky blue? System is working hard but fine ⚠️
- Royal blue? Something is using lots of resources 🔥

### Task 2: See What's Using Resources
1. Click the **⚙️ Processes** tab
2. Look at top of list (sorted by CPU usage)
3. High CPU or Memory? That's your resource hog!

### Task 3: Stop a Program
1. Go to **⚙️ Processes** tab
2. Find the program you want to stop
3. Click on it to select
4. Click **❌ End Process**
5. Confirm by clicking Yes

### Task 4: Check Network Speed
Look at the glass cards:
- **⬆️ Upload** shows upload speed
- **⬇️ Download** shows download speed

Or click **🌐 Network** tab for details!

### Task 5: See System Details
1. Click **ℹ️ System Info** tab
2. See all your hardware specs
3. Operating system, processor, memory, etc.

---

## ⚙️ Quick Settings

### Change Update Speed
1. Click **Tools** menu
2. Click **Settings**
3. Change Refresh Rate:
   - 500ms = Very fast updates (uses more CPU)
   - 1000ms = Default (recommended) ✅
   - 2000ms = Slower updates (uses less CPU)

---

## 💡 Pro Tips

1. **Sort Processes**: Click any column header in the process table
2. **Search**: Type in the search box to filter processes instantly
3. **Watch Charts**: The Overview tab shows trends over time
4. **Check Temperature**: If your system feels hot, check the 🌡️ card
5. **Export Data**: Use File → Export Data to save statistics

---

## 🎨 Design Features

This edition features:
- ✨ **Glassmorphism** - Beautiful glass effects
- 🎨 **Light Blue & White** - Professional color scheme
- ⭕ **Perfect Alignment** - Everything centered perfectly
- 🎬 **Smooth Animations** - Satisfying transitions
- 📊 **Beautiful Charts** - Easy to read graphs

---

## 🚨 When to Worry

### CPU Circle Royal Blue?
- Find what's using CPU in Processes tab
- Close unnecessary programs
- Some programs naturally use high CPU (video editing, games)

### Memory Circle Royal Blue?
- Close browser tabs you're not using
- End unnecessary programs
- Consider upgrading RAM if persistent

### Disk Circle Royal Blue?
- Free up space!
- Delete old files
- Empty recycle bin
- Move files to external drive

### High Network Speed When Idle?
- Check Processes tab for unexpected activity
- Could be Windows Update or cloud sync
- Make sure no unwanted programs are active

---

## ✅ Quick Checklist

After starting the app, you should see:
- ✅ Four circular indicators at the top
- ✅ Five glass info cards in the middle
- ✅ Current date and time in top right
- ✅ Five tabs at the bottom
- ✅ Values updating smoothly

If anything is missing, restart the application.

---

## 🎓 Understanding the Interface

### Circular Progress Indicators
- **Size**: Each circle is the same size
- **Alignment**: Perfectly centered horizontally
- **Animation**: Smooth 0.5 second transitions
- **Color**: Changes based on usage level

### Glass Effect
- Semi-transparent backgrounds
- Blur effect behind elements
- Light blue borders
- Gradient overlays

### Charts (Overview Tab)
- **120 data points** = 2 minutes of history
- **Updates every second** for smooth animation
- **Multiple lines** on network chart
- **Auto-scaling** Y-axis

---

## 🔧 Troubleshooting

**Problem**: Circles not showing
- Restart the application
- Check if PyQt5 installed: `pip list | grep PyQt5`

**Problem**: No GPU circle
- Only NVIDIA GPUs supported
- Install: `pip install GPUtil`

**Problem**: No temperature
- Not all systems have temperature sensors
- This is normal on some laptops

**Problem**: Process table empty
- Wait a few seconds for first update
- Check if psutil installed: `pip list | grep psutil`

**Problem**: Charts not updating
- Check refresh rate in settings
- Make sure app is not minimized

---

## 🎉 You're Ready!

Now you can:
- ✅ Monitor your system in real-time
- ✅ See beautiful glassmorphism design
- ✅ Manage processes effectively
- ✅ Track network and disk usage
- ✅ Export data for analysis

**Enjoy your beautiful system monitor!** 🎨✨

For more details, see the full README.md file.

---

**Version 3.0 | Glassmorphism Edition**
