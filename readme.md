<h1>Sonoff WLAN Multichannel Switcher</h1>

Control your illumination or power switches at home with your Kodi remote. All you need is a Sonoff WLAN (multichannel) switch device from Itead in your home automation equipment flashed with TASMOTA. Interesting? Visit <b>itead.cc</b> to see more.

It's required to flash or update your devices with TASMOTA firmware. You can control your devices with simple HTTP commands within a web browser after that. Additional you have the ability to setup your device(s) via webinterface and get much more control to your devices (MQTT, Emulation).

- show status:

        http://<ip-of-your-device>/cm?cmnd=power<channel number>
        
- power on:

        http://<ip-of-your-device>/cm?cmnd=power<channel number>%20On
        
- power off:

        http://<ip-of-your-device>/cm?cmnd=power<channel number>%20Off
        
- toggle power:

        http://<ip-of-your-device>/cm?cmnd=power<channel number>%20toggle

...and more

<h1>For Experts</h1>

It's possible to use the sonoff.py class module separatly from this addon as a wrapper. If you want to call your switches from shell, just type:

        ./sonoff.py <ip-of-your-device> toggle|on|off <channel (0-3)>
     
 eg:
 
        ./sonoff.py 192.168.1.100 toggle 0
 
Make shure the sonoff.py is executable. Copy the sonoff.py to a place of your needs. You also can use the class module directly in python scripts. Import the class module and use it as follows:
    
    from sonoff.py import *
    Sonoff().send('192.168.1.100', Sonoff().TOGGLE[0]
    
where the 192.168.1.100 is the IP of your device and TOGGLE[0] the first channel that will be toggled. It's also possible to use the commands ON[x], OFF[x], STATUS[x] where x is the number of your device channel - 1 (0-3). 
    