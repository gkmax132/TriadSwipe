```markdown
# TriadSwipe - Three-Finger Swipe Emulator for Touchpad

This Python script is designed to process touchpad events in Linux using the `evdev` library. It tracks finger movements on the touchpad and emulates three-finger swipes (left, right, up, down) through a virtual input device.

## Dependencies
- Python 3
- `evdev` library (`pip install evdev`)
- Input device access permissions (typically requires running with root privileges via `sudo`)

## Main Components

### Constants
- `TOUCHPAD_DEVICE`: Path to the touchpad device (e.g., `/dev/input/event11`).
- `SWIPE_THRESHOLD_X` (80): Horizontal threshold for swipe detection.
- `SWIPE_THRESHOLD_Y` (40): Vertical threshold for swipe detection.
- `DEAD_ZONE` (15): Dead zone to filter out accidental movements.
- `COOLDOWN` (0.3): Cooldown period between swipes (in seconds).
- `GRACE_PERIOD` (0.4): Grace period after lifting fingers during which a swipe can still be recognized.
- `NOISE_THRESHOLD` (5): Noise threshold to filter minor movements.

### Functions
1. **`find_device(event_path)`**  
   Checks the availability of the input device at the specified path and returns the device object or `None` if unavailable.

2. **`create_virtual_touchpad()`**  
   Creates a virtual input device (`UInput`) with multitouch event support, emulating a touchpad. Specifies parameters like coordinate ranges and supported events (taps, movements).

3. **`emulate_swipe(virtual_device, direction_x, direction_y)`**  
   Emulates a three-finger swipe in the specified direction:
   - Initializes three "fingers" with starting coordinates.
   - Performs a smooth movement in the given direction (10 steps).
   - Ends the event by lifting the fingers.

4. **`main()`**  
   Main program loop:
   - Connects to the touchpad.
   - Creates a virtual device.
   - Monitors touchpad events (X/Y coordinates, finger count).
   - Detects swipes based on accumulated data and triggers emulation when thresholds are met.

## How It Works
- The script only processes three-finger swipes (`BTN_TOOL_TRIPLETAP`).
- Accumulated movements (`swipe_accumulated_x`, `swipe_accumulated_y`) are compared to thresholds.
- If movement exceeds the threshold and stays within the dead zone on the other axis, a swipe is executed.
- After a swipe, data is reset, and a cooldown (`COOLDOWN`) is applied.

## Configuration for My Device
This script was developed and tuned specifically for the touchpad on my laptop:  
- **Device:** ETPS/2 Elantech Touchpad  
- **Kernel Path:** /dev/input/event8  
- **Size:** 47x20 mm  
- **Scroll Methods:** two-finger, edge  
- **Features:** tap-to-click disabled, disable-while-typing enabled, acceleration profile — adaptive.  

The thresholds (`SWIPE_THRESHOLD_X`, `SWIPE_THRESHOLD_Y`), dead zone (`DEAD_ZONE`), and noise filter (`NOISE_THRESHOLD`) were experimentally adjusted to ensure accurate swipe detection on this device. If you’re using a different touchpad, you may need to tweak these values.

## Usage
1. Ensure the device path (`TOUCHPAD_DEVICE`) is correct (can be checked with `evtest`).
2. Run the script with root privileges:
   ```bash
   sudo python3 triadswipe.py
Limitations

    Requires root privileges to access /dev/input.
    Works only on systems with evdev support (Linux).
    Thresholds may need fine-tuning for specific touchpads.
