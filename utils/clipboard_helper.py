"""Cross-platform clipboard utility."""


def copy_to_clipboard(text: str) -> bool:
    """Copy text to the system clipboard.

    Uses tkinter's built-in clipboard which works cross-platform without extra deps.

    Args:
        text: The string to copy.

    Returns:
        True if successful, False otherwise.
    """
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.clipboard_clear()
        root.clipboard_append(text)
        root.destroy()
        return True
    except Exception:
        # Fallback: platform-specific approach
        try:
            import platform
            system = platform.system().lower()
            if system == "darwin":  # macOS
                import subprocess
                proc = subprocess.run(["pbcopy"], input=text.encode(), capture_output=True)
                return proc.returncode == 0
            elif system == "windows":  # Windows
                import subprocess
                proc = subprocess.run(["clip"], input=text.encode(), capture_output=True)
                return proc.returncode == 0
            else:  # Linux
                import subprocess
                proc = subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), capture_output=True)
                return proc.returncode == 0
        except Exception:
            return False
