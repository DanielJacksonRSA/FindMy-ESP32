# ESP32 Find My Tag

A DIY location tag that works with Apple's **Find My** network. An ESP32 broadcasts Apple-compatible BLE advertisements from a rotating set of public keys. Nearby iPhones pick them up and report the tag's location to Apple's network, so the owner can track it in Find My without paying for an AirTag.

This was a personal hardware and reverse-engineering project: generating the right key pairs, encoding the payload correctly, spoofing the MAC address, and tuning a deep-sleep cycle for battery life.

> **Use responsibly.** This project lets a device be located by its owner. Do not use it to track people or anything you do not own. Tracking someone without their consent is illegal. This repository is shared for educational purposes.

| | |
|---|---|
| Hardware | ESP32 (tested on ESP32-C3) |
| Firmware | Arduino core with the ESP32 BLE library |
| Key generation | Python 3 with `cryptography` |
| Network | Apple Find My, via offline-finding BLE advertisements |

## How it works

1. **Keys.** `generate_keys.py` makes SECP224R1 key pairs. The private key stays with the owner. The first 28 bytes of the public key go into the advertisement.
2. **Advertisement.** The firmware builds Apple's offline-finding payload: company ID `0x004C`, type `0x12`, then 22 bytes of the public key. The broadcast MAC address is derived from the first 6 bytes of the same public key, as Apple's protocol requires.
3. **Rotation.** A tag that always broadcasts the same key is easy to follow. The firmware holds 20 keys and moves to the next one every 15 minutes, so the broadcast identity changes over time.
4. **Battery.** The board wakes up, advertises for half a second, then deep-sleeps for 4.5 seconds. The duty cycle is what stretches a small battery to weeks.

## Repository layout

```
generate_keys.py        Key generation. Writes output/ plus a firmware header.
scan.py                 BLE sniffer that prints Apple manufacturer packets.
firmware/
  esp32_findmy_tag.ino  The tag firmware. Keys come from public_keys.h.
requirements.txt        Python dependencies.
```

## Setup

### 1. Generate keys

```sh
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 generate_keys.py --nkeys 20 --emit-firmware -o firmware
```

This writes `firmware/public_keys.h`, which the `.gitignore` keeps out of git. It also writes the other files to `firmware/`:

- `<prefix>.keys`: the full key list. **Keep this secret.**
- `<prefix>_devices.json`: an entry you can import into OpenHaystack or a similar Find My viewer so your devices appear on the map.
- `<prefix>_keyfile`: the public keys in binary.

To keep the secrets separate from the firmware, generate into the default `output/` folder and copy only the header across:

```sh
python3 generate_keys.py --nkeys 20 --emit-firmware   # writes output/
cp output/*_public.h firmware/public_keys.h
```

### 2. Flash the firmware

1. Install the ESP32 board support in the Arduino IDE.
2. Open `firmware/esp32_findmy_tag.ino`.
3. Make sure `firmware/public_keys.h` exists (from step 1).
4. Select your board and port and upload.

### 3. Watch it work

```sh
python scan.py
```

Prints any Apple BLE packets it hears, including your tag's. The tag is also visible in a normal Find My or OpenHaystack lookup using the generated keys.

## Improvements made for this portfolio

The original scripts were quick prototypes. For this repository I:

- Replaced `random.getrandbits` with the cryptographically secure `secrets` module. Key material should never come from a PRNG seeded from the clock.
- Removed a hidden `--thisisnotforstalking` flag that lifted the key limit, and kept the limit honest at 50.
- Removed Python 2 leftovers (`.decode('hex')`, `ord()` branches) and made the script Python 3 only.
- Replaced the hand-built JSON string template with `json.dumps`, so the devices file is valid by construction.
- Added `--emit-firmware` so the C header of public keys is generated instead of hand-copied into the sketch.
- Moved the 20 real keys out of the firmware source into the git-ignored `public_keys.h`. The original sketch had them hardcoded.

## Attribution

The Find My key generation follows the approach from the OpenHaystack project and the community work it builds on (buerki's and seemoo's write-ups on Apple's offline-finding protocol). OpenHaystack: <https://github.com/seemoo-lab/openhaystack>

## Author

Daniel Jackson. [GitHub](https://github.com/DanielJacksonRSA)

Code is [All rights reserved](LICENSE). Apple's Find My and the Find My network belong to Apple. This is an unofficial, non-commercial project.
