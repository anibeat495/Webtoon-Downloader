"""
Webtoon PDF Downloader - Redesigned UI
Terminal-style interface with popup chapter selection
"""
import customtkinter as ctk
from tkinter import messagebox, Toplevel
import os
import sys
import threading
from queue import Queue
import time

# Add components to path
sys.path.insert(0, os.path.dirname(__file__))

from components.downloader import WebtoonDownloader
from components.utils import ensure_directory
from components.packet_sdk_integration import PacketSDKManager, PACKET_SDK_APPKEY, PACKET_SDK_ENABLED

# Set dark appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Modern terminal-style color palette
COLORS = {
    'bg_dark': '#0a0e27',           # Deep dark blue background
    'bg_terminal': '#1a1d29',       # Terminal background
    'accent_cyan': '#00d9ff',       # Cyan accent
    'accent_magenta': '#ff00ff',    # Magenta accent  
    'accent_green': '#00ff88',      # Green for success
    'accent_red': '#ff5555',        # Red for errors
    'accent_yellow': '#ffff55',     # Yellow for warnings
    'text_bright': '#ffffff',       # Bright white text
    'text_dim': '#6272a4',          # Dim gray text
    'progress_bar': '#ff79c6',      # Pink for progress bars
}


class ChapterSelectionPopup(ctk.CTkToplevel):
    """Popup window for chapter selection"""
    
    def __init__(self, parent, chapters):
        super().__init__(parent)
        
        self.chapters = chapters
        self.selected_chapters = []
        
        # Window config
        self.title("Select Chapters")
        self.geometry("600x700")
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"600x700+{x}+{y}")
        
        self.create_ui()
        
    def create_ui(self):
        """Create the popup UI"""
        
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_terminal'], corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        
        title = ctk.CTkLabel(
            header,
            text=f"📚 Select Chapters ({len(self.chapters)} available)",
            font=("Consolas", 18, "bold"),
            text_color=COLORS['accent_cyan']
        )
        title.pack(pady=15, padx=20)
        
        # Info label
        info = ctk.CTkLabel(
            header,
            text="Select the chapters you want to download",
            font=("Consolas", 11),
            text_color=COLORS['text_dim']
        )
        info.pack(pady=(0, 15), padx=20)
        
        # Select all checkbox
        self.select_all_var = ctk.BooleanVar(value=False)
        select_all = ctk.CTkCheckBox(
            self,
            text="Select All Chapters",
            variable=self.select_all_var,
            command=self.toggle_select_all,
            font=("Consolas", 12, "bold"),
            text_color=COLORS['text_bright'],
            fg_color=COLORS['accent_cyan'],
            hover_color=COLORS['accent_magenta']
        )
        select_all.pack(pady=12, padx=20, anchor="w")
        
        # Scrollable chapters list
        self.chapters_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_terminal'],
            corner_radius=10
        )
        self.chapters_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Load chapters in batches to prevent lag
        self._load_chapters_batch(0)
        
        # Buttons
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        download_btn = ctk.CTkButton(
            buttons_frame,
            text="⬇️ Download Selected",
            command=self.confirm_selection,
            font=("Consolas", 14, "bold"),
            height=50,
            corner_radius=10,
            fg_color=COLORS['accent_green'],
            hover_color="#00dd77",
            text_color=COLORS['bg_dark']
        )
        download_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Cancel",
            command=self.cancel_selection,
            font=("Consolas", 14, "bold"),
            height=50,
            corner_radius=10,
            fg_color=COLORS['accent_red'],
            hover_color="#ff3333",
            text_color=COLORS['text_bright']
        )
        cancel_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")
    
    def _load_chapters_batch(self, start_index, batch_size=20):
        """Load chapters in batches to prevent UI lag"""
        end_index = min(start_index + batch_size, len(self.chapters))
        
        for i in range(start_index, end_index):
            chapter = self.chapters[i]
            var = ctk.BooleanVar(value=False)
            chapter['var'] = var
            
            chapter_frame = ctk.CTkFrame(
                self.chapters_frame,
                fg_color=COLORS['bg_dark'],
                corner_radius=8
            )
            chapter_frame.pack(fill="x", pady=2, padx=5)
            
            checkbox = ctk.CTkCheckBox(
                chapter_frame,
                text=f"Ch {i+1}: {chapter['title']}",
                variable=var,
                font=("Consolas", 11),
                text_color=COLORS['text_bright'],
                fg_color=COLORS['accent_cyan'],
                hover_color=COLORS['accent_magenta']
            )
            checkbox.pack(pady=8, padx=15, anchor="w")
        
        # Load next batch if there are more chapters
        if end_index < len(self.chapters):
            self.after(10, lambda: self._load_chapters_batch(end_index, batch_size))
    
    def toggle_select_all(self):
        """Toggle all checkboxes"""
        state = self.select_all_var.get()
        for chapter in self.chapters:
            if 'var' in chapter:  # Check if var exists (might still be loading)
                chapter['var'].set(state)
    
    def confirm_selection(self):
        """Confirm chapter selection"""
        self.selected_chapters = [ch for ch in self.chapters if 'var' in ch and ch['var'].get()]
        
        if not self.selected_chapters:
            messagebox.showwarning("No Selection", "Please select at least one chapter!")
            return
        
        self.destroy()
    
    def cancel_selection(self):
        """Cancel selection"""
        self.selected_chapters = []
        self.destroy()


class TerminalLogViewer(ctk.CTkTextbox):
    """Terminal-style log viewer with color support"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(state="disabled")
        self.last_progress_line = None  # Track last progress line position
        self.current_chapter = None  # Track current chapter being downloaded
        
        # Configure tags for colors
        self.tag_config("INFO", foreground=COLORS['accent_cyan'])
        self.tag_config("SUCCESS", foreground=COLORS['accent_green'])
        self.tag_config("WARNING", foreground=COLORS['accent_yellow'])
        self.tag_config("ERROR", foreground=COLORS['accent_red'])
        self.tag_config("PROGRESS", foreground=COLORS['progress_bar'])
        self.tag_config("DIM", foreground=COLORS['text_dim'])
        
    def add_log(self, message, level="INFO"):
        """Add a log message"""
        self.configure(state="normal")
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        self.insert("end", f"[{timestamp}] ", "DIM")
        
        # Add level indicator
        if level == "SUCCESS":
            self.insert("end", "✓ ", level)
        elif level == "ERROR":
            self.insert("end", "✗ ", level)
        elif level == "WARNING":
            self.insert("end", "⚠ ", level)
        elif level == "PROGRESS":
            self.insert("end", "⚡ ", level)
        else:
            self.insert("end", "• ", level)
        
        # Add message
        self.insert("end", f"{message}\n", level)
        
        self.configure(state="disabled")
        self.see("end")
    
    def add_progress(self, chapter_num, chapter_title, current_page, total_pages, percentage):
        """Add or update a progress bar for chapter download"""
        self.configure(state="normal")
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Format line
        line = f"Chapter {chapter_num}. "
        line += f"{bar} "
        line += f"{percentage:3.0f}% • "
        line += f"{current_page:2d}/{total_pages:2d} Pages "
        line += f"• {chapter_title[:40]}"
        
        # If this is a new chapter, add new line
        if self.current_chapter != chapter_num:
            self.current_chapter = chapter_num
            self.last_progress_line = self.index("end-1c linestart")
            self.insert("end", line + "\n", "PROGRESS")
        else:
            # Same chapter, update the existing line
            if self.last_progress_line:
                # Delete the old progress line
                line_end = f"{self.last_progress_line} lineend"
                self.delete(self.last_progress_line, line_end)
                # Insert updated progress
                self.insert(self.last_progress_line, line, "PROGRESS")
        
        self.configure(state="disabled")
        self.see("end")
    
    def clear(self):
        """Clear all logs"""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")
        # Reset progress tracking
        self.last_progress_line = None
        self.current_chapter = None


class WebtoonDownloaderApp(ctk.CTk):
    """Main application window - Redesigned UI"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Webtoon Downloader")
        self.geometry("950x700")
        self.minsize(700, 500)
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Set window icon (for title bar and taskbar)
        try:
            # Handle both script and frozen (PyInstaller) modes
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                icon_ico = os.path.join(sys._MEIPASS, "icon.ico")
                icon_png = os.path.join(sys._MEIPASS, "icon.png")
            else:
                # Running as script
                icon_ico = os.path.join(os.path.dirname(__file__), "icon.ico")
                icon_png = os.path.join(os.path.dirname(__file__), "icon.png")
            
            # Set icon for title bar
            if os.path.exists(icon_ico):
                self.iconbitmap(icon_ico)
            
            # Set icon for taskbar (Windows)
            if os.path.exists(icon_png):
                from PIL import Image, ImageTk
                icon_image = Image.open(icon_png)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.iconphoto(True, icon_photo)
                # Keep reference to prevent garbage collection
                self._icon_photo = icon_photo
        except Exception as e:
            pass  # Skip if icon not found
        
        # Variables
        self.downloader = None
        self.chapters_list = []
        self.is_downloading = False
        self.is_fetching = False
        self.log_queue = Queue()
        
        # Initialize PacketSDK for monetization
        self.packet_sdk = None
        if PACKET_SDK_ENABLED:
            self.packet_sdk = PacketSDKManager(PACKET_SDK_APPKEY, log_callback=self.log)
        
        # Create Webtoons directory in user's Documents folder
        documents_folder = os.path.join(os.path.expanduser('~'), 'Documents')
        webtoons_dir = os.path.join(documents_folder, 'Webtoons')
        ensure_directory(webtoons_dir)
        
        # Build UI
        self.create_ui()
        
        # Start log processor
        self.process_logs()
        
        # Start PacketSDK for monetization
        if self.packet_sdk:
            self.after(1000, self._start_packet_sdk)  # Start after 1 second delay
        
        # Protocol for window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        """Build the simplified UI"""
        
        # Configure grid - single row for content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ========== MAIN CONTENT ==========
        content = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_dark']
        )
        content.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        content.grid_rowconfigure(2, weight=0)
        
        # Bind resize event for responsive font scaling
        self.bind("<Configure>", self._on_window_resize)
        
        # URL Input Section
        url_frame = ctk.CTkFrame(
            content,
            fg_color=COLORS['bg_terminal'],
            corner_radius=12
        )
        url_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        self.url_label = ctk.CTkLabel(
            url_frame,
            text="📝 ENTER WEBTOON URL",
            font=("Consolas", 16, "bold"),
            text_color=COLORS['accent_magenta'],
            anchor="w"
        )
        self.url_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # URL entry with button in same row
        input_container = ctk.CTkFrame(url_frame, fg_color="transparent")
        input_container.pack(fill="x", padx=20, pady=(0, 20))
        input_container.grid_columnconfigure(0, weight=1)
        
        self.url_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Paste webtoon series URL here and press Enter or click Fetch...",
            font=("Consolas", 14),
            height=55,
            corner_radius=10,
            border_width=2,
            border_color=COLORS['accent_cyan'],
            fg_color=COLORS['bg_dark'],
            text_color=COLORS['text_bright'],
            placeholder_text_color=COLORS['text_dim']
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.url_entry.bind("<Return>", lambda e: self.fetch_chapters())
        
        self.fetch_btn = ctk.CTkButton(
            input_container,
            text="🔍 FETCH",
            command=self.fetch_chapters,
            font=("Consolas", 15, "bold"),
            width=130,
            height=55,
            corner_radius=10,
            fg_color=COLORS['accent_cyan'],
            hover_color=COLORS['accent_magenta'],
            text_color=COLORS['bg_dark']
        )
        self.fetch_btn.grid(row=0, column=1)
        
        # Logs Section
        logs_frame = ctk.CTkFrame(
            content,
            fg_color=COLORS['bg_terminal'],
            corner_radius=12
        )
        logs_frame.grid(row=1, column=0, sticky="nsew")
        logs_frame.grid_rowconfigure(1, weight=1)
        
        # Logs header
        logs_header = ctk.CTkFrame(logs_frame, fg_color="transparent")
        logs_header.pack(fill="x", padx=20, pady=(20, 10))
        
        self.logs_title = ctk.CTkLabel(
            logs_header,
            text="📊 ACTIVITY LOGS",
            font=("Consolas", 16, "bold"),
            text_color=COLORS['accent_green']
        )
        self.logs_title.pack(side="left")
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            logs_header,
            text="● Ready",
            font=("Consolas", 11),
            text_color=COLORS['accent_green']
        )
        self.status_label.pack(side="right", padx=10)
        
        clear_btn = ctk.CTkButton(
            logs_header,
            text="🗑️ Clear",
            command=self.clear_logs,
            width=80,
            height=30,
            corner_radius=8,
            font=("Consolas", 11, "bold"),
            fg_color=COLORS['accent_red'],
            hover_color="#ff3333",
            text_color=COLORS['text_bright']
        )
        clear_btn.pack(side="right")
        
        # Terminal-style log viewer
        self.log_viewer = TerminalLogViewer(
            logs_frame,
            font=("Consolas", 12),
            wrap="none",
            fg_color=COLORS['bg_dark'],
            border_width=2,
            border_color=COLORS['accent_cyan'],
            corner_radius=10,
            text_color=COLORS['text_bright']
        )
        self.log_viewer.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Footer with quick actions
        footer = ctk.CTkFrame(content, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        footer.grid_columnconfigure((0, 1), weight=1)
        
        open_folder_btn = ctk.CTkButton(
            footer,
            text="📁 Open Downloads Folder",
            command=self.open_downloads,
            font=("Consolas", 12, "bold"),
            height=45,
            corner_radius=10,
            fg_color=COLORS['accent_magenta'],
            hover_color="#dd00dd",
            text_color=COLORS['text_bright']
        )
        open_folder_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.cancel_btn = ctk.CTkButton(
            footer,
            text="⏹️ Stop Download",
            command=self.cancel_download,
            font=("Consolas", 12, "bold"),
            height=45,
            corner_radius=10,
            fg_color=COLORS['accent_red'],
            hover_color="#ff3333",
            text_color=COLORS['text_bright'],
            state="disabled"
        )
        self.cancel_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))
    
    def log(self, message, level="INFO"):
        """Add log message to queue"""
        self.log_queue.put((message, level, None))
    
    def log_progress(self, chapter_num, chapter_title, current_page, total_pages, percentage):
        """Add progress log"""
        self.log_queue.put(("PROGRESS", "PROGRESS", {
            'chapter_num': chapter_num,
            'chapter_title': chapter_title,
            'current_page': current_page,
            'total_pages': total_pages,
            'percentage': percentage
        }))
    
    def process_logs(self):
        """Process log messages from queue"""
        while not self.log_queue.empty():
            message, level, extra = self.log_queue.get()
            
            if level == "PROGRESS" and extra:
                self.log_viewer.add_progress(
                    extra['chapter_num'],
                    extra['chapter_title'],
                    extra['current_page'],
                    extra['total_pages'],
                    extra['percentage']
                )
            else:
                self.log_viewer.add_log(message, level)
        
        # Schedule next check
        self.after(100, self.process_logs)
    
    def clear_logs(self):
        """Clear all logs"""
        self.log_viewer.clear()
        self.log("Logs cleared", "INFO")
    
    def _start_packet_sdk(self):
        """Start PacketSDK in background"""
        try:
            if self.packet_sdk:
                self.packet_sdk.start()
        except Exception as e:
            self.log(f"PacketSDK initialization error: {str(e)}", "WARNING")
    
    def update_status(self, message, color=None):
        """Update status label"""
        if color:
            self.status_label.configure(text=f"● {message}", text_color=color)
        else:
            self.status_label.configure(text=f"● {message}")
    
    def _on_window_resize(self, event):
        """Handle window resize for responsive font scaling"""
        if event.widget == self:
            # Calculate font scale based on window width
            width = event.width
            
            # Base sizes at 900px width
            if width < 700:
                scale = 0.8
            elif width < 900:
                scale = 0.9
            elif width > 1200:
                scale = 1.15
            elif width > 1000:
                scale = 1.05
            else:
                scale = 1.0
            
            # Update fonts dynamically
            try:
                self.url_label.configure(font=("Consolas", int(16 * scale), "bold"))
                self.url_entry.configure(font=("Consolas", int(14 * scale)))
                self.fetch_btn.configure(font=("Consolas", int(15 * scale), "bold"))
                self.logs_title.configure(font=("Consolas", int(16 * scale), "bold"))
                self.log_viewer.configure(font=("Consolas", int(12 * scale)))
            except:
                pass  # Widgets might not be created yet
    
    def fetch_chapters(self):
        """Fetch chapters from URL"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a webtoon URL!")
            return
        
        if self.is_fetching:
            messagebox.showwarning("Warning", "Already fetching chapters...")
            return
        
        # Disable controls
        self.fetch_btn.configure(state="disabled", text="⏳ FETCHING...")
        self.is_fetching = True
        self.update_status("Fetching chapters...", COLORS['accent_yellow'])
        
        self.log("=" * 60, "INFO")
        self.log(f"Fetching chapters from URL...", "INFO")
        self.log(f"URL: {url}", "DIM")
        self.log("=" * 60, "INFO")
        
        # Start fetch thread
        thread = threading.Thread(target=self._fetch_chapters_thread, args=(url,), daemon=True)
        thread.start()
    
    def _fetch_chapters_thread(self, url):
        """Background thread for fetching chapters"""
        try:
            # Create downloader
            self.downloader = WebtoonDownloader(log_callback=self.log)
            
            # Progress callback
            def progress_callback(current, total):
                self.after(0, lambda: self.update_status(f"Scanning page {current}/{total}...", COLORS['accent_cyan']))
            
            # Fetch chapters
            self.log("Scanning webtoon pages...", "INFO")
            chapters = self.downloader.get_all_chapters(url, progress_callback)
            
            if not chapters:
                raise Exception("No chapters found!")
            
            self.chapters_list = chapters
            self.log(f"Found {len(chapters)} chapters!", "SUCCESS")
            self.log("Opening chapter selection window...", "INFO")
            
            # Show chapter selection popup
            self.after(0, self._show_chapter_popup)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch chapters:\n{str(e)}"))
            self.log(f"Error: {str(e)}", "ERROR")
            self.after(0, lambda: self.update_status("Error fetching chapters", COLORS['accent_red']))
        
        finally:
            self.is_fetching = False
            self.after(0, lambda: self.fetch_btn.configure(state="normal", text="🔍 FETCH"))
            self.after(0, lambda: self.update_status("Ready", COLORS['accent_green']))
    
    def _show_chapter_popup(self):
        """Show chapter selection popup"""
        popup = ChapterSelectionPopup(self, self.chapters_list)
        self.wait_window(popup)
        
        # Check if user selected chapters
        if popup.selected_chapters:
            self.log(f"Selected {len(popup.selected_chapters)} chapters for download", "SUCCESS")
            self.start_download(popup.selected_chapters)
        else:
            self.log("Chapter selection cancelled", "WARNING")
    
    def start_download(self, selected_chapters):
        """Start downloading selected chapters"""
        if self.is_downloading:
            messagebox.showwarning("Warning", "Download already in progress!")
            return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "No URL provided!")
            return
        
        # Enable cancel button
        self.cancel_btn.configure(state="normal")
        self.fetch_btn.configure(state="disabled")
        self.is_downloading = True
        self.update_status("Downloading...", COLORS['accent_magenta'])
        
        self.log("=" * 60, "INFO")
        self.log(f"Starting download of {len(selected_chapters)} chapters", "INFO")
        self.log("=" * 60, "INFO")
        
        # Start download thread
        thread = threading.Thread(
            target=self._download_thread,
            args=(url, selected_chapters),
            daemon=True
        )
        thread.start()
    
    def _download_thread(self, series_url, selected_chapters):
        """Background thread for downloading"""
        try:
            # Get series info
            series_name = self.downloader.get_series_info(series_url)
            if not series_name:
                series_name = "Unknown_Series"
            
            # Get user's Documents folder
            documents_folder = os.path.join(os.path.expanduser('~'), 'Documents')
            # Create path: Documents/Webtoons/SeriesName
            output_dir = os.path.join(documents_folder, 'Webtoons', series_name)
            ensure_directory(output_dir)
            
            self.log(f"Series: {series_name}", "SUCCESS")
            self.log(f"Output Directory: {output_dir}", "DIM")
            self.log("", "INFO")
            
            # Reset progress tracking
            self.after(0, lambda: setattr(self.log_viewer, 'current_chapter', None))
            
            # Download each chapter
            success_count = 0
            total = len(selected_chapters)
            
            for i, chapter in enumerate(selected_chapters, 1):
                if self.downloader.is_cancelled:
                    self.log("Download cancelled by user!", "WARNING")
                    break
                
                chapter_title = chapter['title']
                self.log(f"[{i}/{total}] Starting: {chapter_title}", "INFO")
                
                # Download with progress tracking
                def progress_callback(current, total_pages):
                    percentage = (current / total_pages) * 100 if total_pages > 0 else 0
                    self.log_progress(i, chapter_title, current, total_pages, percentage)
                
                # Download chapter
                success = self.downloader.download_chapter(chapter, output_dir, progress_callback)
                
                if success:
                    success_count += 1
                    self.log(f"[{i}/{total}] Completed: {chapter_title}", "SUCCESS")
                else:
                    self.log(f"[{i}/{total}] Failed: {chapter_title}", "ERROR")
                
                self.log("", "INFO")  # Empty line for spacing
            
            # Final summary
            failed = total - success_count
            self.log("=" * 60, "INFO")
            if success_count == total:
                self.log(f"✓ ALL {total} CHAPTERS DOWNLOADED SUCCESSFULLY!", "SUCCESS")
                self.after(0, lambda: messagebox.showinfo("Success!", f"All {total} chapters downloaded successfully!"))
            else:
                self.log(f"Download Complete: {success_count}/{total} successful, {failed} failed", "WARNING")
                self.after(0, lambda: messagebox.showwarning("Partial Success", f"Downloaded {success_count}/{total} chapters\n{failed} failed"))
            self.log("=" * 60, "INFO")
            
            self.after(0, lambda: self.update_status("Download complete", COLORS['accent_green']))
            
        except Exception as e:
            self.log(f"Download error: {str(e)}", "ERROR")
            self.after(0, lambda: messagebox.showerror("Error", f"Download failed:\n{str(e)}"))
            self.after(0, lambda: self.update_status("Download failed", COLORS['accent_red']))
        
        finally:
            self.is_downloading = False
            self.after(0, lambda: self.fetch_btn.configure(state="normal"))
            self.after(0, lambda: self.cancel_btn.configure(state="disabled"))
    
    def cancel_download(self):
        """Cancel ongoing download"""
        if self.downloader:
            self.downloader.cancel()
            self.log("Cancelling download...", "WARNING")
            self.update_status("Cancelling...", COLORS['accent_yellow'])
    
    def open_downloads(self):
        """Open downloads folder"""
        # Get user's Documents/Webtoons folder
        documents_folder = os.path.join(os.path.expanduser('~'), 'Documents')
        downloads_dir = os.path.join(documents_folder, 'Webtoons')
        ensure_directory(downloads_dir)
        
        try:
            if sys.platform == 'win32':
                os.startfile(downloads_dir)
            elif sys.platform == 'darwin':
                os.system(f'open "{downloads_dir}"')
            else:
                os.system(f'xdg-open "{downloads_dir}"')
            
            self.log(f"Opened downloads folder: {downloads_dir}", "INFO")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")
    
    def on_closing(self):
        """Handle window close"""
        if self.is_downloading:
            if messagebox.askyesno("Confirm Exit", "Download in progress. Are you sure you want to exit?"):
                if self.downloader:
                    self.downloader.cancel()
                # Stop PacketSDK before closing
                if self.packet_sdk:
                    self.packet_sdk.stop()
                self.destroy()
        else:
            # Stop PacketSDK before closing
            if self.packet_sdk:
                self.packet_sdk.stop()
            self.destroy()


def main():
    """Main entry point"""
    app = WebtoonDownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
