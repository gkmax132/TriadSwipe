#!/usr/bin/env python3
import evdev
import select
import time
from evdev import UInput, ecodes as e

# Устройства ввода
TOUCHPAD_DEVICE = "/dev/input/event8"  # Ваш тачпад

# Пороги для свайпов
SWIPE_THRESHOLD_X = 80
SWIPE_THRESHOLD_Y = 40
DEAD_ZONE = 15
COOLDOWN = 0.3
GRACE_PERIOD = 0.4
NOISE_THRESHOLD = 5

def find_device(event_path):
    try:
        device = evdev.InputDevice(event_path)
        return device
    except Exception as e:
        return None

def create_virtual_touchpad():
    capabilities = {
        e.EV_KEY: [
            e.BTN_LEFT,
            e.BTN_RIGHT,
            e.BTN_TOUCH,
            e.BTN_TOOL_FINGER,
            e.BTN_TOOL_DOUBLETAP,
            e.BTN_TOOL_TRIPLETAP,
            e.BTN_TOOL_QUADTAP,
        ],
        e.EV_ABS: [
            (e.ABS_X, evdev.AbsInfo(value=0, min=0, max=32767, fuzz=0, flat=0, resolution=31)),
            (e.ABS_Y, evdev.AbsInfo(value=0, min=0, max=32767, fuzz=0, flat=0, resolution=31)),
            (e.ABS_MT_POSITION_X, evdev.AbsInfo(value=0, min=0, max=32767, fuzz=0, flat=0, resolution=31)),
            (e.ABS_MT_POSITION_Y, evdev.AbsInfo(value=0, min=0, max=32767, fuzz=0, flat=0, resolution=31)),
            (e.ABS_MT_SLOT, evdev.AbsInfo(value=0, min=0, max=2, fuzz=0, flat=0, resolution=0)),
            (e.ABS_MT_TRACKING_ID, evdev.AbsInfo(value=0, min=-1, max=65535, fuzz=0, flat=0, resolution=0)),
            (e.ABS_MT_PRESSURE, evdev.AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
        ],
    }
    return UInput(
        capabilities,
        name="Virtual Touchpad",
        version=3,
        bustype=e.BUS_USB,
        vendor=0x1234,
        product=0x5678,
        phys="virtual-touchpad"
    )

def emulate_swipe(virtual_device, direction_x, direction_y):
    virtual_device.write(e.EV_KEY, e.BTN_TOUCH, 1)
    virtual_device.write(e.EV_KEY, e.BTN_TOOL_TRIPLETAP, 1)

    virtual_device.write(e.EV_ABS, e.ABS_MT_SLOT, 0)
    virtual_device.write(e.EV_ABS, e.ABS_MT_TRACKING_ID, 1000)
    virtual_device.write(e.EV_ABS, e.ABS_MT_POSITION_X, 5000)
    virtual_device.write(e.EV_ABS, e.ABS_MT_POSITION_Y, 5000)
    virtual_device.write(e.EV_ABS, e.ABS_MT_PRESSURE, 30)

    virtual_device.write(e.EV_ABS, e.ABS_MT_SLOT, 1)
    virtual_device.write(e.EV_ABS, e.ABS_MT_TRACKING_ID, 1001)
    virtual_device.write(e.EV_ABS, e.ABS_MT_POSITION_X, 5100)
    virtual_device.write(e.EV_ABS, e.ABS_MT_POSITION_Y, 5100)
    virtual_device.write(e.EV_ABS, e.ABS_MT_PRESSURE, 30)

    virtual_device.write(e.EV_ABS, e.ABS_MT_SLOT, 2)
    virtual_device.write(e.EV_ABS, e.ABS_MT_TRACKING_ID, 1002)
    virtual_device.write(e.EV_ABS, e.ABS_MT_POSITION_X, 5200)
    virtual_device.write(e.EV_ABS, e.ABS_MT_POSITION_Y, 5200)
    virtual_device.write(e.EV_ABS, e.ABS_MT_PRESSURE, 30)

    virtual_device.syn()

    for i in range(10):
        for slot in range(3):
            virtual_device.write(e.EV_ABS, e.ABS_MT_SLOT, slot)
            virtual_device.write(e.EV_ABS, e.ABS_MT_POSITION_X, 5000 + slot * 100 + direction_x * (i + 1) * 50)
            virtual_device.write(e.EV_ABS, e.ABS_MT_POSITION_Y, 5000 + slot * 100 + direction_y * (i + 1) * 50)
        virtual_device.syn()
        time.sleep(0.01)

    for slot in range(3):
        virtual_device.write(e.EV_ABS, e.ABS_MT_SLOT, slot)
        virtual_device.write(e.EV_ABS, e.ABS_MT_TRACKING_ID, -1)
    virtual_device.write(e.EV_KEY, e.BTN_TOOL_TRIPLETAP, 0)
    virtual_device.write(e.EV_KEY, e.BTN_TOUCH, 0)
    virtual_device.syn()

def main():
    touchpad = find_device(TOUCHPAD_DEVICE)
    
    if not touchpad:
        return

    virtual_device = create_virtual_touchpad()

    # Переменные для отслеживания свайпов
    last_x = [None, None]
    last_y = [None, None]
    swipe_accumulated_x = 0
    swipe_accumulated_y = 0
    current_slot = 0
    current_positions_x = [None, None]
    current_positions_y = [None, None]
    last_switch_time = 0
    three_fingers_detected = False
    last_three_fingers_time = 0

    devices = [touchpad]

    while True:
        readable, _, _ = select.select(devices, [], [])
        for device in readable:
            for event in device.read():
                current_time = time.time()

                if device == touchpad:
                    if event.type == evdev.ecodes.EV_ABS and event.code == evdev.ecodes.ABS_MT_SLOT:
                        current_slot = event.value

                    if event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_TOOL_TRIPLETAP:
                        if event.value == 1:
                            three_fingers_detected = True
                            last_three_fingers_time = current_time
                        else:
                            three_fingers_detected = False

                    if event.type == evdev.ecodes.EV_ABS and event.code == evdev.ecodes.ABS_MT_POSITION_X:
                        if current_slot in (0, 1):
                            current_positions_x[current_slot] = event.value
                            if last_x[current_slot] is not None and current_positions_x[current_slot] is not None:
                                delta_x = current_positions_x[current_slot] - last_x[current_slot]
                                if abs(delta_x) > NOISE_THRESHOLD:
                                    swipe_accumulated_x += delta_x
                            last_x[current_slot] = current_positions_x[current_slot]

                    if event.type == evdev.ecodes.EV_ABS and event.code == evdev.ecodes.ABS_MT_POSITION_Y:
                        if current_slot in (0, 1):
                            current_positions_y[current_slot] = event.value
                            if last_y[current_slot] is not None and current_positions_y[current_slot] is not None:
                                delta_y = last_y[current_slot] - current_positions_y[current_slot]
                                if abs(delta_y) > NOISE_THRESHOLD:
                                    swipe_accumulated_y += delta_y
                            last_y[current_slot] = current_positions_y[current_slot]

                    # Обработка свайпов строго с тремя пальцами
                    if three_fingers_detected or (current_time - last_three_fingers_time < GRACE_PERIOD):
                        if current_time - last_switch_time >= COOLDOWN:
                            abs_x = abs(swipe_accumulated_x)
                            abs_y = abs(swipe_accumulated_y)

                            if abs_x >= abs_y and abs_x > SWIPE_THRESHOLD_X and abs_y < DEAD_ZONE:
                                direction = 1 if swipe_accumulated_x > 0 else -1
                                emulate_swipe(virtual_device, direction, 0)
                                swipe_accumulated_x = 0
                                swipe_accumulated_y = 0
                                last_switch_time = current_time
                            elif abs_y > abs_x and abs_y > SWIPE_THRESHOLD_Y and abs_x < DEAD_ZONE:
                                direction = 1 if swipe_accumulated_y > 0 else -1
                                emulate_swipe(virtual_device, 0, direction)
                                swipe_accumulated_x = 0
                                swipe_accumulated_y = 0
                                last_switch_time = current_time

                    if event.type == evdev.ecodes.EV_KEY:
                        if event.code == evdev.ecodes.BTN_TOUCH and event.value == 0:
                            last_x = [None, None]
                            last_y = [None, None]
                            swipe_accumulated_x = 0
                            swipe_accumulated_y = 0
                            current_positions_x = [None, None]
                            current_positions_y = [None, None]
                            three_fingers_detected = False
                            last_three_fingers_time = 0

if __name__ == "__main__":
    main()
