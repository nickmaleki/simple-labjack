# AquiLab
A simple wrapper for LabJack devices which brings high level arduino-like functions to the device.

## Prerequisites
A python environment with LabJackPython.py, Modbus.py, and u3.py which can be found on [LabJack's GitHub](https://github.com/labjack/LabJackPython)

## Getting Started
Run [LabJack.exe](https://labjack.com/support/software/installers/ud) to install LabJack dependecies

## Example Code
```python
import time
from AquiLab import AquiLabs, AquiLab, AquiPin

myLabs = AquiLabs()  # create a new set of aquilabs
myLabs.openDevices()  # open all of the devices
myLabs.printDevicesSerialNumbers()  # print all of the serial numbers
# myLabs.setupDevices()  # use this to setup the defaults of devices in mass
# myLabs.resetDevices()  # use this to reset the defaults of devices in mass
myLabs.closeDevices()  # close all of the devices

myLab = AquiLab(320086141)  # create a single aquilab based on the serial numbers printed earlier
myLab.open()  # open that single aquilab

for i in range(5): # toggle aquilab indicator LED 5 times
   myLab.toggleLED()
   time.sleep(.5)

print(bin(int(myLab.getFIOState())))  # print current FIO pin states
print(bin(int(myLab.getEIOState())))  # print current EIO pin states

myPin = AquiPin(myLab, "FIO7")  # create a pin on FIO7

# The following four images will configure everything for you:
print(myPin.readDigital())  # digital read on myPin.
print(myPin.readAnalog())  # analog read on myPin.
myPin.setHigh()
myPin.setLow()

myPin2 = AquiPin(myLab, "DAC1")  # create a pin on DAC1

myPin2.setVoltage(1.5)  # set pin voltage to 1.5V
```
