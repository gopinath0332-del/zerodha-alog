#!/usr/bin/env python3
"""
Debug script to print all position fields
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from Core_Modules.trader import KiteTrader
import json

def main():
    trader = KiteTrader()
    positions = trader.get_positions()
    
    print("\n=== NET POSITIONS ===")
    for pos in positions.get('net', []):
        if pos['quantity'] != 0:
            print(f"\n{pos['tradingsymbol']}:")
            print(json.dumps(pos, indent=2, default=str))
    
    print("\n=== DAY POSITIONS ===")
    for pos in positions.get('day', []):
        if pos['quantity'] != 0:
            print(f"\n{pos['tradingsymbol']}:")
            print(json.dumps(pos, indent=2, default=str))

if __name__ == "__main__":
    main()
