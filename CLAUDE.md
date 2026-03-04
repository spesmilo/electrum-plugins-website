# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Electrum is a lightweight Bitcoin wallet written in Python (requires >= 3.10). It supports on-chain transactions, Lightning Network payments, hardware wallets, and multiple GUI frontends (Qt desktop, QML mobile).

## Common Commands

### Running from source
```bash
git submodule update --init
python3 -m pip install --user -e .
./run_electrum
```

### Running tests
```bash
pytest tests -v                          # all tests
pytest tests/test_bitcoin.py -v          # single test file
pytest tests/test_bitcoin.py::Test -v    # single test class
pytest tests -v -n auto                  # parallel (needs pytest-xdist)
```

Test extras: `pip install -e ".[tests]"` (installs pycryptodomex, cryptography, pyaes)

### Linting
```bash
flake8 electrum --select "E9,E101,E129,E273,E274,E703,E71,E722,F5,F6,F7,F8,W191,W29,B,B909" --ignore "B007,B009,B010,B036,B042,F541,F841"
```
CI uses flake8 7.3.0 with flake8-bugbear. No mypy/black/pylint.

### Building locale
```bash
./contrib/locale/build_locale.sh electrum/locale/
```

## Architecture

### Entry Points and Execution Modes
- `run_electrum` / `electrum/__main__.py` — three modes: **GUI**, **daemon**, **CLI**
- GUI mode launches Qt or QML frontend; daemon mode runs a long-lived JSON-RPC server; CLI mode sends single commands to daemon or runs offline

### Core Components

**Daemon** (`daemon.py`) — Central orchestrator. Manages the asyncio event loop, wallet lifecycle, Network instance, exchange rates (FxThread), and JSON-RPC command server. All async components share the daemon's event loop.

**Network** (`network.py`) — Manages connections to Electrum servers via `Interface` objects (aiorpcx-based async). Handles header sync, SPV verification, transaction fetching, fee estimation, and mempool monitoring. Maintains ~10 server connections with retry/backoff.

**Wallet hierarchy** (`wallet.py`):
```
Abstract_Wallet
├── Simple_Wallet
│   └── Imported_Wallet
└── Deterministic_Wallet
    ├── Standard_Wallet
    └── Multisig_Wallet
```
`Wallet` is a factory that dispatches to the correct type. Each wallet has a `WalletDB` (persistence), `WalletStorage` (encryption), `AddressSynchronizer` (address history), and optionally an `LNWallet` (Lightning).

**Lightning** (`lnchannel.py`, `lnworker.py`, `lnpeer.py`, `lnrouter.py`) — Full Lightning Network implementation with channel state machine, HTLC management, gossip sync, and onion routing. The Lightning Network protocol specification (BOLTs) is available locally in `bolts-lightning-specification/` — refer to it when working on Lightning-related tasks.

**Commands** (`commands.py`) — Declarative command system. Each command method is decorated with metadata (`requires_network`, `requires_wallet`, `requires_password`). Commands run async on the daemon side via RPC.

**Plugins** (`plugin.py`) — Hook-based plugin system. `@hook` decorator registers methods; `run_hook(name, *args)` calls all enabled plugins. Hardware wallets (Trezor, Ledger, Coldcard, etc.) are plugins in `electrum/plugins/`.

**Config** (`simple_config.py`) — Uses `ConfigVar` descriptors for typed, validated configuration properties with change callbacks.

### Concurrency Model
- Primary: **asyncio** event loop (daemon, network, wallets)
- Threading: RLocks protect wallet state and network interfaces
- Thread-async bridges: `asyncio.run_coroutine_threadsafe()` (sync→async), `aiorpcx.run_in_thread()` (async→sync)

### Event System
`EventListener` mixin + `trigger_callback('event_name', *args)` in `util.py`. Components register callbacks for events like `wallet_updated`, `blockchain_updated`, `network_status`.

### Network Constants
`constants.py` defines per-network config (mainnet, testnet, regtest, signet, etc.) including genesis hashes, BIP32 prefixes, checkpoint headers, and default servers.

### GUI Frontends
- **Qt** (`gui/qt/`) — PyQt6 desktop widgets, multi-window support, system tray
- **QML** (`gui/qml/`) — PyQt6 QML declarative UI, mobile-focused (Android)
- Both share the same Daemon backend

## Code Style
- 4-space indentation, UTF-8, LF line endings (see `.editorconfig`)
- Tests use `ElectrumTestCase` base class (in `tests/__init__.py`) which extends `unittest.IsolatedAsyncioTestCase`
- Use `@as_testnet` decorator for testnet-specific tests
- Key dependencies: aiorpcx (async RPC), aiohttp (HTTP), electrum_ecc (libsecp256k1 wrapper), dnspython, electrum_aionostr (Nostr Protocol library)
