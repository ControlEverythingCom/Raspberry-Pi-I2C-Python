# Using ControlEverything products with Raspberry Pi over I2C

In this article we will connect a ControlEverything relay controller to the Raspberry Pi. 
#### What we will accomplish
- We will explore the I2C protocol which is used to interact with ControlEverything Peripheral hardware connected to the Raspberry Pi.
- We will use i2c-tools which is a linux command line tool used for discovering and interacting with I2C devices connected to the Raspberry Pi
- Finally we will write a couple of simple Python applications which will control the relay on the ControlEverything board.

#### Purpose of Article
The purpose of this article is to get you familiar with communicating to ControlEverything hardware attached to the Raspberry Pi.

#### Hardware used in this article
- [Raspberry Pi 3 with Raspbian image] [pi]
- [ControlEverything Pi interface sheild] [piShield]
- [ControlEverything I2C Relay Controller] [relayController]
- [12VDC power supply for relay controller] [12vdcPower]
- USB micro power supply for powering Raspberry Pi.

#### Important Notes
The Raspberry Pi we are using is a Raspberry Pi 3.  We have the Raspbian image installed on the Pi used in this article.  If you have a different version of the Pi or a different Linux image installed your results may vary.  Just google setting up I2C on your particular Raspberry Pi setup.

I am using TightVNCServer to remotely access the Pi's desktop from my Mac.  If you find that interesting I highly recommend [this great article] [tightvncarticle].

#### Additional Information.
We have accompanying videos for this article on a Youtube Playlist [Here] [youtubeplaylist] 

#### Developer information
ControlEverything designs and develops peripheral products for the IOT platform market.  Our products are proven reliable and we are very excited to support Raspberry Pi.  For more information on ControlEverything please visit www.controleverything.com 

#### How to use this library

The libary can be imported into an existing application or you can simply use our example code.  This can be done through the Particle WEB IDE(Build).  Click the Community Libraries Icon and search for SI7020-A20_CE.  Once found select that library.  Click Include in App button to add it to an existing application or simply click the Use this example button to use our example code.  If you are adding this library to an existing application select the App you want to include the library in.  Finally click Add to this app.  For more information see [Particles's documentation] [sparkIncludeLibrary] 

## Chapter 1 Initial configuration of the Pi

For all intents and purposes this is a brand new fresh Raspberry Pi with Raspbian just installed.  
Before we can interface with I2C devices connected to the Pi Raspbian requires that we enable the I2C port on the ARM processor.  To do that open the terminal on the Pi and enter:
```
sudo raspi-config
```
A window will appear where you can access system level settings on the Pi.  Scroll down the list to Advanced Options and select it.  On the next window scroll down to I2C and select it.  When prompted to enable the I2C interface select yes.  On the next prompt select OK.  On the next prompt(Would you like the I2C kernel module to be loaded by default?) select Yes.  Then select OK.  Finally back at the main window hit the right arrow button on your keyboard to select Finish.  When prompted to reboot say Yes.  The Pi will now reboot.  Once it boots back up we will have access to the I2C port.

## Chapter 2 i2c-tools
i2c-tools is an extremely usefull diagnostics tool that I would not recommend any developer to be without when using ControlEverything products on a Linux based computing platform such as the Raspberry Pi.  So lets install it.  Open up the Terminal.

If you have not done so in a while, or ever, it would be a good idea to go ahead and update the Linux Package Installer by entering in the terminal:
```
sudo apt-get update
```
Once apt-get is up to date enter in the terminal:
```
sudo apt-get install i2c-tools
```
Say yes to any prompts that may appear.

We will use i2c-tools to scan for connected devices first so make sure your ControlEverything device is properly connected to the Raspberry Pi and is powered up.  In the terminal enter:
```
i2cdetect -r -y 1
```
The 1 in the command above specifies I2C bus 1.  To my knowledge Raspbian only supports 1 I2C bus and it is bus 1.  That is important information to have in the future of this article.
Now hopefully you will see a device detected on the port.  My relay controller has a default I2C address of 0x20 and I do not have any Address jumpers installed so it pops up in i2cdetect as 20 so I know it is properly connected and ready to use.

### I2C Device Addressing
Lets take a brief moment to talk about I2C device bus addressing.

An I2C bus should consist of a Master device and one or more connected slave devices.  In this case the Raspberry Pi is acting as the I2C bus Master device and the relay controller is acting as an I2C slave device connected to that bus.

I2C slave devices have an address byte which is how the master individually communicates with them.  The valid range for this I2C device bus address is 0-127 or 0x00-0x7F.  My particular device(relay controller) is using address 0x20 but I could change that using the on board address jumpers.  There can only be one slave on the bus using a particular address.  You do not want 2 slave devices on the bus using the same address.  This means if I wanted to add a second relay controller I would want to be sure to set it's address to something other than 0x20 by using the on board address jumpers.

Another thing to note is that while valid I2C bus addresses are 0-127 not all I2C devices support setting the address to any value from 0-127.  This relay controller for instance has only 3 address jumpers which allows me to set the address to 0x20 - 0x28  This means I can only have up to 8 of these devices on a single I2C bus.  If more of the same device need to be connected it is possible to use an I2C bus multiplexer which takes that single I2C bus and splits it into multiple individual busses, but that is an article for another day.

We could spend hours talking about this.

#### Reading and writing to I2C slave devices
I2C slave devices are relatively simple things.  They have a group of registers each of which hold a single byte.  We can read a byte from a register or write a byte to a register.  Everything that we accomplish using I2C connected devices is done in this way.  By writing to registers you can modify the configuration settings for the device or make it to something.  By reading from a register you can get sensor readings, device status, or check settings stored in the device.  For simplicities sake that's about it.  Once again we could talk about this for hours.

### Enough Jargen already lets do something!
First we need to know a little about the device we are interacting with and what is required to accomplish what we are trying to do.  In my case I have a single relay board.  To get information about how to control it I could pull up it's product page on ControlEverything and look at the code samples.  There I will see the I2C write and read commands used for interacting with the controller.  There I find that there is a single configuration command that needs to be written to the controller first thing.  This command sets all IO lines of the device to outputs(we need that if we want to turn the relay on and off) so lets use i2c-tools to set that configuration byte.  In the terminal enter:
```
i2cset -y 1 0x20 0x00 0x00
```
- i2cset is the command to write to an i2c slave device on the bus.  
- The -y is a command flag that answers an annoying are you sure prompt prior to sending the command
- 0x20 indicates the I2C device on the bus we are directing this write command to.  In this case it is my 1 channel relay controller
- 0x00 indicates the register on that device which I am writing a value to.  Register 0x00 is a configuration register in this devices which sets the direction of the 8 IO lines. 
- 0x00 indicates the byte I wish to write to the register.  This will set all IO lines on this device to outputs.

Now that the lines are set as outputs I can write commands to turn the relays on and off.  The output registers on this device are set through register 0x09.  A write to this register will set the status of all outputs on the device.  Lets turn on the relay.  In the terminal enter:
```
i2cset -y 1 0x00 0x09 0xFF
```
This command writes a value of 0xFF to register 0x09 which essentially turns on all output lines on the chip.  Inversely we can turn all outputs off with this command:
```
i2cset -y 1 0x00 0x09 0x00
```
So using i2c-tools we were able to detect the devices address on the port and then configure and control it all from the terminal with no code development required.  This is fantastic for experineting and getting familiar with your particular I2C device.

It's also possible to read from an I2C device but for simplicity's sake we will save that for a future article.

## Chapter 3 Python
So now we know our controller is properly connected to the Pi and works.  We also know what commands to send to do what we want.  Lets write a Python script for fun.

Now Python needs a way of interacting with devices on the Pi's I2C port.  Luckley there is a very simple to use Python Package that allows for that.  It's called SMBus.  Lets install that now.  In the terminal enter:
```
sudo apt-get install python-smbus
```
That's it.  We are ready to write our Python application.  Now I could sit here and write a book or I could just tell you to have a look at the Python examples in the Python Scripts folder on this Repo so that's what I'll do.  The scripts in there are very simple and self explanitory.  With the knowledge you have gained so far you will be able to completely determine what is going on in that code.

If you have any questions be sure you watch all the videos in the [YouTube Playlist] [youtubeplaylist] which serve to accompany this article.  I do everything in those videos I do here in the article so you can see in realtime how this all comes together.

### Have Fun!

License
----

GNU
[sparkIncludeLibrary]:http://docs.spark.io/build/#flash-apps-with-spark-build-using-libraries
[pi]:https://www.amazon.com/Raspberry-Pi-RASP-PI-3-Model-Motherboard/dp/B01CD5VC92/ref=sr_1_2?s=pc&ie=UTF8&qid=1481913044&sr=1-2&keywords=raspberry+pi
[piShield]:https://www.controleverything.com/content/I2C-Master?sku=INPI2
[relayController]:https://www.controleverything.com/content/Relay-Controller?sku=MCP23008_I2CIO7R1G5LE_10A
[youtubeplaylist]:https://www.youtube.com/playlist?list=PLGoyJ253LT0LbVgzKDyi9AB0jDmRW4BNZ
[12vdcPower]:https://www.controleverything.com/content/Power-Supplies?sku=12vAdapter
[tightvncarticle]:https://smittytone.wordpress.com/2016/03/02/mac_remote_desktop_pi/