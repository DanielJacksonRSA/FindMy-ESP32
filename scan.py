import asyncio
from bleak import BleakScanner

async def main():
    print("Scanning for ESP32 Apple Find My packets... (15 seconds)")
    results = []
    def callback(device, advertising_data):
        # Apple Company ID is 76 (0x004C)
        if 76 in advertising_data.manufacturer_data:
            m_data = advertising_data.manufacturer_data[76]
            rssi = advertising_data.rssi
            line = f"[Apple Packet] RSSI: {rssi} dBm | Hex: {m_data.hex()}"
            results.append(line)
            print(line)

    async with BleakScanner(detection_callback=callback):
        await asyncio.sleep(15)
    
    print(f"\n--- Scan complete. Found {len(results)} Apple BLE packets. ---")

asyncio.run(main())
