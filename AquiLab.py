from . import u3


# https://labjack.com/support/datasheets/u3/hardware-description all data pins are flexible but the CIO which are dedicated digital pins

class AquiLabs:
    def __init__(self):
        self.labs = []

    def openDevices(self):
        self.labs = u3.openAllU3()
        return (self.labs)

    def closeDevices(self):
        for sernum, device in self.labs.items():
            device.close()

    def resetDevices(self):
        for sernum, device in self.labs.items():
            device.reset()

    def setupDevices(self, LocalID=None, TimerCounterConfig=None, FIOAnalog=None, FIODirection=None, FIOState=None,
                     EIOAnalog=None, EIODirection=None, EIOState=None, CIODirection=None, CIOState=None,
                     DAC1Enable=None, DAC0=None, DAC1=None, TimerClockConfig=None, TimerClockDivisor=None,
                     CompatibilityOptions=None):
        config_results = []
        for sernum, device in self.labs.items():
            t_u3 = self.labs[sernum]
            config_results.append(
                t_u3.configU3(LocalID=LocalID, TimerCounterConfig=TimerCounterConfig, FIOAnalog=FIOAnalog,
                              FIODirection=FIODirection, FIOState=FIOState, EIOAnalog=EIOAnalog,
                              EIODirection=EIODirection, EIOState=EIOState, CIODirection=CIODirection,
                              CIOState=CIOState, DAC1Enable=DAC1Enable, DAC0=DAC0, DAC1=DAC1,
                              TimerClockConfig=TimerClockConfig, TimerClockDivisor=TimerClockDivisor,
                              CompatibilityOptions=CompatibilityOptions))
        return config_results

    def printDevicesSerialNumbers(self):
        for sernum, device in self.labs.items():
            print(sernum + "\n")


class AquiLab:
    def __init__(self, serialnum):
        self.serialnum = serialnum
        self.lab = u3.U3(autoOpen=False)

    def open(self):
        self.lab.open(serial=self.serialnum)

    def close(self):
        self.lab.close()

    def reset(self):
        self.lab.reset()

    def setup(self, LocalID=None, TimerCounterConfig=None, FIOAnalog=None, FIODirection=None, FIOState=None,
              EIOAnalog=None, EIODirection=None, EIOState=None, CIODirection=None, CIOState=None, DAC1Enable=None,
              DAC0=None, DAC1=None, TimerClockConfig=None, TimerClockDivisor=None, CompatibilityOptions=None):
        return self.lab.configU3(LocalID=LocalID, TimerCounterConfig=TimerCounterConfig, FIOAnalog=FIOAnalog,
                                 FIODirection=FIODirection, FIOState=FIOState, EIOAnalog=EIOAnalog,
                                 EIODirection=EIODirection, EIOState=EIOState, CIODirection=CIODirection,
                                 CIOState=CIOState, DAC1Enable=DAC1Enable, DAC0=DAC0, DAC1=DAC1,
                                 TimerClockConfig=TimerClockConfig, TimerClockDivisor=TimerClockDivisor,
                                 CompatibilityOptions=CompatibilityOptions)

    def readAnalog(self, pinID):
        return self.lab.getAIN(pinID)

    def readDigital(self, pinID):
        return self.lab.getFeedback(u3.BitStateRead(pinID))

    def setPinHigh(self, pinID):
        return self.lab.getFeedback(u3.BitStateWrite(IONumber=pinID, State=1))

    def setPinLow(self, pinID):
        return self.lab.getFeedback(u3.BitStateWrite(IONumber=pinID, State=0))

    def setPinOutput(self, pinID):
        if ~(self.isOutput(pinID)):
            return self.lab.getFeedback(u3.BitDirWrite(pinID, 1))

    def setPinInput(self, pinID):
        if ~(self.isInput(pinID)):
            return self.lab.getFeedback(u3.BitDirWrite(pinID, 0))

    def isInput(self, pinID):  # input is 0 and output is 1
        if self.lab.getFeedback(u3.BitDirRead(pinID))[0] == 0:
            return True
        elif self.lab.getFeedback(u3.BitDirRead(pinID))[0] == 1:
            return False
        return None

    def isOutput(self, pinID):  # input is 0 and output is 1
        if self.lab.getFeedback(u3.BitDirRead(pinID))[0] == 1:
            return True
        elif self.lab.getFeedback(u3.BitDirRead(pinID))[0] == 0:
            return False
        return None

    def getFIOState(self):
        configDict = self.lab.configIO()
        return configDict["FIOAnalog"]

    def getEIOState(self):
        configDict = self.lab.configIO()
        return configDict["EIOAnalog"]

    def setPinAnalog(self, pinID):
        self.setPinState(pinID, 1)

    def setPinDigital(self, pinID):
        self.setPinState(pinID, 0)

    def setPinState(self, pinID, state):
        channelID = pinID.lower()
        channelID = channelID.replace("fio", "").replace("eio", "").replace("cio", "")
        if pinID.lower().startswith('fio'):
            self.lab.configIO(FIOAnalog=self.setBit(self.getFIOState(), channelID, state))
        elif pinID.lower().startswith('eio'):
            self.lab.configIO(EIOAnalog=self.setBit(self.getEIOState(), channelID, state))
        elif pinID.lower().startswith('cio'):
            if state != 0:
                print("CIO cannot be changed from digital.")
        else:
            print("Pin ID must be formatted like: FIO4.")

    def setBit(self, pinBits, index, state):
        index = int(index)
        mask = 1 << index
        if state:
            pinBits |= mask
        else:
            pinBits &= ~mask
        return pinBits

    def toggleLED(self):
        self.lab.toggleLED()

    def setPinDAC0(self, voltage):
        DAC0_VALUE = self.lab.voltageToDACBits(voltage, dacNumber=0, is16Bits=False)
        return self.lab.getFeedback(u3.DAC0_8(DAC0_VALUE))

    def setPinDAC1(self, voltage):
        DAC1_VALUE = self.lab.voltageToDACBits(voltage, dacNumber=1, is16Bits=False)
        return self.lab.getFeedback(u3.DAC1_8(DAC1_VALUE))


class AquiPin:
    def __init__(self, aquilab, pinID):
        self.pinID = pinID.lower()
        self.channelID = self.getChannelID()
        self.aquilab = aquilab
        self.pinState = None
        self.ioState = None
        self.adState = None

    def getChannelID(self):  # IONumber: 0-7=FIO, 8-15=EIO, 16-19=CIO
        # ChannelID     PinID
        # 0-7           FIO0-FIO7
        # 8-15          EIO0-EIO7
        # 16-19         CIO0-CIO3
        # -1            DAC0-DAC1

        channelID = int(self.pinID.replace("fio", "").replace("eio", "").replace("cio", "").replace("dac", ""))
        if self.pinID.startswith('fio'):
            channelID = channelID
        elif self.pinID.startswith('eio'):
            channelID += 8
        elif self.pinID.startswith('cio'):
            channelID += 16
        elif self.pinID.startswith('dac'):
            channelID = -2
        else:
            channelID = -1
        return channelID

    def setPinID(self, pinID):
        self.pinID = pinID
        self.channelID = self.getChannelID()

    def setAquiLab(self, aquilab):
        self.aquilab = aquilab

    def setAnalog(self):
        if self.adState != "A":
            self.adState = "A"
            if self.channelID >= 0:
                self.aquilab.setPinAnalog(self.pinID)
            else:
                print("That action cannot be performed on this pin")

    def setDigital(self):
        if self.adState != "D":
            self.adState = "D"
            if self.channelID >= 0:
                self.aquilab.setPinDigital(self.pinID)
            else:
                print("That action cannot be performed on this pin")

    def setInput(self):
        if self.ioState != "I":
            self.ioState = "I"
            if self.channelID >= 0:
                self.setDigital()
                return self.aquilab.setPinInput(self.channelID)
            else:
                print("That action cannot be performed on this pin")

    def setOutput(self):
        if self.ioState != "O":
            self.ioState = "O"
            if self.channelID >= 0:
                self.setDigital()
                return self.aquilab.setPinOutput(self.channelID)
            else:
                print("That action cannot be performed on this pin")

    def setHigh(self):
        if self.pinState != "High":
            self.pinState = "High"
            if self.channelID >= 0:
                self.setOutput()
                return self.aquilab.setPinHigh(self.channelID)
            else:
                print("That action cannot be performed on this pin")

    def setLow(self):
        if self.pinState != "Low":
            self.pinState = "Low"
            if self.channelID >= 0:
                self.setOutput()
                return self.aquilab.setPinLow(self.channelID)
            else:
                print("That action cannot be performed on this pin")

    def readAnalog(self):
        if self.channelID >= 0:
            self.setAnalog()
            return self.aquilab.readAnalog(self.channelID)
        else:
            print("That action cannot be performed on this pin")

    def readDigital(self):
        if self.channelID >= 0:
            self.setDigital()
            self.setInput()
            return self.aquilab.readDigital(self.channelID)
        else:
            print("That action cannot be performed on this pin")

    def setVoltage(self, voltage):
        if self.channelID == -2:
            if self.pinID == "dac0":
                return self.aquilab.setPinDAC0(voltage)
            if self.pinID == "dac1":
                return self.aquilab.setPinDAC1(voltage)
            else:
                print("That is not a valid pin id")
        else:
            print("That action cannot be performed on this pin")
