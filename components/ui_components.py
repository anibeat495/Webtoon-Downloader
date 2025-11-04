"""
Custom UI Components with animations
"""
import customtkinter as ctk
import threading
import time


class AnimatedProgressBar(ctk.CTkFrame):
    """Modern thin animated progress bar with percentage label"""
    
    def __init__(self, master, height=8, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Container for progress bar and percentage on same line
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x")
        
        # Progress bar container
        progress_container = ctk.CTkFrame(container, fg_color="transparent")
        progress_container.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.progress = ctk.CTkProgressBar(
            progress_container,
            mode="determinate",
            height=height,
            corner_radius=4,
            border_width=0,
            fg_color="#374151",  # Track color
            progress_color="#5b9cf5"  # Bar color
        )
        self.progress.pack(fill="x")
        self.progress.set(0)
        
        # Percentage label on the right
        self.label = ctk.CTkLabel(
            container,
            text="0%",
            font=("Segoe UI", 11, "bold"),
            text_color="#9ca3af",
            width=45
        )
        self.label.pack(side="right")
        
        self.animating = False
        self.animation_thread = None
    
    def set(self, value):
        """Set progress value (0-1)"""
        self.progress.set(value)
        percentage = int(value * 100)
        self.label.configure(text=f"{percentage}%")
    
    def get(self):
        """Get current progress value"""
        return self.progress.get()
    
    def start_pulse(self):
        """Start pulsing animation for indeterminate progress"""
        if not self.animating:
            self.animating = True
            self.animation_thread = threading.Thread(target=self._pulse_animation, daemon=True)
            self.animation_thread.start()
    
    def stop_pulse(self):
        """Stop pulsing animation"""
        self.animating = False
    
    def _pulse_animation(self):
        """Pulse animation effect"""
        direction = 1
        value = 0
        
        while self.animating:
            value += direction * 0.02
            if value >= 1:
                value = 1
                direction = -1
            elif value <= 0:
                value = 0
                direction = 1
            
            try:
                self.progress.set(value)
            except:
                break
            
            time.sleep(0.03)


class StatusBadge(ctk.CTkLabel):
    """Animated status badge"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            corner_radius=10,
            font=("Roboto", 11, "bold"),
            padx=15,
            pady=5
        )
        self.set_status("ready")
    
    def set_status(self, status):
        """
        Set status with appropriate color
        
        Args:
            status (str): Status type - 'ready', 'working', 'success', 'error'
        """
        status_config = {
            'ready': {
                'text': '⚪ Ready',
                'fg_color': ('gray70', 'gray30'),
                'text_color': ('gray10', 'gray90')
            },
            'working': {
                'text': '🔵 Working...',
                'fg_color': ('#3498db', '#2980b9'),
                'text_color': 'white'
            },
            'success': {
                'text': '✅ Success',
                'fg_color': ('#27ae60', '#229954'),
                'text_color': 'white'
            },
            'error': {
                'text': '❌ Error',
                'fg_color': ('#e74c3c', '#c0392b'),
                'text_color': 'white'
            }
        }
        
        config = status_config.get(status, status_config['ready'])
        self.configure(**config)


class ChapterCard(ctk.CTkFrame):
    """Modern minimal card for displaying chapter with checkbox"""
    
    def __init__(self, master, chapter_number, chapter_title, variable, **kwargs):
        super().__init__(
            master,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color="#374151",
            **kwargs
        )
        
        self.variable = variable
        self.default_border = "#374151"
        self.hover_border = "#5b9cf5"
        
        # Main container with padding
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=12, pady=10)
        
        # Checkbox with modern styling
        self.checkbox = ctk.CTkCheckBox(
            self.container,
            text="",
            variable=variable,
            width=20,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=6,
            fg_color="#5b9cf5",
            hover_color="#4a8ae5",
            border_color="#374151"
        )
        self.checkbox.pack(side="left", padx=(0, 12))
        
        # Chapter info container
        self.info_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.info_frame.pack(side="left", fill="both", expand=True)
        
        # Chapter number badge
        self.number_label = ctk.CTkLabel(
            self.info_frame,
            text=f"#{chapter_number}",
            font=("Segoe UI", 10, "bold"),
            text_color="#5b9cf5",
            width=45,
            anchor="w"
        )
        self.number_label.pack(side="left", padx=(0, 12))
        
        # Chapter title
        self.title_label = ctk.CTkLabel(
            self.info_frame,
            text=chapter_title,
            font=("Segoe UI", 11),
            text_color="#ffffff",
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True)
        
        # Hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.container.bind("<Enter>", self._on_enter)
        self.container.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Mouse enter effect - subtle highlight"""
        self.configure(
            fg_color="#2a2d3a",
            border_color=self.hover_border
        )
    
    def _on_leave(self, event):
        """Mouse leave effect"""
        self.configure(
            fg_color="transparent",
            border_color=self.default_border
        )


class AnimatedButton(ctk.CTkButton):
    """Button with hover animation"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store original colors
        self._fg_color = kwargs.get('fg_color', ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self._hover_color = kwargs.get('hover_color', ctk.ThemeManager.theme["CTkButton"]["hover_color"])
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Scale up slightly on hover"""
        self.configure(height=self.cget("height") + 2)
    
    def _on_leave(self, event):
        """Scale back on leave"""
        self.configure(height=self.cget("height") - 2)


class LogViewer(ctk.CTkTextbox):
    """Custom log viewer with color-coded messages"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure tags for different log levels
        self.tag_config("INFO", foreground="#3498db")
        self.tag_config("SUCCESS", foreground="#27ae60")
        self.tag_config("WARNING", foreground="#f39c12")
        self.tag_config("ERROR", foreground="#e74c3c")
        
        self.configure(state="disabled")
    
    def add_log(self, message, level="INFO"):
        """
        Add a log message with color coding
        
        Args:
            message (str): Log message
            level (str): Log level (INFO, SUCCESS, WARNING, ERROR)
        """
        timestamp = time.strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{level}] {message}\n"
        
        self.configure(state="normal")
        self.insert("end", formatted_msg)
        self.see("end")
        self.configure(state="disabled")
    
    def clear(self):
        """Clear all logs"""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


class StatCard(ctk.CTkFrame):
    """Animated statistics card"""
    
    def __init__(self, master, title, icon="📊", **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        
        self.configure(fg_color=("#f0f0f0", "#2b2b2b"))
        
        # Icon
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Roboto", 32)
        )
        self.icon_label.pack(pady=(15, 5))
        
        # Value
        self.value_label = ctk.CTkLabel(
            self,
            text="0",
            font=("Roboto", 28, "bold")
        )
        self.value_label.pack(pady=5)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Roboto", 12),
            text_color="gray70"
        )
        self.title_label.pack(pady=(0, 15))
    
    def set_value(self, value):
        """
        Set the displayed value
        
        Args:
            value: Value to display
        """
        self.value_label.configure(text=str(value))
    
    def animate_to_value(self, target_value):
        """
        Animate counting to target value
        
        Args:
            target_value (int): Target value to count to
        """
        def animate():
            current = 0
            step = max(1, target_value // 20)
            
            while current < target_value:
                current = min(current + step, target_value)
                self.value_label.configure(text=str(current))
                time.sleep(0.05)
        
        threading.Thread(target=animate, daemon=True).start()


class GradientFrame(ctk.CTkFrame):
    """Frame with gradient-like appearance using layers"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Create layered effect
        self.configure(
            corner_radius=15,
            border_width=2,
            border_color=("#3498db", "#2980b9")
        )
