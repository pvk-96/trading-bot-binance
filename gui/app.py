import logging
import os
import threading

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from dotenv import load_dotenv

from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.logging_config import setup_logging
from bot.exceptions import TradingBotError

load_dotenv()
setup_logging()
logger = logging.getLogger("trading_bot")


class TradingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Binance Futures Testnet Trading Bot")
        self.root.geometry("620x680")
        self.root.resizable(False, False)

        self.client = None
        self.order_manager = None
        self._init_backend()
        self._build_ui()
        self._load_symbols()

    def _init_backend(self):
        api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
        if not api_key or not api_secret:
            logger.warning("API credentials not found in .env")
            return
        try:
            self.client = BinanceFuturesClient(api_key, api_secret)
            self.order_manager = OrderManager(self.client)
        except Exception as e:
            logger.error("Backend init failed: %s", e)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding="20")
        main.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            main, text="Binance Futures Testnet", font=("Helvetica", 16, "bold")
        )
        title.pack(pady=(0, 2))
        subtitle = ttk.Label(main, text="Trading Bot", font=("Helvetica", 12))
        subtitle.pack(pady=(0, 20))

        inp = ttk.Frame(main)
        inp.pack(fill=tk.X)

        # Row 0: Symbol
        ttk.Label(inp, text="Symbol:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.symbol_var = tk.StringVar(value="BTCUSDT")
        self.symbol_combo = ttk.Combobox(
            inp,
            textvariable=self.symbol_var,
            state="readonly",
            width=22,
        )
        self.symbol_combo.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Row 1: Side
        ttk.Label(inp, text="Side:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.side_var = tk.StringVar(value="BUY")
        self.side_combo = ttk.Combobox(
            inp,
            textvariable=self.side_var,
            values=["BUY", "SELL"],
            state="readonly",
            width=22,
        )
        self.side_combo.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Row 2: Order type
        ttk.Label(inp, text="Order Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value="MARKET")
        self.type_combo = ttk.Combobox(
            inp,
            textvariable=self.type_var,
            values=["MARKET", "LIMIT"],
            state="readonly",
            width=22,
        )
        self.type_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        # Row 3: Quantity
        ttk.Label(inp, text="Quantity:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.quantity_entry = ttk.Entry(inp, width=25)
        self.quantity_entry.grid(row=3, column=1, sticky=tk.W, pady=5)

        # Row 4: Price
        ttk.Label(inp, text="Price:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.price_entry = ttk.Entry(inp, width=25)
        self.price_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        self.price_entry.configure(state="disabled")

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(pady=20)

        self.submit_btn = ttk.Button(
            btn_frame,
            text="Submit Order",
            command=self._submit_order,
        )
        self.submit_btn.pack(side=tk.LEFT, padx=6)

        self.clear_btn = ttk.Button(
            btn_frame,
            text="Clear",
            command=self._clear,
        )
        self.clear_btn.pack(side=tk.LEFT, padx=6)

        # Response output
        ttk.Label(main, text="Response:", font=("Helvetica", 10, "bold")).pack(
            anchor=tk.W
        )
        self.response_text = scrolledtext.ScrolledText(
            main,
            height=13,
            width=72,
            state=tk.DISABLED,
            font=("Consolas", 9),
        )
        self.response_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def _on_type_change(self, event=None):
        if self.type_var.get() == "MARKET":
            self.price_entry.configure(state="disabled")
            self.price_entry.delete(0, tk.END)
        else:
            self.price_entry.configure(state="normal")

    def _load_symbols(self):
        if not self.client:
            defaults = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
            self.symbol_combo["values"] = defaults
            return
        try:
            info = self.client.get_exchange_info()
            symbols = [
                s["symbol"]
                for s in info.get("symbols", [])
                if s.get("status") == "TRADING"
            ]
            symbols.sort()
            self.symbol_combo["values"] = symbols
            if "BTCUSDT" in symbols:
                self.symbol_var.set("BTCUSDT")
        except Exception as e:
            logger.error("Failed to load symbols: %s", e)

    def _submit_order(self):
        if not self.order_manager:
            messagebox.showerror(
                "Error", "Backend not initialised. Check API credentials in .env"
            )
            return

        symbol = self.symbol_var.get().strip()
        side = self.side_var.get()
        order_type = self.type_var.get()
        quantity = self.quantity_entry.get().strip()
        price = self.price_entry.get().strip() if order_type == "LIMIT" else None

        if not quantity:
            messagebox.showerror("Error", "Quantity is required.")
            return
        try:
            qty_val = float(quantity)
            if qty_val <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a valid number.")
            return
        if order_type == "LIMIT" and not price:
            messagebox.showerror("Error", "Price is required for LIMIT orders.")
            return

        self.submit_btn.configure(state=tk.DISABLED, text="Placing…")
        self._append("Placing order…\n")

        threading.Thread(
            target=self._place_order_thread,
            args=(symbol, side, order_type, quantity, price),
            daemon=True,
        ).start()

    def _place_order_thread(self, symbol, side, order_type, quantity, price):
        try:
            response = self.order_manager.place_order(
                symbol,
                side,
                order_type,
                quantity,
                price,
            )
            self.root.after(0, self._on_success, response, order_type)
        except TradingBotError as e:
            self.root.after(0, self._on_error, str(e))
        except Exception as e:
            logger.exception("Unhandled error in order thread")
            self.root.after(0, self._on_error, f"Unexpected error: {e}")

    def _on_success(self, response, order_type):
        self.submit_btn.configure(state=tk.NORMAL, text="Submit Order")
        status = response.get("status", "N/A")
        executed = response.get("executed_qty", "0")
        avg_price = response.get("avg_price", "N/A")
        if order_type == "MARKET" and status in ("FILLED", "PARTIALLY_FILLED"):
            self._append("✓ MARKET order filled!\n\n")
        elif order_type == "MARKET" and status == "NEW":
            self._append("ℹ MARKET order placed (awaiting fill)\n\n")
        else:
            self._append("✓ Order placed successfully!\n\n")
        for key, value in response.items():
            if value is not None:
                label = key.replace("_", " ").title()
                self._append(f"{label}: {value}\n")
        self._append("\n" + "-" * 50 + "\n")
        msg = "Order placed successfully!"
        if order_type == "MARKET" and status == "FILLED":
            msg = f"MARKET order filled! Executed: {executed}, Avg price: {avg_price}"
        messagebox.showinfo("Success", msg)

    def _on_error(self, error):
        self.submit_btn.configure(state=tk.NORMAL, text="Submit Order")
        self._append(f"✗ Error: {error}\n\n")

    def _append(self, text):
        self.response_text.configure(state=tk.NORMAL)
        self.response_text.insert(tk.END, text)
        self.response_text.see(tk.END)
        self.response_text.configure(state=tk.DISABLED)

    def _clear(self):
        self.symbol_var.set("BTCUSDT")
        self.side_var.set("BUY")
        self.type_var.set("MARKET")
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.price_entry.configure(state="disabled")
        self.response_text.configure(state=tk.NORMAL)
        self.response_text.delete(1.0, tk.END)
        self.response_text.configure(state=tk.DISABLED)


def main():
    root = tk.Tk()
    TradingBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
