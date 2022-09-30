# TalkingPlushiePi4

## Necessary components

- Raspberry Pi 4
- 1x MG996 servo
- 2x M4 x 20 mm
- 1x Adafruit I2S 3W Class D Amplifier Breakout
- 1x Stereo Enclosed Speaker Set - 3W 4 Ohm
- 1x Plushie with a ~180 mm wide mouth 


## Software requirements

### Audio setup

Follow [this](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/raspberry-pi-test?view=all) instructions in order to install the breakout circuit.

### Bluetooth setup

```
bluetoothctl
bluetoothctl pair CELLPHONE_MAC_ADDRESS
bluetoothctl trust CELLPHONE_MAC_ADDRESS
sudo nano /etc/systemd/system/dbus-org.bluez.service
```
Edit the service and add the compatibility flag -C at the end of the `ExecStart=` line. And a new line after that adds the SP profile.
```
ExecStart=/usr/lib/bluetooth/bluetoothd -C
ExecStartPost=/usr/bin/sdptool add SP
```

## Results:

![](https://github.com/RolandVtuber/TalkingPlushiePi4/blob/main/plushie.gif)
