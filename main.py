#!/usr/bin/env python3
"""Offline Unit & Currency Converter — Entry Point.

A desktop application for converting physical units and currency exchange rates.
Works fully offline with optional online rate updates via free APIs.

Usage:
    python main.py

Requirements:
    pip install requests customtkinter
"""

import sys
import os

# Ensure the converter package directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from gui.theme import apply_theme, COLORS
from gui.unit_tab import UnitTab
from gui.currency_tab import CurrencyTab


class App(ctk.CTk):
    """Main application window with tabbed converter interface."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Unit & Currency Converter")
        self.geometry("680x520")
        self.minsize(500, 400)

        # Center window on screen
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 680) // 2
        y = (screen_h - 520) // 2
        self.geometry(f"680x520+{x}+{y}")

        # Apply dark theme
        apply_theme(self)

        # Build the tabbed interface
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the main application UI."""
        # Main container frame
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Tab view
        self.tab_view = ctk.CTkTabview(
            main_frame,
            width=640,
            height=460,
            fg_color=COLORS["bg_primary"],
            segmented_button_fg_color=COLORS["bg_secondary"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["border"],
        )
        self.tab_view.pack(padx=20, pady=(15, 10), fill="both", expand=True)

        # Add tabs
        self.unit_tab = self.tab_view.add("Unit Converter")
        self.currency_tab = self.tab_view.add("Currency")

        # Fill tab frames with the actual widget content
        unit_frame = UnitTab(self.unit_tab)
        unit_frame.pack(fill="both", expand=True)

        curr_frame = CurrencyTab(self.currency_tab)
        curr_frame.pack(fill="both", expand=True)

        # Footer status bar
        footer = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_secondary"], height=24)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkLabel(
            footer, text="Offline-first • Rates refresh when online",
            font=ctk.CTkFont(size=10), fg_color="transparent", text_color=COLORS["fg_muted"]
        ).pack(pady=(3, 0))

    def on_closing(self) -> None:
        """Handle window close event."""
        self.destroy()


def main() -> None:
    """Application entry point."""
    app = App()

    # Handle graceful shutdown
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
