# -*- coding: utf-8 -*-
"""
Rich console UI components for Crypto Checker.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

console = Console()

VERSION = "2.2.0"
TITLE = "Crypto Checker"


def print_banner():
    console.print()
    console.print(
        Panel(
            f"[bold white]{TITLE}[/bold white] [dim]v{VERSION}[/dim]\n"
            "[dim]DeBank Bypass — Multi-Thread Address & Seed Scanner[/dim]",
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(1, 2),
        )
    )
    console.print()


def show_menu_table(menu_items):
    """Display menu table and return user choice."""
    table = Table(
        title=f"[bold cyan]{TITLE}[/bold cyan]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        title_style="bold white",
        show_header=True,
        header_style="bold bright_white",
        padding=(0, 2),
    )
    table.add_column("#", style="bold yellow", justify="center", width=4)
    table.add_column("Icon", style="white", justify="center", width=4)
    table.add_column("Action", style="white", min_width=30)
    table.add_column("Description", style="dim", min_width=30)

    for idx, icon, action, desc in menu_items:
        style = "bold red" if action.lower() == "exit" else "white"
        table.add_row(idx, icon, f"[{style}]{action}[/{style}]", desc)

    console.print()
    console.print(table)
    console.print()

    choice = console.input("[bold cyan]  Select option >[/] ").strip()
    return choice


def show_balance_table(balances):
    table = Table(
        title="[bold cyan]Balance Report[/bold cyan]",
        box=box.SIMPLE_HEAVY,
        border_style="cyan",
    )
    table.add_column("Chain", style="bold white", width=14)
    table.add_column("Balance", style="yellow", width=18)
    table.add_column("USD Value", justify="right", style="bold green", width=14)
    table.add_column("Tokens", justify="center", style="dim", width=18)

    for row in balances:
        table.add_row(*row)

    console.print(table)
    console.print()


def show_chain_table(chains):
    table = Table(
        title="[bold cyan]Chain Configuration[/bold cyan]",
        box=box.ROUNDED,
        border_style="dim",
    )
    table.add_column("Chain", style="bold white", width=14)
    table.add_column("Token", justify="center", style="yellow", width=10)
    table.add_column("RPC", style="dim", width=34)
    table.add_column("Status", justify="center", width=12)

    for c in chains:
        table.add_row(*c)

    console.print(table)
    console.print()


def show_export_table(formats):
    table = Table(
        title="[bold cyan]Export Formats[/bold cyan]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
    )
    table.add_column("Format", style="bold white", width=10)
    table.add_column("Extension", style="dim", width=12)
    table.add_column("Fields", style="white", width=36)
    table.add_column("Use Case", style="yellow", width=20)

    for row in formats:
        table.add_row(*row)

    console.print(table)
    console.print()


def show_portfolio_summary(records):
    table = Table(
        title="[bold cyan]Portfolio Summary[/bold cyan]",
        box=box.DOUBLE_EDGE,
        border_style="green",
    )
    table.add_column("Chain", style="bold white", width=14)
    table.add_column("Balance", style="yellow", width=18)
    table.add_column("USD", justify="right", style="bold green", width=14)
    table.add_column("Tokens", justify="center", style="dim", width=10)
    table.add_column("Share %", justify="right", style="cyan", width=10)

    for rec in records:
        table.add_row(*rec)

    console.print(table)
    console.print()


def show_proxy_pool_table(proxies):
    """Display proxy pool status table."""
    table = Table(
        title="[bold cyan]Proxy Pool Status[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
    )
    table.add_column("#", style="dim", justify="right", width=4)
    table.add_column("Proxy", style="bright_white", width=36)
    table.add_column("Type", style="cyan", width=8)
    table.add_column("Latency", justify="right", style="yellow", width=10)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Last Used", style="dim", width=12)

    for i, p in enumerate(proxies, 1):
        table.add_row(*p)

    console.print(table)
    console.print()


def show_seed_results_table(results):
    """Display seed phrase check results."""
    table = Table(
        title="[bold cyan]Seed Phrase Results[/bold cyan]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
    )
    table.add_column("#", style="dim", justify="right", width=4)
    table.add_column("Seed (preview)", style="bright_white", width=28)
    table.add_column("Chain", style="cyan", width=12)
    table.add_column("Address", style="bright_green", width=42)
    table.add_column("Balance", justify="right", style="yellow", width=16)
    table.add_column("USD", justify="right", style="bold green", width=14)
    table.add_column("Alert", justify="center", width=12)

    for r in results:
        table.add_row(*r)

    console.print(table)
    console.print()


def print_success(message):
    console.print(f"  [bold green]✓[/bold green] {message}")


def print_error(message):
    console.print(f"  [bold red]✗[/bold red] {message}")


def print_info(message):
    console.print(f"  [bold blue]ℹ[/bold blue] {message}")


def print_warning(message):
    console.print(f"  [bold yellow]⚠[/bold yellow] {message}")


def separator():
    console.print("[dim]─" * 60 + "[/dim]")


def progress_bar(description, total=100, transient=False):
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, complete_style="cyan", finished_style="bright_green"),
        TextColumn("[bold]{task.percentage:>3.0f}%"),
        console=console,
        transient=transient,
    )


def show_simple_list(title, items):
    """Display a simple list of items with a title."""
    if title:
        console.print(f"\n[bold cyan]{title}[/bold cyan]")
    for item in items:
        console.print(f"  [bright_white]•[/] {item}")
    console.print()
