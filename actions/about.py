# -*- coding: utf-8 -*-
"""About action — project info, features, requirements for Crypto Checker."""

from rich.table import Table
from rich.panel import Panel
from rich import box

from scanner.ui import console


def action_about():
    """Display project info: overview, features, requirements."""
    features_table = Table(
        show_header=True,
        header_style="bold bright_blue",
        border_style="blue",
        box=box.SIMPLE,
        title="[bold bright_blue] ◈ FEATURES ◈ [/]",
        title_style="bright_blue",
    )
    features_table.add_column("Feature", style="bright_blue")
    features_table.add_column("Status", justify="center", style="bright_green")

    for feat in [
        "Multi-chain balance lookup (EVM, BTC, SOL)",
        "Batch address checking with async engine",
        "Portfolio analytics and value aggregation",
        "Transaction history with filtering",
        "Export to CSV, JSON, PDF, HTML",
        "Configurable RPC endpoints per chain",
        "Explorer API key integration",
        "Real-time price conversion (CoinGecko)",
        "Rich terminal UI with color-coded output",
        "Cross-platform support (Win/Linux/macOS)",
        "Local-only processing, no telemetry",
        "Historical portfolio snapshots",
    ]:
        features_table.add_row(feat, "✓")

    setup_table = Table(
        show_header=True,
        header_style="bold bright_cyan",
        border_style="cyan",
        box=box.MINIMAL_HEAVY_HEAD,
        title="[bold bright_cyan] ◈ REQUIREMENTS & SETUP ◈ [/]",
        title_style="bright_cyan",
    )
    setup_table.add_column("Item", style="bright_blue")
    setup_table.add_column("Note", style="dim")
    setup_table.add_row("Python", "3.10 or higher")
    setup_table.add_row("pip", "Latest version recommended")
    setup_table.add_row("Libraries", "rich, web3, requests, aiohttp, tabulate")
    setup_table.add_row("Install", "pip install -r requirements.txt")
    setup_table.add_row("Run", "python main.py")
    setup_table.add_row("RPC Nodes", "Per-chain endpoints (Alchemy, Infura, public)")
    setup_table.add_row("API Keys", "Optional — Etherscan, BscScan, etc.")

    console.print()
    console.print(Panel(features_table, border_style="blue", box=box.ROUNDED))
    console.print()
    console.print(Panel(setup_table, border_style="cyan", box=box.ROUNDED))
    console.print()
    console.print(
        "[dim]Crypto Checker — multi-chain wallet balance checker with portfolio analytics. "
        "Configure RPC endpoints in Settings to begin.[/]"
    )
    console.print()
    console.print("[dim]Contact:[/] [bright_blue]0x7a3B1c9E45d82f06aD3e17C4b58F92d1A60cE834[/] (ETH/EVM)")
    console.print()
