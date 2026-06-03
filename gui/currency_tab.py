"""Currency Converter tab widget for CustomTkinter."""

import customtkinter as ctk
from converters.currency_converter import get_currency_converter, CurrencyConverter
from utils.clipboard_helper import copy_to_clipboard
from utils.network_check import is_online


# ── Currency symbol map ─────────────────────────────────────────────
CURRENCY_SYMBOLS = {
    "USD": "$", "EUR": chr(8364),   # euro sign
    "GBP": chr(163),                 # pound sign
    "INR": chr(2082),               # rupee sign (new)
    "JPY": chr(165),                # yen sign
    "AUD": "A$", "CAD": "C$", "CHF": "CHF",
}


class CurrencyTab(ctk.CTkFrame):
    """GUI tab for currency exchange rate conversion."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, fg_color="#2b2f38")

        self.converter = get_currency_converter()
        self.currencies = []
        self._refreshing = False

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the currency converter UI layout."""
        # Title + status row
        header_frame = ctk.CTkFrame(self, fg_color="#2b2f38", corner_radius=0)
        header_frame.pack(padx=20, pady=(15, 5), fill="x")

        title_label = ctk.CTkLabel(
            header_frame, text="Currency Converter",
            font=ctk.CTkFont(size=22, weight="bold"),
            fg_color="transparent", text_color="#e0e0e0"
        )
        title_label.pack(side="left", anchor="w")

        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            header_frame, text="● Loading...",
            font=ctk.CTkFont(size=11),
            fg_color="transparent", text_color="#8a8f98"
        )
        self.status_indicator.pack(side="right", anchor="e")

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            header_frame, text="Refresh", width=70, height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#373c47", hover_color="#4a4f5a",
            corner_radius=6, command=self._fetch_rates
        )
        self.refresh_btn.pack(side="right", padx=(8, 0))

        # Currency row (from + to)
        curr_frame = ctk.CTkFrame(self, fg_color="#373c47", corner_radius=10)
        curr_frame.pack(padx=20, pady=(5, 5), fill="x")

        ctk.CTkLabel(
            curr_frame, text="From:", font=ctk.CTkFont(size=13),
            fg_color="transparent", text_color="#8a8f98"
        ).pack(side="left", padx=(15, 0), pady=(12, 0))

        self.from_var = ctk.StringVar(value="USD")
        from_combo = ctk.CTkComboBox(
            curr_frame, values=["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF"], width=150, height=34,
            font=ctk.CTkFont(size=13), variable=self.from_var,
            command=lambda _v: self._convert()
        )
        from_combo.pack(side="left", padx=(5, 0))

        ctk.CTkLabel(
            curr_frame, text="To:", font=ctk.CTkFont(size=13),
            fg_color="transparent", text_color="#8a8f98"
        ).pack(side="left", padx=(25, 0), pady=(12, 0))

        self.to_var = ctk.StringVar(value="EUR")
        to_combo = ctk.CTkComboBox(
            curr_frame, values=["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF"], width=150, height=34,
            font=ctk.CTkFont(size=13), variable=self.to_var,
            command=lambda _v: self._convert()
        )
        to_combo.pack(side="left", padx=(5, 0))

        # Amount input
        amount_frame = ctk.CTkFrame(self, fg_color="#373c47", corner_radius=10)
        amount_frame.pack(padx=20, pady=(5, 5), fill="x")

        ctk.CTkLabel(
            amount_frame, text="Amount:", font=ctk.CTkFont(size=14),
            fg_color="transparent", text_color="#8a8f98"
        ).pack(side="left", padx=(15, 0), pady=(12, 0))

        self.amount_entry = ctk.CTkEntry(
            amount_frame, placeholder_text="Enter amount",
            font=ctk.CTkFont(size=16), width=200, height=40
        )
        self.amount_entry.pack(side="left", padx=(10, 15), pady=8, expand=True)
        self.amount_entry.bind("<KeyRelease>", self._on_input_change)

        # Result row
        result_frame = ctk.CTkFrame(self, fg_color="#373c47", corner_radius=10)
        result_frame.pack(padx=20, pady=(5, 5), fill="x")

        self.result_label = ctk.CTkLabel(
            result_frame, text="Result: --",
            font=ctk.CTkFont(size=16, weight="bold"), fg_color="transparent", text_color="#6c63ff"
        )
        self.result_label.pack(side="left", padx=(15, 0), pady=(12, 0))

        copy_btn = ctk.CTkButton(
            result_frame, text="Copy", width=60, height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#6c63ff", hover_color="#5a52d5",
            corner_radius=6, command=self._copy_result
        )
        copy_btn.pack(side="right", padx=(0, 15))

        # Rate info label
        self.rate_label = ctk.CTkLabel(
            result_frame, text="", font=ctk.CTkFont(size=11),
            fg_color="transparent", text_color="#8a8f98"
        )
        self.rate_label.pack(side="right", padx=(10, 0))

    def _convert(self) -> None:
        """Perform the currency conversion and update labels."""
        try:
            amount_str = self.amount_entry.get().strip()
            if not amount_str:
                self.result_label.configure(text_color="#6c63ff", text="Result: --")
                self.rate_label.configure(text="")
                return

            value = float(amount_str)
            if value < 0:
                self.result_label.configure(text_color="#f44336", text="Error: Negative amount")
                return

            from_ccy = self.from_var.get()
            to_ccy = self.to_var.get()

            if not from_ccy or not to_ccy:
                self.result_label.configure(text_color="#8a8f98", text="Result: Select currencies")
                return

            # Attempt conversion
            result = self.converter.convert(value, from_ccy, to_ccy)

            # ── Currency symbols (proper Unicode, not hardcoded) ────────
            symbol_from = CURRENCY_SYMBOLS.get(from_ccy, from_ccy)
            symbol_to   = CURRENCY_SYMBOLS.get(to_ccy, to_ccy)

            # Build result string: show BOTH amounts with correct symbols
            self.result_label.configure(
                text_color="#6c63ff",
                text=f"Result: {symbol_from}{value:,.2f} {from_ccy} => {symbol_to}{result:,.4f} {to_ccy}"
            )

            # ── Rate info (rate per 1 unit) ─────────────────────────────
            rate_str = ""
            if from_ccy != to_ccy:
                try:
                    from_rate = self.converter.get_rate(from_ccy) or 0
                    to_rate   = self.converter.get_rate(to_ccy) or 0

                    if from_ccy == "USD":
                        # show rate per 1 USD
                        rate_str = f"1 USD => {to_rate:.4f} {to_ccy}"
                    elif to_ccy == "USD":
                        # invert: how much 1 from_ccy is in USD
                        inv = 1.0 / from_rate if from_rate != 0 else 0
                        rate_str = f"1 {from_ccy} => {inv:.4f} USD"
                    else:
                        # cross-rate: both non-USD
                        cross = to_rate / from_rate if from_rate != 0 else 0
                        rate_str = f"1 {from_ccy} => {cross:.4f} {to_ccy}"
                except Exception:
                    rate_str = ""

            self.rate_label.configure(text=rate_str)

        except ValueError as e:
            error_msg = str(e).replace("'", "")
            self.result_label.configure(text_color="#f44336", text=f"Error: {error_msg[:50]}")
        except Exception:
            if self.converter.is_expired:
                self.result_label.configure(
                    text_color="#ff9800",
                    text="Result: Using expired cached rates (warning)"
                )
                self.rate_label.configure(text="Cached rates may be outdated")

    def _on_input_change(self, _event) -> None:
        """Trigger conversion on input change."""
        self._convert()

    def _fetch_rates(self) -> None:
        """Attempt to fetch fresh exchange rates from online API."""
        if self._refreshing:
            return
        self._refreshing = True
        self.refresh_btn.configure(state="disabled", text="Fetching...")
        self.status_indicator.configure(text_color="#ff9800", text="● Fetching...")

        # Check connectivity first
        online = is_online()
        if not online:
            self.status_indicator.configure(text_color="#f44336", text="● Offline")
            self.refresh_btn.configure(state="normal", text="Refresh")
            self._refreshing = False
            return

        try:
            # Attempt online fetch (may raise ConnectionError)
            fetched = self.converter.fetch_rates()
            if fetched:
                self.status_indicator.configure(text_color="#4caf50", text="● Online")
                # Update currency lists dynamically from live rates
                self.currencies = self.converter.get_units()
                if self.from_var.get() not in self.currencies:
                    self.from_var.set("USD")
                to_curr = self.to_var.get()
                if to_curr not in self.currencies and len(self.currencies) > 1:
                    self.to_var.set(self.currencies[1])
                # Trigger reconversion with new rates
                self._convert()
            else:
                raise ValueError("No rates returned")
        except (ConnectionError, ValueError) as e:
            error_msg = str(e)[:40]
            self.status_indicator.configure(text_color="#ff9800", text="● Using cache (warning)")
            if self.converter.is_expired:
                self.status_indicator.configure(text_color="#f44336", text="● Expired cache")
        finally:
            self.refresh_btn.configure(state="normal", text="Refresh")
            self._refreshing = False

    def _copy_result(self) -> None:
        """Copy the result text to clipboard."""
        text = self.result_label.cget("text")
        rate_text = self.rate_label.cget("text")
        full_text = f"{text}\n{rate_text}" if rate_text else text
        if text and text != "Result: --":
            copy_to_clipboard(full_text)
