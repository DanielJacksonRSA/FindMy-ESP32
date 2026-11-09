<div align="center">

# ESP32 Find My Tag

**Build your own AirTag.** A tiny, cheap ESP32 chip broadcasts a signal that Apple's Find My network picks up. Any iPhone that walks past quietly reports your tag's location, so you can see it on a map — without buying an AirTag.

![Hardware](https://img.shields.io/badge/Hardware-ESP32--C3-red?logo=espressif&logoColor=white)
![Firmware](https://img.shields.io/badge/Firmware-Arduino-00979d?logo=arduino&logoColor=white)
![Key_gen](https://img.shields.io/badge/Key_generation-Python_3-3776ab?logo=python&logoColor=white)
![Network](https://img.shields.io/badge/Works_with-Apple_Find_My-000?logo=apple&logoColor=white)
![Licence](https://img.shields.io/badge/licence-All_rights_reserved-red)

</div>

> **Use responsibly.** This project lets you locate your own device. Do not use it to track people or anything you don't own. Tracking someone without their consent is illegal. Shared for educational purposes.

## What it is

Apple's Find My network is the system that finds lost AirPods and AirTags. It works because millions of iPhones around the world are always listening for these little Bluetooth signals and reporting what they hear. This project makes a small, inexpensive ESP32 board speak that same language, so it can be found the same way an AirTag can.

The project was really about the reverse-engineering puzzle: generating the right kind of cryptographic keys, packaging the broadcast signal in exactly the format Apple expects, disguising the chip's network address the way the protocol requires, and stretching the battery by making the chip sleep almost all the time.

## How it works, in plain English

1. **Make keys.** A Python script creates a batch of secret keys. You keep the secret half; the public half is what the tag shouts into the air.
2. **Broadcast.** The tag sends out a small Bluetooth message containing part of a public key, in the exact format Apple's network recognises.
3. **Change identity.** A tag that always shouts the same thing would be easy to follow. So it cycles through its keys and changes its identity every 15 minutes, just like a real AirTag does.
4. **Sip power.** The chip wakes up, broadcasts for half a second, then goes into a deep sleep for a few seconds. Because it's asleep almost all the time, a small battery lasts for weeks.

## Setup

### 1. Generate your keys

```sh
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 generate_keys.py --nkeys 20 --emit-firmware -o firmware
```

This writes a file `firmware/public_keys.h` that the firmware needs (the `.gitignore` keeps it out of git, since it's yours). It also produces a secret key file — **keep that one private** — and a devices file you can load into a Find My viewer like OpenHaystack to see your tag on a map.

### 2. Flash the chip

Open `firmware/esp32_findmy_tag.ino` in the Arduino IDE (with ESP32 board support installed), make sure `firmware/public_keys.h` exists from step 1, pick your board and port, and upload.

### 3. See it working

```sh
python scan.py
```

This listens for Apple Bluetooth packets nearby and prints what it hears — including your tag. The tag also shows up in a normal Find My or OpenHaystack lookup using your keys.

---

<details>
<summary><b>Technical detail</b> — the protocol and design, for a developer reader</summary>

### The pieces

1. **Keys.** `generate_keys.py` makes SECP224R1 key pairs. The private key stays with the owner. The first 28 bytes of the public key go into the advertisement.
2. **Advertisement.** The firmware builds Apple's offline-finding payload: company ID `0x004C`, type `0x12`, then 22 bytes of the public key. The broadcast MAC address is derived from the first 6 bytes of the same public key, as the protocol requires.
3. **Rotation.** The firmware holds 20 keys and advances to the next every 15 minutes, so the broadcast identity changes over time.
4. **Battery.** The board wakes, advertises for ~0.5 s, then deep-sleeps for ~4.5 s. That duty cycle is what stretches a small battery to weeks.

### Repository layout

```
generate_keys.py        Key generation. Writes output/ plus a firmware header.
scan.py                 BLE sniffer that prints Apple manufacturer packets.
firmware/
  esp32_findmy_tag.ino  The tag firmware. Keys come from public_keys.h.
requirements.txt        Python dependencies.
```

### Design notes

- Key material comes from the cryptographically secure `secrets` module, never from a PRNG seeded from the clock.
- The key count is capped at 50.
- The script is Python 3 only.
- The devices file is written with `json.dumps`, so it is valid by construction.
- `--emit-firmware` generates the C header of public keys instead of hand-copying them into the sketch.
- Real keys live in the git-ignored `public_keys.h`, not in the firmware source.

</details>

<details>
<summary><b>Attribution</b></summary>

The Find My key generation follows the approach from the OpenHaystack project and the community work it builds on (buerki's and seemoo's write-ups on Apple's offline-finding protocol). OpenHaystack: <https://github.com/seemoo-lab/openhaystack>

</details>

---

<div align="center">
<sub>Daniel Jackson · <a href="https://github.com/DanielJacksonRSA">GitHub</a> · <a href="LICENSE">All rights reserved</a>. Apple's Find My network belongs to Apple; this is an unofficial, non-commercial project.</sub>
</div>
