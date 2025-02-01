import logging
import os
import shutil
import time
import traceback
from threading import Timer

import dash_bootstrap_components as dbc
import diskcache
from dash import Dash, Input, Output, State, callback, ctx, dcc, html, no_update
from dash.long_callback import DiskcacheLongCallbackManager
from selenium.common.exceptions import (
    ElementNotInteractableException,
    SessionNotCreatedException,
    TimeoutException,
)
from soupsieve.util import SelectorSyntaxError

import native_web_app
from components.main import main
from components.sidebar import sidebar
from helpers import (
    check_chrome_exe_path,
    download_chromedriver,
    get_alert,
    get_chrome_version,
    load_txt_file,
    read_list,
    write_txt_file,
)
from marktguru_scraper import generate_output, launch_scraper, set_location
from selenium_init import ChromeBinaryNotFound, get_driver
from settings import SETTINGS


def launch_app() -> None:
    native_web_app.open("http://127.0.0.1:8050")


def App(long_callback_manager) -> None:
    external_stylesheets = [dbc.themes.UNITED, dbc.icons.BOOTSTRAP]

    app = Dash(
        __name__,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True,
        long_callback_manager=long_callback_manager,
    )

    page = html.Div(id="page-content")

    app.layout = html.Div([dcc.Location(id="url"), sidebar, page])

    # ---------------------------------------------------------------------------------
    @callback(
        Output("modal-centered", "is_open"),
        Input("open-centered", "n_clicks"),
        State("modal-centered", "is_open"),
    )
    def toggle_modal(n1, is_open):
        if n1:
            return not is_open
        return is_open

    # Storage block
    # ---------------------------
    # Works
    @callback(
        Output("path-input", "value"),
        Output("zip-input", "value"),
        Output("lp-input", "value"),
        #
        Output("store-input-1", "value"),
        Output("name-input", "value"),
        Output("brand-input-1", "value"),
        Output("dv-input", "value"),
        Output("price-input-1", "value"),
        Output("price-input-2", "value"),
        Output("price-input-3", "value"),
        #
        Output("filter", "value"),
        #
        Input("store", "modified_timestamp"),
        State("store", "data"),
    )
    def get_from_store(modified_timestamp, data):
        # print(data)
        data = data or SETTINGS

        return (
            data.get("path"),
            data.get("zip"),
            data.get("lp"),
            #
            data.get("store1"),
            data.get("name"),
            data.get("brand1"),
            data.get("dv"),
            data.get("price1"),
            data.get("price2"),
            data.get("price3"),
            #
            data.get("filter"),
        )

    # ---------------------------
    @callback(
        Output("top-row-0", "children"),
        Output("store", "data"),
        #
        Input("save-button", "n_clicks"),
        Input("reset-button", "n_clicks"),
        #
        State("path-input", "value"),
        State("zip-input", "value"),
        State("lp-input", "value"),
        #
        State("store-input-1", "value"),
        State("name-input", "value"),
        State("brand-input-1", "value"),
        State("dv-input", "value"),
        State("price-input-1", "value"),
        State("price-input-2", "value"),
        State("price-input-3", "value"),
        #
        State("store", "data"),
        #
        State("filter", "value"),
        #
        # prevent_initial_call=True,  # on load
    )
    def set_to_store(
        n1,
        n2,
        #
        path_,
        zip_,
        lp,
        #
        store1,
        name,
        brand1,
        dv,
        price1,
        price2,
        price3,
        #
        store_data,
        #
        filter,
    ):
        store_data = {}

        store_data["path"] = path_
        store_data["zip"] = zip_
        store_data["lp"] = lp
        #
        store_data["store1"] = store1 or SETTINGS["store1"]
        store_data["name"] = name or SETTINGS["name"]
        store_data["brand1"] = brand1 or SETTINGS["brand1"]
        store_data["dv"] = dv or SETTINGS["dv"]
        store_data["price1"] = price1 or SETTINGS["price1"]
        store_data["price2"] = price2 or SETTINGS["price2"]
        store_data["price3"] = price3 or SETTINGS["price3"]
        #
        if filter != None:
            store_data["filter"] = filter
        else:
            store_data["filter"] = SETTINGS["filter"]

        # print(store_data)

        # ---------------------------
        triggered_id = ctx.triggered_id
        if triggered_id == "reset-button":
            return get_alert("Settings reset", "success"), SETTINGS
        elif triggered_id == "save-button":
            return get_alert("Settings saved", "success"), store_data
        else:
            return "", store_data

    @callback(
        Output("hidden-out", "children"),
        Input("results-button", "n_clicks"),
        State("hidden-in", "value"),
        prevent_initial_call=True,
    )
    def open_file(n_clicks, value):
        os.startfile(value)

        return ""

    @callback(
        Output("shopping-list", "value"),
        Output("item-blacklist", "value"),
        Input("check-button", "n_clicks"),
    )
    def load_lists(n_clicks):
        return load_txt_file("shopping_list"), load_txt_file("item_blacklist")

    @callback(
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

    @callback(
        Output("collapse", "is_open"),
        [Input("collapse-button", "n_clicks")],
        [State("collapse", "is_open")],
    )
    def toggle_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

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
        shopping_list,
        item_blacklist,
        store_data,
    ):
        if n_clicks:
            try:
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

                try:
                    driver = get_driver(path_, headless=True)
                    assert driver is not None
                except ChromeBinaryNotFound as e:
                    set_progress(("...", "", "", 100, no_update))

                    return (
                        get_alert(
                            e,
                            "warning",
                        ),
                        no_update,
                        no_update,
                    )
                except (
                    FileNotFoundError,  # driver not found error
                    SessionNotCreatedException,  # driver version error
                    AssertionError,  # other driver error
                ):
                    set_progress(
                        ("Downloading Chrome driver...", "", "", 50, no_update)
                    )
                    version = get_chrome_version(path_)
                    download_chromedriver(version)
                    set_progress(("...", "", "", 100, no_update))

                    driver = get_driver(path_, headless=True)

                # ---------------------------
                set_progress(("Setting location", "", "", 10))
                try:
                    set_location(driver, sl[0], zip_)
                except ElementNotInteractableException:
                    pass
                set_progress(("Location set", "", "", 20))

                time.sleep(1)

                # ---------------------------
                set_progress(("Scraping", "", "", 40))
                data = launch_scraper(driver, url, sl, zip_, store_data, set_progress)
                set_progress(("Done scraping", "", "", 80))

                time.sleep(1)

                # ---------------------------
                set_progress(("Processing data", "", "", 90))
                file = generate_output(data, lp, ib, store_data["filter"])
                set_progress(("Writing Excel file", "", "", 95))

                time.sleep(1)

                # ---------------------------
                set_progress(("...", "", "", 100))

                return (
                    get_alert("Scraping successful", "success"),
                    {"visibility": "visible"},
                    file,
                )
            except SelectorSyntaxError as e:
                set_progress(("...", "", "", 100, no_update))

                return (
                    get_alert(
                        f"{e}. Bad selector format. Please check HTML selectors for changes, save the settings, and retry",
                        "warning",
                    ),
                    no_update,
                    no_update,
                )
            except TimeoutException as e:
                set_progress(("...", "", "", 100, no_update))

                return (
                    get_alert(
                        "Selenium timed out. Please retry",
                        "warning",
                    ),
                    no_update,
                    no_update,
                )
            except ProcessLookupError:
                pass
            except Exception as e:
                set_progress(("...", "", "", 100, no_update))

                traceback_text = traceback.format_exc()

                if str(e).startswith("Warning: "):
                    return (
                        get_alert(
                            e,
                            "warning",
                        ),
                        no_update,
                        no_update,
                    )

                return (
                    get_alert(
                        e,
                        "danger",
                        traceback=True,
                        traceback_text=traceback_text,
                    ),
                    no_update,
                    no_update,
                )
            finally:
                try:
                    driver.quit()
                except:
                    set_progress(("...", "", "", 100, no_update))

    @callback(Output("page-content", "children"), [Input("url", "pathname")])
    def output_page_content(pathname):
        return main

    # ---------------------------
    Timer(1, launch_app).start()

    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    app.run_server(debug=False)  # debug=True, use_reloader=False

    print()


if __name__ == "__main__":
    try:
        shutil.rmtree("cache")
        shutil.rmtree("Chrome")
    except (PermissionError, FileNotFoundError):
        pass

    cache = diskcache.Cache("./cache")
    long_callback_manager = DiskcacheLongCallbackManager(cache)

    App(long_callback_manager)
