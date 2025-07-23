"""
Date: 16.07.2025
Author: ChatGPT
Purpose:
    - Scans for all available interfaces
    - Prints the URIs that can be used to connect
"""

import cflib.crtp

def main():
    cflib.crtp.init_drivers()

    print("🔍 Scanning interfaces for Crazyflies...")
    available = cflib.crtp.scan_interfaces()

    if not available:
        print("❌ No Crazyflies found.")
    else:
        print("✅ Available Crazyflies:")
        for uri, desc in available:
            print(f"    {uri} - {desc}")

if __name__ == '__main__':
    main()