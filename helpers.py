from os import path
from dash import html
import dash_bootstrap_components as dbc


def check_chrome_exe_path(p: str) -> bool:
    return "chrome.exe" in p and path.exists(p)


def check_chrome_driver_exe_path() -> bool:
    return path.exists("chromedriver.exe")


def load_txt_file(file) -> str:
    try:
        with open(f"{file}.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        with open(f"{file}.txt", "w", encoding="utf-8") as f:
            f.write("")

            return load_txt_file(file)


def write_txt_file(file: str, txt: str) -> None:
    try:
        with open(f"{file}.txt", "w", encoding="utf-8") as f:
            f.write(txt)
    except Exception as e:
        print(e)


def read_list(input: str) -> list:
    return [
        line.rstrip().lower()
        for line in input.splitlines()
        if not line.startswith("#") and not line.rstrip() == ""
    ]  # strips spaces and new lines


def get_alert(text, color, traceback=False, traceback_text=""):
    if traceback:
        alert = dbc.Alert(
            [
                text,
                html.Hr(),
                dbc.Button(
                    "See traceback",
                    id="collapse-button",
                    className="mb-3",
                    outline=True,
                    color="primary",
                    n_clicks=0,
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody(traceback_text)),
                    id="collapse",
                    is_open=False,
                ),
            ],
            color=color,
            is_open=True,
            dismissable=True,
        )
    else:
        if color in ["danger", "warning"]:
            alert = dbc.Alert(
                text,
                color=color,
                is_open=True,
                dismissable=True,
            )
        else:
            alert = dbc.Alert(
                text,
                color=color,
                is_open=True,
                duration=5_000,
            )

    return alert
