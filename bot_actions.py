# -*- coding: utf-8 -*-
"""Bot actions for Crypto Checker — address checks, seed phrase scanning,
proxy management, portfolio summary, export, and chain configuration.

Realistic simulation layer with Rich output.
"""

import random
import time
from datetime import datetime

from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

from scanner.ui import (
    console,
    print_info,
    print_success,
    print_warning,
    print_error,
    separator,
)


_CHAINS = ["Ethereum", "Bitcoin", "Solana", "BNB Chain", "Polygon", "Arbitrum", "Avalanche", "Base"]
_TOKENS = {
    "Ethereum": ("ETH", 3500.0),
    "Bitcoin": ("BTC", 67000.0),
    "Solana": ("SOL", 150.0),
    "BNB Chain": ("BNB", 600.0),
    "Polygon": ("MATIC", 0.70),
    "Arbitrum": ("ETH", 3500.0),
    "Avalanche": ("AVAX", 35.0),
    "Base": ("ETH", 3500.0),
}

_SAMPLE_PROXIES = [
    "http://usr:px9a2k@185.22.18.41:8080",
    "socks5://usr:bq81mf@91.20.14.22:1080",
    "http://45.12.88.104:3128",
    "socks5://usr:zt34xc@104.21.55.7:1080",
    "http://usr:kp72df@192.168.44.12:8080",
]

_SAMPLE_SEEDS = [
    "abandon ability able about above absent absorb abstract absurd abuse access accident",
    "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
    "letter advice cage absurd amount doctor acoustic avoid letter advice cage above",
    "able absorb absurd abuse access accident account accuse across act action adult",
    "acid acoustic acquire across act action actor actress actual adapt add addict",
]


def _short_addr(addr: str) -> str:
    if not addr or len(addr) < 10:
        return addr or "unknown"
    return f"{addr[:6]}...{addr[-4:]}"


def _random_address(chain: str) -> str:
    if chain == "Bitcoin":
        return f"bc1q{random.randbytes(20).hex()[:38]}"
    elif chain == "Solana":
        return f"{random.randbytes(16).hex()[:32]}{random.randbytes(16).hex()[:12]}"
    else:
        return f"0x{random.randbytes(20).hex()}"


def _random_proxy() -> str:
    return random.choice(_SAMPLE_PROXIES)


def action_check_address(cfg: dict):
    """Check balance for a single address through proxy (simulation)."""
    address = cfg.get("last_address", _random_address("Ethereum"))
    proxy = _random_proxy()

    console.print()
    print_info(f"Target: [bright_cyan]{_short_addr(address)}[/]")
    print_info(f"Proxy:  [yellow]{proxy}[/]")
    separator()

    with Progress(
        SpinnerColumn(style="bright_blue"),
        TextColumn("[bright_blue]{task.description}"),
        BarColumn(bar_width=40, style="blue", complete_style="bright_green"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning via proxy...", total=5)
        for step_label in [
            f"Connecting through {proxy[:30]}...",
            "Querying native balances...",
            "Fetching token balances...",
            "Calculating USD values...",
            "Building report...",
        ]:
            progress.update(task, description=step_label)
            time.sleep(0.35)
            progress.advance(task)

    table = Table(
        show_header=True,
        header_style="bold bright_blue",
        border_style="blue",
        box=box.ROUNDED,
        title="[bold bright_blue] BALANCE REPORT [/]",
    )
    table.add_column("Chain", style="bright_cyan")
    table.add_column("Balance", justify="right", style="bright_white")
    table.add_column("USD Value", justify="right", style="bright_green")
    table.add_column("Tokens", justify="center", style="dim")

    total_usd = 0.0
    total_tokens = 0
    for chain in random.sample(_CHAINS, random.randint(3, 6)):
        symbol, price = _TOKENS[chain]
        balance = round(random.uniform(0.01, 50.0), 6)
        usd_val = balance * price
        tokens_count = random.randint(0, 20)
        total_usd += usd_val
        total_tokens += tokens_count
        table.add_row(chain, f"{balance:.6f} {symbol}", f"${usd_val:,.2f}", str(tokens_count))

    table.add_section()
    table.add_row("[bold]TOTAL[/]", "", f"[bold]${total_usd:,.2f}[/]", f"[bold]{total_tokens}[/]")

    console.print()
    console.print(table)
    console.print()
    print_success(f"Balance check complete via proxy {proxy[:30]}...")


def action_batch_check(cfg: dict):
    """Batch check multiple addresses multi-threaded through proxies (simulation)."""
    count = random.randint(5, 12)
    addresses = [_random_address(random.choice(_CHAINS)) for _ in range(count)]
    threads = cfg.get("scanner", {}).get("threads", 20)

    console.print()
    print_info(f"Batch checking {count} addresses with {threads} threads...")
    print_info(f"Proxy pool: {len(_SAMPLE_PROXIES)} proxies loaded")
    separator()

    with Progress(
        SpinnerColumn(style="bright_magenta"),
        TextColumn("[bright_magenta]{task.description}"),
        BarColumn(bar_width=40, style="magenta", complete_style="bright_green"),
        console=console,
    ) as progress:
        task = progress.add_task("Multi-thread scanning...", total=count)
        for i, addr in enumerate(addresses):
            proxy = _random_proxy()
            progress.update(task, description=f"[Thread-{i%threads+1:02d}] {_short_addr(addr)} via {proxy[:25]}...")
            time.sleep(0.25)
            progress.advance(task)
            if i % 3 == 0:
                console.print(f"  [dim]Proxy rotated: {proxy[:30]}...[/]")

    table = Table(
        show_header=True,
        header_style="bold bright_magenta",
        border_style="bright_cyan",
        box=box.ROUNDED,
        title="[bold bright_magenta] BATCH RESULTS [/]",
    )
    table.add_column("#", style="dim", justify="right", width=3)
    table.add_column("Address", style="bright_cyan")
    table.add_column("Chain", style="bright_blue")
    table.add_column("Balance", justify="right", style="bright_white")
    table.add_column("USD Value", justify="right", style="bright_green")
    table.add_column("Proxy", style="dim", width=20)
    table.add_column("Status", justify="center")

    total_usd = 0.0
    for i, addr in enumerate(addresses, 1):
        chain = random.choice(_CHAINS)
        symbol, price = _TOKENS[chain]
        balance = round(random.uniform(0.001, 100.0), 6)
        usd_val = balance * price
        total_usd += usd_val
        proxy_short = _random_proxy()[:22] + "..."
        status = "[bright_green]Active[/]" if random.random() > 0.2 else "[dim]Empty[/]"
        table.add_row(str(i), _short_addr(addr), chain, f"{balance:.6f} {symbol}",
                      f"${usd_val:,.2f}", proxy_short, status)

    console.print()
    console.print(table)
    console.print()
    print_success(f"Batch complete. Total portfolio value: [bold]${total_usd:,.2f}[/]")


def action_seed_check(cfg: dict):
    """Check seed phrases from file — multi-threaded through proxies (simulation)."""
    seed_cfg = cfg.get("seed_checker", {})
    seed_file = seed_cfg.get("seed_file", "seeds.txt")
    threads = seed_cfg.get("threads", 10)
    threshold = seed_cfg.get("highlight_threshold_usd", 10000)

    console.print()
    print_info(f"Loading proxy pool... {len(_SAMPLE_PROXIES) * 9} proxies loaded from proxies.txt")

    with Progress(
        SpinnerColumn(style="bright_cyan"),
        TextColumn("[bright_cyan]{task.description}"),
        BarColumn(bar_width=40, style="cyan", complete_style="bright_green"),
        console=console,
    ) as progress:
        task = progress.add_task("Validating proxies...", total=3)
        for label in [
            f"Loading proxies... {len(_SAMPLE_PROXIES) * 9} loaded",
            f"Validating proxies... {len(_SAMPLE_PROXIES) * 7}/{len(_SAMPLE_PROXIES) * 9} alive",
            "Proxy pool ready.",
        ]:
            progress.update(task, description=label)
            time.sleep(0.4)
            progress.advance(task)

    alive = len(_SAMPLE_PROXIES) * 7
    total_proxies = len(_SAMPLE_PROXIES) * 9
    print_info(f"Validating proxies... {alive}/{total_proxies} alive ({total_proxies - alive} dead removed)")

    seed_count = random.randint(120, 200)
    print_info(f"Loading seed phrases from {seed_file}... {seed_count} entries")
    print_info(f"Starting multi-thread scan (threads: {threads})")
    separator()

    results = []
    high_value_count = 0

    for i in range(min(12, seed_count)):
        seed = random.choice(_SAMPLE_SEEDS)
        seed_preview = seed[:12] + "..." + seed[-6:]
        thread_id = (i % threads) + 1
        proxy = _random_proxy()

        has_balance = random.random() > 0.4
        if has_balance:
            chain = random.choice(_CHAINS)
            symbol, price = _TOKENS[chain]
            balance = round(random.uniform(0.1, 300.0), 4)
            usd_val = balance * price
            addr = _random_address(chain)
            is_high = usd_val >= threshold
            if is_high:
                high_value_count += 1

            alert = "[bold red]⚠ HIGH VALUE[/]" if is_high else "[dim]—[/]"
            console.print(
                f"  [dim][Thread-{thread_id:02d}][/dim] {seed_preview} | "
                f"{chain}: {balance:.2f} {symbol} (${usd_val:,.0f}) | "
                f"{alert}"
            )
            results.append((str(i+1), seed_preview, chain, _short_addr(addr),
                           f"{balance:.4f} {symbol}", f"${usd_val:,.0f}", alert))
        else:
            console.print(
                f"  [dim][Thread-{thread_id:02d}][/dim] {seed_preview} | "
                f"[dim]All chains: 0.00 | Empty[/]"
            )

        if i % 4 == 0 and i > 0:
            new_proxy = _random_proxy()
            console.print(f"  [dim]Proxy rotated: {proxy[:28]}... → {new_proxy[:28]}...[/]")

        time.sleep(0.15)

    console.print()
    console.print(f"  [dim]... ({seed_count - 12} more seeds checked)[/]")
    console.print()

    summary = Table(
        show_header=False,
        border_style="bright_cyan",
        box=box.ROUNDED,
    )
    summary.add_column("Metric", style="bright_cyan")
    summary.add_column("Value", justify="right", style="bright_white")
    summary.add_row("Seeds Checked", str(seed_count))
    summary.add_row("Wallets with Balance", f"{high_value_count + random.randint(2, 5)}")
    summary.add_row(f"High Value (>${threshold:,})", f"[bold red]{high_value_count}[/]")
    summary.add_row("Proxies Used", f"{alive}")
    summary.add_row("Threads", str(threads))
    summary.add_row("Time", f"{random.uniform(45, 180):.0f} seconds")

    console.print(Panel(summary, border_style="bright_cyan",
                        title="[bold bright_cyan] SCAN SUMMARY [/]"))
    console.print()

    output_file = seed_cfg.get("output_file", "seed_results.txt")
    print_success(f"Results saved to results/{output_file}")


def action_proxy_manager(cfg: dict):
    """Show proxy pool, validate, display stats (simulation)."""
    proxy_cfg = cfg.get("proxies", {})
    mode = proxy_cfg.get("rotation_mode", "round-robin")

    console.print()
    print_info(f"Proxy rotation mode: [bright_cyan]{mode}[/]")
    separator()

    with Progress(
        SpinnerColumn(style="bright_green"),
        TextColumn("[bright_green]{task.description}"),
        BarColumn(bar_width=40, style="green", complete_style="bright_green"),
        console=console,
    ) as progress:
        task = progress.add_task("Validating proxy pool...", total=3)
        for label in [
            "Loading proxies from proxies.txt...",
            "Testing connectivity...",
            "Validation complete.",
        ]:
            progress.update(task, description=label)
            time.sleep(0.4)
            progress.advance(task)

    total = random.randint(40, 60)
    alive = total - random.randint(2, 8)
    dead = total - alive

    table = Table(
        show_header=True,
        header_style="bold bright_green",
        border_style="green",
        box=box.ROUNDED,
        title="[bold bright_green] PROXY POOL STATUS [/]",
    )
    table.add_column("#", style="dim", justify="right", width=4)
    table.add_column("Proxy", style="bright_white", width=38)
    table.add_column("Type", style="cyan", width=8)
    table.add_column("Latency", justify="right", style="yellow", width=10)
    table.add_column("Status", justify="center", width=10)

    for i in range(min(10, total)):
        proxy = _SAMPLE_PROXIES[i % len(_SAMPLE_PROXIES)]
        ptype = "SOCKS5" if "socks5" in proxy else "HTTP"
        latency = f"{random.randint(50, 350)} ms"
        is_alive = random.random() > 0.15
        status = "[bright_green]Alive[/]" if is_alive else "[red]Dead[/]"
        table.add_row(str(i+1), proxy, ptype, latency, status)

    if total > 10:
        table.add_row("...", f"[dim]({total - 10} more proxies)[/]", "", "", "")

    console.print()
    console.print(table)

    stats = Table(
        show_header=False,
        border_style="bright_green",
        box=box.SIMPLE,
    )
    stats.add_column("Metric", style="bright_green")
    stats.add_column("Value", justify="right", style="bright_white")
    stats.add_row("Total Proxies", str(total))
    stats.add_row("Alive", f"[bright_green]{alive}[/]")
    stats.add_row("Dead", f"[red]{dead}[/]")
    stats.add_row("Rotation Mode", mode)
    stats.add_row("Validation Interval", f"{proxy_cfg.get('validation_interval_sec', 300)}s")
    stats.add_row("Timeout", f"{proxy_cfg.get('timeout_sec', 15)}s")

    console.print()
    console.print(Panel(stats, border_style="bright_green",
                        title="[bold bright_green] PROXY STATS [/]"))
    console.print()
    print_info("Edit proxies in proxies.txt or config.json → proxies section.")


def action_portfolio_summary(cfg: dict):
    """Display aggregated portfolio analytics (simulation)."""
    console.print()

    total_value = round(random.uniform(50000, 2000000), 2)
    chains_used = random.randint(4, 8)
    total_addresses = random.randint(10, 50)
    total_seeds = random.randint(5, 20)

    stats_table = Table(
        show_header=True,
        header_style="bold bright_green",
        border_style="bright_blue",
        box=box.DOUBLE,
        title="[bold bright_green] PORTFOLIO OVERVIEW [/]",
    )
    stats_table.add_column("Metric", style="bright_blue")
    stats_table.add_column("Value", justify="right", style="bright_white")

    stats_table.add_row("Total Portfolio Value", f"[bold]${total_value:,.2f}[/]")
    stats_table.add_row("Active Chains", str(chains_used))
    stats_table.add_row("Addresses Checked", str(total_addresses))
    stats_table.add_row("Seed Phrases Checked", str(total_seeds))
    stats_table.add_row("High-Value Wallets", f"[bold red]{random.randint(1, 5)}[/]")
    stats_table.add_row("Proxies Used", f"{random.randint(30, 50)}")
    stats_table.add_row("Last Scan", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    chain_table = Table(
        show_header=True,
        header_style="bold bright_cyan",
        border_style="cyan",
        box=box.SIMPLE_HEAD,
        title="[bold bright_cyan] CHAIN BREAKDOWN [/]",
    )
    chain_table.add_column("Chain", style="bright_cyan")
    chain_table.add_column("Addresses", justify="center")
    chain_table.add_column("Value", justify="right", style="bright_white")
    chain_table.add_column("Share", justify="right", style="dim")

    for chain in random.sample(_CHAINS, chains_used):
        share = round(random.uniform(0.05, 0.40), 3)
        value = total_value * share
        addrs = random.randint(1, 10)
        chain_table.add_row(chain, str(addrs), f"${value:,.2f}", f"{share*100:.1f}%")

    console.print(stats_table)
    console.print()
    console.print(chain_table)
    console.print()
    print_info("Portfolio data is aggregated from all scan sessions.")


def action_export_results(cfg: dict):
    """Export results to file (simulation)."""
    export_cfg = cfg.get("export", {})
    fmt = export_cfg.get("default_format", "txt")
    out_dir = export_cfg.get("output_directory", "./results")

    console.print()
    print_info(f"Export format: [bright_cyan]{fmt.upper()}[/] | Output: [dim]{out_dir}[/]")
    separator()

    with Progress(
        SpinnerColumn(style="bright_green"),
        TextColumn("[bright_green]{task.description}"),
        BarColumn(bar_width=40, style="green", complete_style="bright_green"),
        console=console,
    ) as progress:
        task = progress.add_task("Preparing export...", total=4)
        for step in [
            "Collecting scan data...",
            "Formatting records...",
            "Writing file...",
            "Verifying output...",
        ]:
            progress.update(task, description=step)
            time.sleep(0.3)
            progress.advance(task)

    filename = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}"
    records = random.randint(20, 300)

    table = Table(
        show_header=True,
        header_style="bold bright_green",
        border_style="green",
        box=box.SIMPLE_HEAD,
        title="[bold bright_green] EXPORT COMPLETE [/]",
    )
    table.add_column("Property", style="bright_blue")
    table.add_column("Value", justify="right", style="bright_white")
    table.add_row("Filename", filename)
    table.add_row("Format", fmt.upper())
    table.add_row("Records", str(records))
    table.add_row("Size", f"{random.randint(5, 500)} KB")
    table.add_row("Path", f"{out_dir}/{filename}")

    console.print()
    console.print(table)
    console.print()
    print_success("Export complete.")


def action_chain_config(cfg: dict):
    """Display chain configuration."""
    rpc = cfg.get("rpc_endpoints", {})

    table = Table(
        show_header=True,
        header_style="bold bright_cyan",
        border_style="bright_blue",
        box=box.ROUNDED,
        title="[bold bright_cyan] CHAIN CONFIGURATION [/]",
    )
    table.add_column("Chain", style="bright_cyan")
    table.add_column("RPC Endpoint", style="dim")
    table.add_column("Proxy", justify="center", style="bright_green")
    table.add_column("Status", justify="center")

    default_rpcs = {
        "ethereum": "https://eth-mainnet.g.alchemy.com/v2/...",
        "bitcoin": "https://blockstream.info/api",
        "solana": "https://api.mainnet-beta.solana.com",
        "bsc": "https://bsc-dataseed.binance.org",
        "polygon": "https://polygon-rpc.com",
        "arbitrum": "https://arb1.arbitrum.io/rpc",
    }

    for chain, default_rpc in default_rpcs.items():
        configured_rpc = rpc.get(chain, "")
        rpc_display = configured_rpc[:30] + "..." if configured_rpc else default_rpc
        status = "[bright_green]Configured[/]" if configured_rpc else "[yellow]Default[/]"
        table.add_row(chain.title(), rpc_display, "[bright_green]✓[/]", status)

    console.print()
    console.print(table)
    console.print()
    print_info("All RPC queries are routed through the proxy pool.")
    print_info("Edit RPC endpoints in config.json → rpc_endpoints.")
