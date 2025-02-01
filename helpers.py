import re
import sys
from os import listdir, path
from zipfile import ZipFile

import dash_bootstrap_components as dbc
import pandas as pd
import requests
from dash import html

from settings import SETTINGS


def read_settings() -> dict:
    try:
        with open("settings.yaml", "r", encoding="utf-8") as f:
            return yaml.load(f)
    except FileNotFoundError:
        write_settings(SETTINGS)


def write_settings(data: dict) -> None:
    try:
        with open("settings.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f)
    except Exception as e:
        print(e)


def rank_similarity(df: pd.DataFrame) -> pd.DataFrame:
    unfiltered_df = df.copy()

    grouped_unfiltered_df = unfiltered_df.groupby(["Item"])

    groups = []
    for name, group in grouped_unfiltered_df:
        gdf = group[group["Name"].str.endswith(name)]
        groups.append(gdf)

    filtered_df = pd.concat(groups)

    return filtered_df


def get_chrome_version(path: str) -> str:
    """Get local Chrome version sans the subversion"""
    chrome_dir = path.rsplit("\\", 1)[0]
    return listdir(chrome_dir)[0].rsplit(".", 1)[0]


def download_chromedriver(version: str) -> None:
    downloads_url = "https://chromedriver.chromium.org/downloads"
    downloads_html = requests.get(downloads_url).text

    # Parse HTML: match version, reverse sort the results, get latest version
    latest_version = sorted(re.findall(version + r"\.\d{2}", downloads_html))[::-1][0]

    chromedriver_url = f"https://chromedriver.storage.googleapis.com/{latest_version}/chromedriver_win32.zip"
    response = requests.get(chromedriver_url, allow_redirects=True)

    if response.status_code != requests.codes.ok:
        download_chromedriver(version)

    open("chromedriver.zip", "wb").write(response.content)

    with ZipFile("chromedriver.zip", "r") as chromedriver_zip:
        chromedriver_zip.extractall()


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


def read_list(input_: str) -> list:
    return [
        line.rstrip().lower()
        for line in input_.splitlines()
        if not line.startswith("#") and not line.rstrip() == ""
    ]  # strips spaces and new lines


def get_alert(
    text: str, color: str, traceback: bool = False, traceback_text: str = ""
) -> dbc.Alert:
    if traceback:
        alert = dbc.Alert(
            [
                str(text),
                html.Hr(),
                dbc.Button(
                    "Show/Hide traceback",
                    id="collapse-button",
                    className="mb-3",
                    outline=True,
                    color="primary",
                    n_clicks=0,
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody(str(traceback_text))),
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
                str(text),
                color=color,
                is_open=True,
                dismissable=True,
            )
        else:
            alert = dbc.Alert(
                str(text),
                color=color,
                is_open=True,
                duration=5_000,
            )

    return alert


if __name__ == "__main__":
    ...
