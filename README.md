# 📚 Webtoon Downloader

A modern, terminal-style application for downloading webtoons and manga as PDF files with a clean, professional interface.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.10+-green)

## ✨ Features

### 🎨 Modern Terminal-Style UI
- Dark theme with colorful, terminal-style interface
- Clean and intuitive design
- Responsive layout that adapts to window size
- Custom icon in titlebar and taskbar

### 📥 Smart Download System
- **URL Detection**: Automatically fetches all available chapters
- **Chapter Selection**: Choose specific chapters via popup window
- **Batch Download**: Download multiple chapters at once
- **Progress Tracking**: Real-time progress bars with page counts
- **Automatic PDF**: Converts downloaded images to PDF automatically

### 🎯 Live Progress Display
- One-line updating progress bars (no log spam)
- Chapter-by-chapter progress tracking
- Real-time page count display
- Percentage completion
- Color-coded status messages

### 📊 Activity Logs
- Detailed activity logging
- Color-coded messages (Info, Success, Warning, Error)
- Clear button to clean logs
- Easy-to-read console-style output

---

## 🚀 Quick Start

### Installation

1. **Download the Application**
   - Get `WebtoonDownloader.exe` (standalone executable)
   - OR download source code and install dependencies

2. **Run the Application**
   ```bash
   # If using executable
   WebtoonDownloader.exe
   
   # If using source
   python main.py
   ```

3. **Install Dependencies** (source only)
   ```bash
   pip install -r requirements.txt
   ```

---

## 📖 How to Use

### Step 1: Launch Application
- Double-click `WebtoonDownloader.exe` or `run.bat`
- Application window opens with terminal-style interface

### Step 2: Enter Webtoon URL
1. Find a webtoon/manga series on supported sites
2. Copy the series URL (e.g., `https://www.webtoons.com/en/...`)
3. Paste URL in the input field
4. Press **Enter** or click **🔍 FETCH** button

### Step 3: Wait for Chapter Detection
- Application automatically scans all available chapters
- Progress shown in Activity Logs
- May take a few seconds depending on series size

### Step 4: Select Chapters
1. **Popup window** appears with all chapters
2. Check the chapters you want to download
3. Use **"Select All"** for all chapters
4. Click **⬇️ Download Selected**
5. Window closes automatically

### Step 5: Monitor Download
- Watch live progress in Activity Logs section
- Each chapter shows:
  - **Progress bar** (animated)
  - **Percentage** complete
  - **Page count** (current/total)
  - **Chapter title**
- Progress updates in ONE LINE per chapter (clean!)

### Step 6: Access Downloads
- Click **📁 Open Downloads Folder** button
- PDFs saved in: `C:\Users\[YourName]\Documents\Webtoons\[Series Name]\`
- Each chapter = one PDF file
- Files named automatically based on chapter titles

---

## 🎮 Interface Guide

### Main Window Layout

![main window layout](https://i.ibb.co/TM1JN7SJ/10-2500x1667.jpg)



### Activity Log Colors
- **🔵 Cyan**: Information messages
- **🟢 Green**: Success messages  
- **🟡 Yellow**: Warnings
- **🔴 Red**: Errors
- **🟣 Magenta**: Download progress bars

### Buttons
- **🔍 FETCH**: Fetch chapters from URL
- **📁 Open Downloads**: Open downloads folder in explorer
- **⏹️ Stop Download**: Cancel ongoing download
- **🗑️ Clear**: Clear activity logs

---

## 🌟 Advanced Features

### Chapter Selection Window
- **Search functionality**: Filter chapters by name
- **Select All/None**: Quick selection toggles
- **Scrollable list**: Handles 100+ chapters smoothly
- **Auto-close**: Window closes after selection
- **Batch loading**: No lag even with many chapters

### Progress Animation
- **Smart updates**: One line per chapter (no spam)
- **Real-time**: Updates as pages download
- **Visual bars**: ASCII art progress bars
- **Detailed info**: Chapter number, percentage, pages

### Download Management
- **Concurrent downloading**: Multiple pages at once
- **Error handling**: Failed pages logged but don't stop download
- **Resume capability**: Cancel and restart anytime
- **Automatic retry**: Retries failed connections
- **Cleanup**: Temporary files removed automatically

---

## 📁 File Structure

```
Webtoon Downloader/
├── WebtoonDownloader.exe    # Standalone executable
├── icon.ico                  # Application icon
├── downloads/                # Downloaded PDFs
│   └── [Series Name]/
│       ├── Chapter 1.pdf
│       ├── Chapter 2.pdf
│       └── ...
└── logs/                     # Activity logs (optional)
```

---

## 🎯 Supported Sites

Currently supports:
- ✅ Webtoons.com
- ✅ Other sites using similar structure

### URL Format Examples
```
https://www.webtoons.com/en/fantasy/tower-of-god/...
https://www.webtoons.com/en/drama/true-beauty/...
```

---

## ⚙️ Settings & Configuration

### Window Resizing
- **Responsive fonts**: Text scales with window size
- **Minimum size**: 700x500 pixels
- **Default size**: 950x700 pixels
- **Maximize**: Supported

### Downloads Location
- **Default**: `downloads` folder in app directory
- **Organization**: One folder per series
- **Format**: PDF (high quality)
- **Naming**: Automatic based on chapter titles

---

## 🐛 Troubleshooting

### "No chapters found"
**Solutions:**
- Check if URL is correct
- Ensure series URL (not chapter URL)
- Try copying URL again
- Check internet connection

### "Failed to fetch chapters"
**Solutions:**
- Verify internet connection
- Check if site is accessible
- Wait a moment and retry
- Check Activity Logs for details

### Download stuck or slow
**Solutions:**
- Check internet speed
- Site may be rate-limiting
- Try fewer chapters at once
- Check Activity Logs for errors

### PDF not created
**Solutions:**
- Check Activity Logs for errors
- Ensure disk space available
- Check downloads folder permissions
- Retry the chapter

### Application won't start
**Solutions:**
- Check if Python installed (source mode)
- Verify all dependencies installed
- Try running as administrator
- Check system requirements

---

## 💡 Tips & Best Practices

### For Best Results
1. **Stable Internet**: Use reliable connection
2. **Batch Smartly**: Download 5-10 chapters at a time
3. **Check Logs**: Monitor Activity Logs for issues
4. **Wait Patiently**: Large chapters take time
5. **Select Carefully**: Choose only chapters you need

### Performance Tips
- Close other bandwidth-heavy applications
- Don't resize window during download
- Let download complete before closing
- Use "Select All" for full series

### Storage Tips
- PDFs can be large (10-50 MB each)
- Monitor disk space
- Organize downloads folder regularly
- Delete unwanted PDFs

---

## 📊 Performance

### Speed
- **Chapter Detection**: 5-30 seconds (depends on series size)
- **Download Speed**: Depends on internet and site
- **PDF Conversion**: ~1-3 seconds per chapter
- **Average**: 1-2 minutes per chapter

### Resource Usage
- **Memory**: ~100-300 MB
- **CPU**: Low (5-10%)
- **Disk**: Space for PDFs only
- **Network**: Varies with download speed

---

## 🔒 Privacy & Safety

### Data Collection
- **No tracking**: Application doesn't track users
- **No accounts**: No login required
- **Local only**: All data stays on your computer
- **No uploads**: No data sent except download requests

### Safety
- **Official sources**: Downloads from official sites only
- **No malware**: Clean, safe application
- **Open source**: Code is transparent
- **Automatic updates**: No automatic updates

---

## ❓ FAQ

### Q: Is this free?
**A:** Yes, completely free to use.

### Q: Do I need an account?
**A:** No, no registration required.

### Q: What format are downloads?
**A:** PDF format, ready to read.

### Q: Can I download entire series?
**A:** Yes, use "Select All" in chapter selection.

### Q: Where are downloads saved?
**A:** In `downloads` folder, organized by series name.

### Q: Can I use this on mobile?
**A:** No, Windows desktop only.

### Q: Does it work offline?
**A:** No, internet connection required.

### Q: Can I cancel downloads?
**A:** Yes, click "Stop Download" button.

### Q: Are downloads permanent?
**A:** Yes, PDFs saved locally forever.

### Q: Can I redistribute PDFs?
**A:** Check the original content's copyright/license.

---

## 🎨 Interface Screenshots

### Main Window
Clean, modern interface with terminal aesthetics and real-time progress.

### Chapter Selection
Popup window with all available chapters, easy selection with checkboxes.

### Live Download
One-line updating progress bars showing real-time download status.

---

## 🆘 Support

### Getting Help
1. Check Activity Logs in app
2. Review Troubleshooting section above
3. Check FAQ
4. Verify internet connection
5. Try restarting application

### Error Messages
All errors displayed in Activity Logs with:
- **Timestamp**: When error occurred
- **Details**: What went wrong
- **Level**: Error/Warning severity

---

## 📝 License & Credits

### Application
- **Name**: Webtoon Downloader
- **Version**: 1.0.0
- **Platform**: Windows
- **License**: Free to use

### Technologies Used
- **Python**: Core programming language
- **CustomTkinter**: Modern UI framework
- **Pillow**: Image processing
- **img2pdf**: PDF conversion
- **Requests**: HTTP library
- **BeautifulSoup**: HTML parsing

### Credits
Created with modern design principles and user experience in mind.

---

## 🚀 Getting Started Checklist

- [ ] Download WebtoonDownloader.exe
- [ ] Run the application
- [ ] Copy a webtoon series URL
- [ ] Paste URL and click FETCH
- [ ] Select chapters in popup
- [ ] Monitor progress in Activity Logs
- [ ] Open downloads folder
- [ ] Enjoy your PDFs!

---

## 📞 Quick Reference

| Action | How To |
|--------|--------|
| Fetch Chapters | Paste URL → Press Enter or FETCH |
| Select Chapters | Check boxes in popup → Download Selected |
| Cancel Download | Click "Stop Download" button |
| Clear Logs | Click "Clear" button in logs section |
| Open Downloads | Click "Open Downloads Folder" button |
| Close App | Click X or Alt+F4 |

---

**Enjoy downloading your favorite webtoons! 📚✨**

---

*Last Updated: November 2025*
*Version: 1.0.0*
