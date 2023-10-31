# BLE HID Ring

VR is fun, but sometimes you need to fake being able to reach out and touch something (Looking at you DCS). [PointCtrl](https://pointctrl.com/) would seem to be ideal, but has a waitlist measured in years.

Using this [Ring With Mouse Buttons Wheel](https://www.instructables.com/Ring-With-Mouse-Buttons-Wheel/) instructable as inspiration this project will seek to implement the features in the table below.

| Feature | Status | Notes |
| - | - | - |
| BLE HID Service | ❌ | Service advertised |
| BLE Battery Service | ❌ | Service advertised |
| BLE Device Information Service | ❌ | Not implemented |
| Battery & Charge Monitoring | ✅ | Working |
| Status Indication | ✅ | This would be more predicatable if there was a signle "thread" for all three LEDs |
| Button Monitoring | ✅ | Working? |
| IMU Usable for Input | ✅ | Working |
| IMU Gesture as Button Presses | ❌ | Not implemented |

## Hardware

| Part | Source |
| - | - |
| [Leap Motion](https://ca.robotshop.com/products/leap-motion-controller) |
| [nRF52840](https://www.seeedstudio.com/Seeed-XIAO-BLE-Sense-nRF52840-p-5253.html) |
| [Push Button Switch](https://www.amazon.ca/dp/B06Y6DDG8K?psc=1&ref=ppx_yo2ov_dt_b_product_details) |
| [Slide Switch](https://www.amazon.ca/dp/B08SLQ1KBX?ref=ppx_yo2ov_dt_b_product_details&th=1) |
| [3D Printed Ring](https://www.thingiverse.com/thing:5886564) |
| [Battery 50mAh](https://www.aliexpress.com/item/32548166394.html?spm=a2g0o.order_list.order_list_main.4.685c1802jLIyDU) |

## Software

### Leap Motion

DCS ships with an old version of the Leap Motion libraries

### Ring

Load [circuitpython](https://circuitpython.org/board/Seeed_XIAO_nRF52840_Sense/) onto the devboard.

Setup & activate a python virtual environment to talk to the devboard used for the ring.

```bash
virtualenv /tmp/ble-hid-ring
source /tmp/ble-hid-ring/bin/act
pip install --upgrade pip
pip install -r requirements.txt
```

Load the software on to the devboard.

```bash
./push.sh <path to devboard>
```
