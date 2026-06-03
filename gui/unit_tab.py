"""Unit Converter tab widget for CustomTkinter."""

import customtkinter as ctk
from converters.unit_converter import UnitConverter
from utils.clipboard_helper import copy_to_clipboard


class UnitTab(ctk.CTkFrame):
    """GUI tab for physical unit conversion."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, fg_color="#2b2f38")

        self.converter = UnitConverter()
        self.current_category = ctk.StringVar(value="Length")

        # Current unit codes (not display names) for conversion logic
        self._from_code = None
        self._to_code = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the unit converter UI layout."""
        # Title
        title_label = ctk.CTkLabel(
            self, text="Unit Converter",
            font=ctk.CTkFont(size=22, weight="bold"),
            fg_color="transparent",
            text_color="#e0e0e0"
        )
        title_label.pack(padx=20, pady=(15, 10), anchor="w")

        # ── Category selector (compact dropdown) ──────────────────────
        cat_frame = ctk.CTkFrame(self, fg_color="#373c47", corner_radius=10)
        cat_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(
            cat_frame, text="Category:", font=ctk.CTkFont(size=13),
            fg_color="transparent", text_color="#8a8f98"
        ).pack(side="left", padx=(15, 0), pady=(12, 0))

        categories = list(self.converter.CATEGORIES.keys())
        self.cat_var = ctk.StringVar(value=categories[0])
        cat_combo = ctk.CTkComboBox(
            cat_frame, values=categories, width=340, height=34,
            font=ctk.CTkFont(size=13), variable=self.cat_var,
            command=self._on_category_change
        )
        cat_combo.pack(side="left", padx=(8, 0))

        # ── Unit selectors (from / to) ────────────────────────────────
        self.cat_frame = ctk.CTkFrame(self, fg_color="#373c47", corner_radius=10)
        self.cat_frame.pack(padx=20, pady=(0, 8), fill="x")

        # (filled by _on_category_change)
        self._on_category_change(categories[0])

        # ── Input amount ──────────────────────────────────────────────
        input_frame = ctk.CTkFrame(self, fg_color="#373c47", corner_radius=10)
        input_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(
            input_frame, text="Amount:", font=ctk.CTkFont(size=14),
            fg_color="transparent", text_color="#8a8f98"
        ).pack(side="left", padx=(15, 0), pady=(12, 0))

        self.amount_entry = ctk.CTkEntry(
            input_frame, placeholder_text="Enter value",
            font=ctk.CTkFont(size=16), width=200, height=40
        )
        self.amount_entry.pack(side="left", padx=(10, 15), pady=8, expand=True)
        self.amount_entry.bind("<KeyRelease>", self._on_input_change)

        # ── Result row ────────────────────────────────────────────────
        result_frame = ctk.CTkFrame(self, fg_color="#373c47", corner_radius=10)
        result_frame.pack(padx=20, pady=(0, 8), fill="x")

        self.result_label = ctk.CTkLabel(
            result_frame, text="Result: —",
            font=ctk.CTkFont(size=16, weight="bold"), fg_color="transparent", text_color="#6c63ff"
        )
        self.result_label.pack(side="left", padx=(15, 0), pady=(12, 0))

        copy_btn = ctk.CTkButton(
            result_frame, text="Copy", width=60, height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#6c63ff", hover_color="#5a52d5",
            corner_radius=6, command=self._copy_result
        )
        copy_btn.pack(side="right", padx=(0, 15), pady=(12, 0))

    def _on_category_change(self, category: str) -> None:
        """Handle category switch — rebuild unit selectors."""
        # Clear old frame and rebuild with new units
        for w in self.cat_frame.winfo_children():
            w.destroy()

        units = self.converter.get_units(category)
        display_names = [self.converter.get_unit_code_display(u) for u in units]

        ctk.CTkLabel(
            self.cat_frame, text="From:", font=ctk.CTkFont(size=13),
            fg_color="transparent", text_color="#8a8f98"
        ).pack(side="left", padx=(15, 0), pady=(12, 0))

        # Store actual codes for conversion logic
        self._from_codes = dict(zip(display_names, units))
        self.from_var = ctk.StringVar(value=units[0])
        self._from_code = units[0]
        from_combo = ctk.CTkComboBox(
            self.cat_frame, values=display_names, width=180, height=34,
            font=ctk.CTkFont(size=12), command=self._rebuild_from, variable=self.from_var
        )
        from_combo.pack(side="left", padx=(5, 0))

        ctk.CTkLabel(
            self.cat_frame, text="To:", font=ctk.CTkFont(size=13),
            fg_color="transparent", text_color="#8a8f98"
        ).pack(side="left", padx=(20, 0), pady=(12, 0))

        self._to_codes = dict(zip(display_names, units))
        to_default = units[-1] if len(units) > 1 else units[0]
        self.to_var = ctk.StringVar(value=to_default)
        self._to_code = to_default
        to_combo = ctk.CTkComboBox(
            self.cat_frame, values=display_names, width=180, height=34,
            font=ctk.CTkFont(size=12), command=self._rebuild_to, variable=self.to_var
        )
        to_combo.pack(side="left", padx=(5, 0))

    def _rebuild_from(self, _val: str = None) -> None:
        """Re-trigger conversion after 'from' unit change."""
        self._from_code = self._from_codes.get(self.from_var.get())
        self._convert()

    def _rebuild_to(self, _val: str = None) -> None:
        """Re-trigger conversion after 'to' unit change."""
        self._to_code = self._to_codes.get(self.to_var.get())
        self._convert()

    def _on_input_change(self, _event) -> None:
        """Handle input field changes — trigger real-time conversion."""
        self._convert()

    def _convert(self) -> None:
        """Perform the current conversion and update the result label."""
        try:
            # Update from/to codes in case dropdown changed mid-edit
            self._from_code = self._from_codes.get(self.from_var.get())
            self._to_code = self._to_codes.get(self.to_var.get())

            amount_str = self.amount_entry.get().strip()
            if not amount_str:
                self.result_label.configure(text_color="#6c63ff", text="Result: —")
                return

            value = float(amount_str)
            if value > 1e15 or value < -1e15:
                self.result_label.configure(
                    text_color="#f44336",
                    text="Result: Value too large (max: 1e15)"
                )
                return

            from_code = self._from_codes.get(self.from_var.get())
            to_code = self._to_codes.get(self.to_var.get())

            if not from_code or not to_code:
                self.result_label.configure(text_color="#8a8f98", text="Result: Select units")
                return

            result = self.converter.convert(value, from_code, to_code)

            # Get display labels for both source and target units
            from_display = self.converter.get_unit_code_display(from_code)
            to_display = self.converter.get_unit_code_display(to_code)

            self.result_label.configure(
                text_color="#6c63ff",
                text=f"Result: {value} {from_display} = {result} {to_display}"
            )

        except ValueError as e:
            error_msg = str(e).replace("'", "")
            self.result_label.configure(text_color="#f44336", text=f"Error: {error_msg}")
        except Exception:
            self.result_label.configure(
                text_color="#8a8f98",
                text="Result: Enter a valid number"
            )

    def _copy_result(self) -> None:
        """Copy the result text to clipboard."""
        text = self.result_label.cget("text")
        if text and text != "Result: —":
            copy_to_clipboard(text)
