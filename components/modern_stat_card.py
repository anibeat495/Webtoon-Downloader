"""
Modern Mini Stat Card Component
"""
import customtkinter as ctk


def create_mini_stat_card(parent, title, value, accent_color):
    """
    Create a modern mini statistics card
    
    Args:
        parent: Parent widget
        title (str): Card title
        value (str): Initial value
        accent_color (str): Accent color for the card
        
    Returns:
        dict: Dictionary containing frame and value_label for updates
    """
    # Card frame
    card = ctk.CTkFrame(
        parent,
        corner_radius=10,
        fg_color="#2a2d3a",
        border_width=0
    )
    
    # Accent bar on top
    accent_bar = ctk.CTkFrame(
        card,
        height=3,
        corner_radius=0,
        fg_color=accent_color
    )
    accent_bar.pack(fill="x", padx=0, pady=0)
    
    # Content area
    content = ctk.CTkFrame(card, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=12, pady=12)
    
    # Value (large number)
    value_label = ctk.CTkLabel(
        content,
        text=value,
        font=("Segoe UI", 24, "bold"),
        text_color="#ffffff"
    )
    value_label.pack(pady=(0, 2))
    
    # Title (small text)
    title_label = ctk.CTkLabel(
        content,
        text=title,
        font=("Segoe UI", 10),
        text_color="#9ca3af"
    )
    title_label.pack()
    
    # Return object with methods
    class StatCard:
        def __init__(self, frame, val_label):
            self.frame = frame
            self.value_label = val_label
        
        def set_value(self, new_value):
            self.value_label.configure(text=str(new_value))
        
        def grid(self, **kwargs):
            self.frame.grid(**kwargs)
        
        def pack(self, **kwargs):
            self.frame.pack(**kwargs)
    
    return StatCard(card, value_label)
