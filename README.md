# aQRootG3 #
### Enable telnet access via QRCode command Injection for Aqara G3 ###

<p align="center" width="100%">
    <img src="https://user-images.githubusercontent.com/1288525/152621650-993c5630-c749-4758-9609-e5421df4d7ff.png"> 
</p>

:warning:  **WARNING** :warning:
---------------
Aqara have closed the exploit in firmware 3.3.9_0011.0004 by filtering ``` `$'";|&\``` from variables.

It is unlikely that this method of exploitation will ever work again in newer version. It was good while it lasted. 

Aqara - go f*ck yourselves.

Intro
---------------
I was disappointed to see the Aqara G3 camera did not ship with telnet enabled so I managed to grab a copy of a firmware update for some good 'ol static analysis which confirmed none of the previous methods were going to work.

Whilst going through  "ha_master" I did see that one of the variables passed in by the setup qrcode is thrown through sprintf as "nslookup %s" and subsequently passed to popen (yay).

Getting telnet was fairly trivial, getting persistent telnet in one shot within the 132 char sprintf buffer on a readonly filesystem was a little more challenging.

Thankfully another qrcode variable (b aka bind_key) has a larger buffer so we store some data in this which can later be used by the main payload.


Usage
---------------
```bash
usage: aQRootG3.py [-h] ssid pwd [filename]

aQRootG3 v0.x
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
> :warning:  **NOTE**
> 
> *Due to the amount of data in the QRCode, it is no longer possible for the camera to read from a small screen (such as a phone).*\
> *With default settings the QRCode needs to be displayed at a minimum of ~110x110mm to scan successfully.*


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
payload=[
    'y=/data/scripts/post_init.sh',         
    '"fw_man"ager.sh -t -f',                        # Create default /data/scripts/post_init.sh
    'echo -e `agetprop persist.app.bind_key`>$y',   # Write post_init[] content below to post_init.sh
    'tail -n2 $y|sh'                                # Clear $USER password, enable tty and start telnetd
],
post_init = [
    '#!/bin/sh',
    'fw_manager.sh -r',                             # Start firmware as normal
    'passwd -d $USER',                              # Clear $USER password
    'fw_manager.sh -t -k'                           # Enable tty and start telnetd
],
}
```

Tested Versions
---------------

| Firmware Version | Status |
| --------------- | -- |
| 3.2.7_0019.0004 | :white_check_mark: |
| 3.3.2_0003.0004  | :white_check_mark: |
| 3.3.4_0007.0004  | :white_check_mark: |
| 3.3.9_0011.0004  | :no_entry_sign: |


