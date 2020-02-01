import network
import utime

def connect(ssid, password, hostname):
    station = network.WLAN(network.STA_IF)

    if station.isconnected() == True:
        print("Already connected")
        return

    station.active(True)
    station.config(dhcp_hostname=str(hostname))
    station.connect(ssid, password)

    while station.isconnected() == False:
        utime.sleep_ms(100)
        pass

    print("Connection successful")
    print(station.ifconfig())
