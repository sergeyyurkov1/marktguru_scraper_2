import shutil
import subprocess
import webbrowser
from typing import Optional

try:
    import winreg
except ImportError:
    winreg = None


def read_app_paths(browser: str) -> Optional[str]:
    if winreg == None:
        return None

    APP_PATHS = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
    browser += ".exe"

    try:
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, APP_PATHS, 0, winreg.KEY_READ
            ) as key:
                return winreg.QueryValue(key, browser)
        except FileNotFoundError:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, APP_PATHS, 0, winreg.KEY_READ
            ) as key:
                return winreg.QueryValue(key, browser)
    except OSError:
        return None


def get_exe(browser: str) -> Optional[str]:
    return shutil.which(browser) or read_app_paths(browser)


BROWSERS = [
    "chrome",
    "msedge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
]

FALLBACK_BROWSERS = [
    "windows-default",
    "macosx",
    "wslview %s",  # WSL
    "x-www-browser %s",
    "gnome-open %s",
    "firefox",
    "opera",
    "safari",
]


def open(url: str, try_app_mode: bool = True) -> None:
    if try_app_mode:
        for browser in BROWSERS:
            exe = get_exe(browser)
            if exe:
                try:
                    p = subprocess.Popen(
                        [exe, f"--app={url}"], close_fds=True, start_new_session=True
                    )
                    return_code = p.poll()
                    if return_code:
                        raise OSError(return_code)
                except OSError:
                    pass
                else:
                    return

    for browser in FALLBACK_BROWSERS:
        try:
            b = webbrowser.get(browser)
        except webbrowser.Error:
            pass
        else:
            if b.open(url):
                return

    raise RuntimeError("No browser found")
