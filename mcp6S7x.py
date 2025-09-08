"""
MCP97S1/2/3 programmable amp library
See README.md
See repository https://github.com/xxxxx
"""

DEBUG = const(False)
if DEBUG:
    def debug(msg):
        print(msg)
else:
    def debug(msg):
        pass

from adafruit_bus_device import spi_device
from micropython import const

__version__ = "0.1"
# __repo__ = "https://github.com/...."

try:
    # blinka has all this?
    from busio import SPI
    from digitalio import DigitalInOut
except ImportError:
    pass

INSTRUCTION_NOP =      0b00000000
INSTRUCTION_GAIN =     0b01000000
INSTRUCTION_CHANNEL =  0b01000001 # select input channel
INSTRUCTION_SHUTDOWN = 0b00100000 # output goes high
GAINS = [ 1,2,4,5,8,10,16,32 ]
GAINS_BYTE = [ 0b00, 0b001, 0b010, 0b011,0b100,0b101,0b110,0b111 ]

class MCP6S7x:
    
    def __init__(self, spi: SPI, cs: DigitalInOut, devices=1):
        self._device_count = devices
        self._cs = cs
                
        self._spi = spi_device.SPIDevice(spi, cs, baudrate=2000000)
        self._init_device()

    def _init_device(self):
        # has random settings, per spec sheet 5.2.1, till CS toggle
        with self._spi:
           self._cs.value = True
           self._cs.value = False
           self._cs.value = True
        # default to gain 1
        self.gain( *[1 for i in range(self._device_count) ] )
        self.channel(0)
        debug("  init'd")

    def gain(self, *gains):
        if len(gains) == 0:
            raise Exception("Expected at least one gain value, saw none")
        if len(gains) > self._device_count:
            raise Exception(f"Too many gain values, we have {self._device_count} devices, but you gave {len(gains)} values")

        debug(f"  Set gains {gains}")

        command = []
        for g in gains:
            command.extend( self._gain(g) )
        command = bytes( command )
        hex = ' '.join( [f'0x{c:02x}' for c in command] )
        debug(f"  Full Gain command = {hex}")

        with self._spi as devices:
            devices.write( command )

    def _gain(self, gain):
        """One 16byte command"""
        debug(f"  ## _gain <- {gain}")
        if gain < 0:
            gain = 1

        # floor, not rounding
        gain_i = [i for i,x in enumerate(GAINS) if gain >= x][-1]
        debug(f"  ## gain_i for {gain} = {gain_i}")
        gain_byte = GAINS_BYTE[ gain_i ]

        command = [ INSTRUCTION_GAIN, gain_byte ]
        hex = ' '.join( [f'0x{c:02x}' for c in command] )
        debug(f"  Gain command = {hex}")
        return command

    def channel(self, *channels):
        """Select 0 or 1 input channel for each device, channels is a list of 0|1 for each device.
        Select channel 1 for a single channel device (e.g. MCP69S1) has no effect"""
        if len(channels) == 0:
            raise Exception("Expected at least one channel value, saw none")
        if len(channels) > self._device_count:
            raise Exception(f"Too many channel values, we have {self._device_count} devices, but you gave {len(channels)} values")
        command = []
        for c in channels:
            command.extend( self._channel(c) )
        command = bytes( command )
        hex = ' '.join( [f'0x{c:02x}' for c in command] )
        debug(f"  Full channel command = {hex}")

        with self._spi as devices:
            devices.write( command )
        

    def _channel(self, channel):
        """Select which inputs (channel) to use: 0|1"""
        command = [ INSTRUCTION_CHANNEL, channel ]
        hex = ' '.join( [f'0x{c:02x}' for c in command] )
        debug(f"  Channel command = {hex}")
        return command

    def shutdown(self, *devices):
        if len(devices) > self._device_count:
            raise Exception(f"Too many devices, we have {self._device_count} devices, but you gave {len(devices)} values")
        if len(devices) == 0:
            devices = [True for x in self._channels]

        debug(f"  Shutdown {devices}")
        command = []
        for x in devices:
            command.extend( self._shutdown(x) )
        command = bytes(command)
        hex = ' '.join( [f'0x{c:02x}' for c in command] )
        debug(f"  Full shutdown command = {hex}")
    
    def _shutdown(self, shutdown ):
        """Command, T|F for shutdown. False makes a noop"""
        return [ INSTRUCTION_SHUTDOWN if shutdown else INSTRUCTION_NOP, 0 ]

