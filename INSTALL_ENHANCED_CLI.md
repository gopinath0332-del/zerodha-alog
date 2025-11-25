# Enhanced CLI - Installation & Quick Test

## Installation

Install the new dependency (tabulate):

```bash
cd /Users/admin/Projects/my-trade-py
pip3.9 install tabulate
```

Or install all dependencies:

```bash
pip3.9 install -r Configuration/requirements.txt
```

## Quick Test

Test the import:

```bash
python3.9 -c "from Application.main_enhanced import EnhancedTradingCLI; print('✓ Enhanced CLI ready')"
```

## Run the Application

```bash
./run_cli_enhanced.sh
```

Or directly:

```bash
python3.9 Application/main_enhanced.py
```

## Features to Test

1. **Authentication** - Should auto-authenticate on startup
2. **Portfolio Summary** - Menu option 1
3. **Positions** - Menu option 2
4. **Strategy Monitors** - Menu option 7 (requires market hours for full test)
5. **Tools** - Menu option 8 (position calculator, exports)

## Notes

- The enhanced CLI is now ready for use
- All GUI features are available in the terminal
- Perfect for Raspberry Pi deployment
- See `Documentation/ENHANCED_CLI_GUIDE.md` for full documentation
