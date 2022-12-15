import os, shutil, time
from psutil import NoSuchProcess
from threading import Timer
import webbrowser
import logging

from dash import Dash, dcc, html, Input, Output, State, no_update
from dash.long_callback import DiskcacheLongCallbackManager
import diskcache
import dash_bootstrap_components as dbc

from selenium.common.exceptions import SessionNotCreatedException

from helpers import (
    check_chrome_exe_path,
    load_txt_file,
    write_txt_file,
    read_list,
    get_alert,
    check_chrome_driver_exe_path,
)
from settings import SETTINGS
from components.sidebar import sidebar
from components.main import main

from selenium_init import get_driver
from marktguru_scraper import set_location, launch_scraper, generate_output


# ---------------------------
def launch_app() -> None:
    webbrowser.open_new("http://127.0.0.1:8050")


def App() -> None:
    external_stylesheets = [dbc.themes.UNITED]

    app = Dash(
        __name__,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True,
        long_callback_manager=long_callback_manager,
    )

    CONTENT_STYLE = {
        "margin-left": "22rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
    }

    content = html.Div(id="page-content", style=CONTENT_STYLE)

    app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

    # ---------------------------------------------------------------------------------
    @app.callback(
        Output("path-input", "value"),
        Output("zip-input", "value"),
        Output("lp-input", "value"),
        Output("moe-input", "value"),
        #
        Output("store-input-1", "value"),
        Output("store-input-2", "value"),
        Output("name-input", "value"),
        Output("brand-input-1", "value"),
        Output("brand-input-2", "value"),
        Output("dv-input", "value"),
        Output("price-input-1", "value"),
        Output("price-input-2", "value"),
        Output("price-input-3", "value"),
        #
        Input("store", "modified_timestamp"),
        State("store", "data"),
    )
    def get_from_store(modified_timestamp, data):
        data = data or SETTINGS

        return (
            data.get("path"),
            data.get("zip"),
            data.get("lp"),
            data.get("moe"),
            #
            data.get("store1"),
            data.get("store2"),
            data.get("name"),
            data.get("brand1"),
            data.get("brand2"),
            data.get("dv"),
            data.get("price1"),
            data.get("price2"),
            data.get("price3"),
        )

    @app.callback(
        Output("top-row-0", "children"),
        Output("store", "data"),
        #
        Input("save-button", "n_clicks"),
        #
        State("path-input", "value"),
        State("zip-input", "value"),
        State("lp-input", "value"),
        State("moe-input", "value"),
        #
        State("store-input-1", "value"),
        State("store-input-2", "value"),
        State("name-input", "value"),
        State("brand-input-1", "value"),
        State("brand-input-2", "value"),
        State("dv-input", "value"),
        State("price-input-1", "value"),
        State("price-input-2", "value"),
        State("price-input-3", "value"),
        #
        State("store", "data"),
        prevent_initial_call=True,
    )
    def set_to_store(
        n_clicks,
        #
        path_,
        zip_,
        lp,
        moe,
        #
        store1,
        store2,
        name,
        brand1,
        brand2,
        dv,
        price1,
        price2,
        price3,
        #
        store_data,
    ):
        if n_clicks:
            store_data = store_data or {}

            store_data["path"] = path_
            store_data["zip"] = zip_
            store_data["lp"] = lp
            store_data["moe"] = int(moe)
            #
            store_data["store1"] = store1 or SETTINGS["store1"]
            store_data["store2"] = store2 or SETTINGS["store2"]
            store_data["name"] = name or SETTINGS["name"]
            store_data["brand1"] = brand1 or SETTINGS["brand1"]
            store_data["brand2"] = brand2 or SETTINGS["brand2"]
            store_data["dv"] = dv or SETTINGS["dv"]
            store_data["price1"] = price1 or SETTINGS["price1"]
            store_data["price2"] = price2 or SETTINGS["price2"]
            store_data["price3"] = price3 or SETTINGS["price3"]

            return get_alert("Settings saved", "success"), store_data

    @app.callback(
        Output("hidden-out", "children"),
        Input("results-button", "n_clicks"),
        State("hidden-in", "value"),
        prevent_initial_call=True,
    )
    def open_file(n_clicks, value):
        os.startfile(value)

        return ""

    @app.callback(
        Output("shopping-list", "value"),
        Output("item-blacklist", "value"),
        Input("check-button", "n_clicks"),
    )
    def load_lists(n_clicks):
        return load_txt_file("shopping_list"), load_txt_file("item_blacklist")

    @app.callback(
        Output("top-row-2", "children"),
        Input("check-button", "n_clicks"),
        State("path-input", "value"),
    )
    def toggle_path_alert(n_clicks, value):
        if n_clicks:
            exists = check_chrome_exe_path(value)
            if exists:
                return get_alert("Chrome executable found", "success")
            return get_alert("Chrome executable not found", "danger")

    # ---------------------------------------------------------------------------------
    @app.long_callback(
        prevent_initial_call=True,
        output=[
            Output("top-row-1", "children"),
            Output("results-button", "style"),
            Output("hidden-in", "value"),
        ],
        inputs=[
            Input("scrape-button", "n_clicks"),
            State("url-input", "value"),
            State("path-input", "value"),
            State("zip-input", "value"),
            State("lp-input", "value"),
            State("moe-input", "value"),
            State("shopping-list", "value"),
            State("item-blacklist", "value"),
            State("store", "data"),
        ],
        running=[
            (Output("scrape-button", "disabled"), True, False),
            (
                Output("stop-button", "style"),
                {"visibility": "visible"},
                {"visibility": "hidden"},
            ),
            (
                Output("progress-container", "style"),
                {"visibility": "visible"},
                {"visibility": "hidden"},
            ),
        ],
        progress=[
            Output("label-1", "children"),
            Output("span", "children"),
            Output("label-2", "children"),
            Output("progress", "value"),
        ],
        cancel=[Input("stop-button", "n_clicks")],
    )
    def scrape(
        set_progress,
        n_clicks,
        url,
        path_,
        zip_,
        lp,
        moe,
        shopping_list,
        item_blacklist,
        store_data,
    ):
        if n_clicks:
            try:
                if not check_chrome_exe_path(path_):
                    raise FileNotFoundError(
                        "Chrome executable not found. Please check the settings and save any changes"
                    )
                if not check_chrome_driver_exe_path():
                    raise FileNotFoundError("chromedriver.exe not found")

                write_txt_file("shopping_list", shopping_list)
                write_txt_file("item_blacklist", item_blacklist)

                sl = read_list(shopping_list)
                ib = read_list(item_blacklist)

                if len(sl) == 0:
                    return (
                        get_alert("Shopping list is empty", "danger"),
                        no_update,
                        no_update,
                    )

                driver = get_driver(path_, headless=True)

                set_progress(("Setting location", "", "", 10))
                try:
                    set_location(driver, sl[0], zip_)
                except Exception as e:
                    return (
                        get_alert(
                            f"{str(e)}. Please check HTML selectors for Location. Refer to 'log.txt' to find which selector is causing the issue",
                            "danger",
                        ),
                        no_update,
                        no_update,
                    )
                finally:
                    if driver is not None:
                        driver.quit()

                set_progress(("Location set", "", "", 20))

                time.sleep(1)

                set_progress(("Scraping", "", "", 40))
                data = launch_scraper(
                    driver, url, moe, sl, zip_, store_data, set_progress
                )
                set_progress(("Done scraping", "", "", 80))

                time.sleep(1)

                set_progress(("Processing data", "", "", 90))
                file = generate_output(data, lp, ib)
                set_progress(("Writing Excel file", "", "", 95))

                time.sleep(1)

                set_progress(("...", "", "", 100))

                return (
                    get_alert("Scraping successful", "success"),
                    {"visibility": "visible"},
                    file,
                )
            except FileNotFoundError as e:
                set_progress(("...", "", "", 100))

                return (
                    get_alert(
                        str(e),
                        "danger",
                    ),
                    no_update,
                    no_update,
                )
            except SessionNotCreatedException as e:
                set_progress(("...", "", "", 100))

                return (
                    get_alert(
                        f"{str(e)}. Please download the right driver version from https://chromedriver.chromium.org/downloads",
                        "danger",
                    ),
                    no_update,
                    no_update,
                )

            except Exception as e:
                set_progress(("...", "", "", 100))

                return (
                    get_alert(
                        str(e),
                        "danger",
                    ),
                    no_update,
                    no_update,
                )
            finally:
                if driver is not None:
                    driver.quit()

    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname == "/":
            return main

        return html.Div(
            [html.A("Go Home", href="/")],
            className="p-3",
        )

    # Timer(1, launch_app).start()

    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    app.run_server(debug=True)  # debug=True, use_reloader=False


if __name__ == "__main__":
    try:
        shutil.rmtree("cache")
        shutil.rmtree("Chrome")
    except (PermissionError, FileNotFoundError):
        pass

    cache = diskcache.Cache("./cache")
    long_callback_manager = DiskcacheLongCallbackManager(cache)

    App()
