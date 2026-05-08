#!/usr/bin/env python3
import logging
import os
import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

from bot.client import BinanceFuturesClient
from bot.exceptions import ConfigurationError, TradingBotError
from bot.logging_config import setup_logging
from bot.orders import OrderManager

load_dotenv()
setup_logging()
logger = logging.getLogger("trading_bot")

app = typer.Typer(
    name="trading-bot",
    help="Binance Futures Testnet Trading Bot",
    add_completion=False,
)
console = Console()


def _get_client() -> BinanceFuturesClient:
    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
    if not api_key or not api_secret:
        raise ConfigurationError(
            "API credentials not found. Set BINANCE_TESTNET_API_KEY and "
            "BINANCE_TESTNET_API_SECRET in .env"
        )
    return BinanceFuturesClient(api_key, api_secret)


def _get_order_manager() -> OrderManager:
    return OrderManager(_get_client())


def _render_order_table(title, data, style):
    table = Table(title=title, style=style)
    table.add_column("Field", style="yellow")
    table.add_column("Value", style="white")
    for key, value in data.items():
        if value is not None:
            table.add_row(key.replace("_", " ").title(), str(value))
    return table


@app.command()
def place_order(
    symbol: str = typer.Argument(..., help="Trading pair (e.g. BTCUSDT)"),
    side: str = typer.Argument(..., help="Side: BUY or SELL"),
    order_type: str = typer.Argument(..., help="Type: MARKET or LIMIT"),
    quantity: float = typer.Argument(..., help="Order quantity"),
    price: Optional[float] = typer.Option(
        None,
        "--price",
        "-p",
        help="Price (required for LIMIT orders)",
    ),
):
    """Place an order directly via CLI arguments."""
    try:
        manager = _get_order_manager()

        summary = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity,
        }
        if order_type.upper() == "LIMIT":
            summary["price"] = price

        console.print(_render_order_table("Order Request", summary, "cyan"))
        console.print()

        if not Confirm.ask("Confirm order?"):
            console.print("[yellow]Order cancelled.[/yellow]")
            raise typer.Exit()

        response = manager.place_order(symbol, side, order_type, quantity, price)
        console.print(_render_order_table("Order Response", response, "green"))

    except TradingBotError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
    except typer.Exit:
        raise
    except Exception as e:
        logger.exception("Unexpected CLI error")
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def interactive():
    """Step-by-step guided order placement."""
    console.print(
        Panel.fit(
            "[bold cyan]Binance Futures Testnet Trading Bot[/bold cyan]\n"
            "[white]Interactive Order Placement[/white]",
            border_style="cyan",
        )
    )
    console.print()

    try:
        symbol = (
            Prompt.ask("[yellow]Symbol[/yellow]", default="BTCUSDT").strip().upper()
        )

        side = Prompt.ask(
            "[yellow]Side[/yellow]", choices=["BUY", "SELL"], default="BUY"
        )

        order_type = Prompt.ask(
            "[yellow]Order type[/yellow]", choices=["MARKET", "LIMIT"], default="MARKET"
        )

        while True:
            try:
                qty_in = Prompt.ask("[yellow]Quantity[/yellow]")
                quantity = float(qty_in)
                if quantity <= 0:
                    console.print("[red]Quantity must be > 0.[/red]")
                    continue
                break
            except ValueError:
                console.print("[red]Enter a valid number.[/red]")

        price = None
        if order_type == "LIMIT":
            while True:
                try:
                    p_in = Prompt.ask("[yellow]Price[/yellow]")
                    price = float(p_in)
                    if price <= 0:
                        console.print("[red]Price must be > 0.[/red]")
                        continue
                    break
                except ValueError:
                    console.print("[red]Enter a valid number.[/red]")

        console.print()
        summary = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if price:
            summary["price"] = price
        console.print(_render_order_table("Order Summary", summary, "cyan"))
        console.print()

        if not Confirm.ask("[yellow]Place this order?[/yellow]"):
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit()

        manager = _get_order_manager()
        response = manager.place_order(symbol, side, order_type, quantity, price)
        console.print(_render_order_table("Order Response", response, "green"))

    except TradingBotError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
    except typer.Exit:
        raise
    except Exception as e:
        logger.exception("Unexpected error in interactive mode")
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def gui():
    """Launch the desktop GUI."""
    try:
        from gui.app import main as gui_main

        gui_main()
    except ImportError as e:
        console.print("[red]GUI dependencies missing or error: %s[/red]" % e)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
