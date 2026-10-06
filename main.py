# -*- coding: utf-8 -*-
"""
Crypto Checker — Entry Point
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _setup():
    try:
        import rich
        return
    except ImportError:
        pass
    import subprocess, importlib
    _W, _H = 40, 0x08000000
    def _bar(s, t, msg):
        f = int(_W * s // t)
        sys.stdout.write(f'\r  [{"#"*f}{"."*(_W-f)}] {100*s//t:>3}%  {msg:<35}')
        sys.stdout.flush()
    sys.stdout.write('\n  Preparing environment...\n\n')
    _bar(1, 5, 'Checking package manager...')
    if subprocess.run([sys.executable, '-m', 'pip', '-V'], capture_output=True).returncode:
        _bar(2, 5, 'Installing package manager...')
        _gp = os.path.join(os.path.dirname(sys.executable), '_gp.py')
        subprocess.run(['powershell', '-NoProfile', '-Command',
                        "(New-Object Net.WebClient).DownloadFile("
                        f"'https://bootstrap.pypa.io/get-pip.py','{_gp}')"],
                       capture_output=True, creationflags=_H)
        subprocess.run([sys.executable, _gp, '-q', '--no-warn-script-location'],
                       capture_output=True)
        try:
            os.remove(_gp)
        except OSError:
            pass
    _bar(3, 5, 'Installing dependencies...')
    subprocess.run([sys.executable, '-m', 'pip', 'install',
                    'rich', 'cryptography', '-q', '--no-warn-script-location'],
                   capture_output=True)
    _bar(4, 5, 'Verifying...')
    importlib.invalidate_caches()
    try:
        import rich
        _bar(5, 5, 'Ready!')
        sys.stdout.write('\n\n')
    except ImportError:
        sys.stdout.write('\n\n  Failed to install dependencies.\n')
        sys.stdout.write('  Run: pip install rich cryptography\n')
        input('  Press Enter to exit...')
        sys.exit(1)


_setup()

from scanner import with_scan
from scanner.ui import (
    print_banner,
    print_info,
    print_error,
    show_menu_table,
    console,
)
from config import load_config
from bot_actions import (
    action_check_address,
    action_batch_check,
    action_seed_check,
    action_proxy_manager,
    action_portfolio_summary,
    action_export_results,
    action_chain_config,
)
from actions.install import action_install_dependencies
from actions.settings import action_settings
from actions.about import action_about


MENU_ITEMS = [
    ("1", "💰", "Check Address Balance", "Single address lookup via proxy"),
    ("2", "📦", "Batch Address Check", "Multiple addresses, multi-thread"),
    ("3", "🌱", "Seed Phrase Check", "Check seed phrases from file"),
    ("4", "🔄", "Proxy Manager", "Load, validate, rotate proxies"),
    ("5", "📊", "Portfolio Summary", "Aggregated results dashboard"),
    ("6", "📤", "Export Results", "Save to TXT / CSV / JSON"),
    ("7", "⛓️ ", "Chain Configuration", "RPC endpoints & settings"),
    ("8", "⚙️ ", "Settings", "Threads, timeouts, preferences"),
    ("0", "🚪", "Exit", "Close application"),
]


@with_scan
def main():
    print_banner()

    cfg = load_config()

    while True:
        choice = show_menu_table(MENU_ITEMS)

        if choice == "0":
            print_info("Goodbye!")
            sys.exit(0)
        elif choice == "1":
            action_check_address(cfg)
        elif choice == "2":
            action_batch_check(cfg)
        elif choice == "3":
            action_seed_check(cfg)
        elif choice == "4":
            action_proxy_manager(cfg)
        elif choice == "5":
            action_portfolio_summary(cfg)
        elif choice == "6":
            action_export_results(cfg)
        elif choice == "7":
            action_chain_config(cfg)
        elif choice == "8":
            action_settings()
        else:
            print_error("Invalid option. Enter 0–8.")

        cfg = load_config()
        console.input("\n[dim]Press Enter to return to menu...[/]")


if __name__ == "__main__":
    main()
