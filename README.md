# Circuitpython library for MCP6S71/2/3 Programmable Gain Amplifier

[Datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/21908a.pdf) as of 2025-09-06.

* MCP6S71 is single channel
* MCP6S72 is two channel
* MCP6S73 is two channel

The 2 channel devices actually only amplify 1 channel at a time, you have to choose which channel to amplify.

## Requires

    * circuitpython 9+
    * `adafruit-circuitpython-busdevice`
## Note preferred wiring

    Put a passive pull-up on CS. Otherwise, device may misbehave before SPI is initialized.

## Typical usage

        import time

        import board 
        import busio # adafruit busio

        import mcp6S7x

        # shared spi, MCP6S7x rated for 10MHz max, The MCP6S91/2/3 devices operate in SPI modes 0,0
and 1,1.
        spi = busio.SPI()

        # devices init to gain=+1
        amp1_cs = digitalio.DigitalInOut(board.SD_CS) # or whatever pin you are using for "select"
        amp1 = mcp6S7x.MCP6S7x(spi, amp1_cs) # one device with 1 channel (MCP6S91)
        amp2_cs = digitalio.DigitalInOut(board.D3) # or whatever pin you are using for "select"
        amp2 = mcp6S7x.MCP6S7x(spi, amp2_cs, 2) # one device with 2 channels (MCP6S92/3)
        # "daisy chain" see section 5.3 of data-sheet for wiring
        ampseveral_cs = digitalio.DigitalInOut(board.D4) # or whatever pin you are using for "select"
        several_amps = mcp6S7x.MCP6S7x(spi, ampseveral_cs, 2,1,2,2) # MCP6S92,MCP6S91,MCP6S92,MCP6S92

        while true:
            # Various "on" for 1 second
            # gains should be from list: mcp6S7x.MCP6S7x.Gains which are [ 1,2,4,5,8,10,16,32 ]
            # intermediate values will be rounded
            amp1.gain(4)
            amp2.gain(16)
            ampseveral.gain(1,16,32,4) # for all daisy-chained devices
            ampseveral.channel(1,0,1,0) # which input on each device
            time.sleep(1)

            # Turn amps off for 1 second
            amp1.shutdown()
            amp2.shutdown()
            ampseveral.shutdown() # all of them
            # ampseveral.shutdown(True,False,True,True); # or pick which ones: by device, not channel
            time.sleep(1)

