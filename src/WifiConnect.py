import network

def connect():
    ssid = "BNET"
    password = open("wifi-password.txt").read()

    station = network.WLAN(network.STA_IF)

    if station.isconnected() == True:
        print("Already connected")
        return

    station.active(True)
    station.config(dhcp_hostname='backlight')
    station.connect(ssid, password)

    while station.isconnected() == False:
        pass

    print("Connection successful")
    print(station.ifconfig())
