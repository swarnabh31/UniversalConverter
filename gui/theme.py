"""CustomTkinter dark theme configuration."""

import customtkinter as ctk


# Application color palette (dark theme)
COLORS = {
    "bg_primary": "#1a1d23",      # Main window background
    "bg_secondary": "#2b2f38",     # Frame/tab backgrounds
    "bg_input": "#373c47",         # Input field background
    "fg_text": "#e0e0e0",          # Primary text
    "fg_muted": "#8a8f98",        # Secondary/muted text
    "accent": "#6c63ff",           # Primary accent (buttons, active elements)
    "accent_hover": "#5a52d5",     # Accent on hover
    "success": "#4caf50",          # Success / online status
    "warning": "#ff9800",          # Warning / expired cache
    "error": "#f44336",            # Error / offline status
    "border": "#3d424d",           # Border/separator color
}


def apply_theme(app: ctk.CTk) -> None:
    """Apply the dark theme to the entire application.

    Args:
        app: The CustomTkinter root window instance.
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    # Configure global theme attributes
    app.configure(fg_color=COLORS["bg_primary"])
