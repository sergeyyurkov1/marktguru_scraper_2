import os, shutil
from psutil import NoSuchProcess
from threading import Timer
import webbrowser
import logging

from dash import Dash, dcc, html, Input, Output, State, no_update
from dash.long_callback import DiskcacheLongCallbackManager
import diskcache
import dash_bootstrap_components as dbc

from helpers import (
    check_chrome_exe_path,
    load_txt_file,
    write_txt_file,
    read_list,
    get_alert,
    check_chrome_driver_exe_path,
)
from settings import SETTINGS

from selenium_init import Driver
from marktguru_scraper import set_location, launch_scraper, generate_output


# ---------------------------
try:
    shutil.rmtree("cache")
    shutil.rmtree("Chrome")
except (PermissionError, FileNotFoundError):
    pass


cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)


# ---------------------------
def launch_app_mode() -> None:
    webbrowser.open_new("http://127.0.0.1:8050")


def App() -> None:
    external_stylesheets = [dbc.themes.UNITED]

    app = Dash(
        __name__,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True,
        long_callback_manager=long_callback_manager,
    )

    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "20rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
        "overflow-y": "scroll",
        "max-height": "100vh",
    }

    CONTENT_STYLE = {
        "margin-left": "22rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
    }

    sidebar = html.Div(
        [
            dcc.Store(id="store", storage_type="local"),
            html.H2("MarktGuru Scraper", className="display-6"),
            html.Hr(),
            html.Div(
                [
                    dbc.Label("Search URL"),
                    dbc.Input(
                        value="https://www.marktguru.de/search",
                        size="md",
                        className="mb-3",
                        id="url-input",
                        readonly=True,
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Label("Path to Chrome executable"),
                    dbc.InputGroup(
                        [
                            dbc.Input(
                                value=SETTINGS["path"],
                                size="md",
                                id="path-input",
                            ),
                            dbc.Button(
                                "Check",
                                color="primary",
                                n_clicks=0,
                                className="me-1",
                                id="check-button",
                            ),
                        ]
                    ),
                ]
            ),
            html.Hr(),
            dbc.Tabs(
                [
                    dbc.Tab(
                        [
                            html.Div(
                                [
                                    dbc.Label("ZIP code"),
                                    dbc.Input(
                                        value=SETTINGS["zip"],
                                        size="md",
                                        className="mb-3",
                                        id="zip-input",
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    dbc.Label("Display lowest price by"),
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "Search item", "value": "Item"},
                                            {"label": "Product name", "value": "Name"},
                                        ],
                                        value=SETTINGS["lp"],
                                        id="lp-input",
                                        className="mb-3",
                                        inline=True,
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    dbc.Label("Margin of error"),
                                    dbc.Input(
                                        type="number",
                                        value=SETTINGS["moe"],
                                        min=0,
                                        max=10,
                                        step=1,
                                        id="moe-input",
                                    ),
                                    dbc.Tooltip(
                                        "The maximum number of empty results to skip in case of errors on a product page",
                                        target="moe-input",
                                        placement="right",
                                    ),
                                ],
                                id="styled-numeric-input",
                                className="mb-4",
                            ),
                        ],
                        className="pt-2",
                        label="Settings",
                    ),
                    dbc.Tab(
                        html.Div(
                            [
                                dbc.Label("HTML selectors (after <li> tag)"),
                                html.Div(
                                    [
                                        dbc.Input(
                                            type="text",
                                            value=SETTINGS["store1"],
                                            placeholder="Store 1",
                                            id="store-input-1",
                                        ),
                                        dbc.Tooltip(
                                            "Selector for Store with <a> tag in the title",
                                            target="store-input-1",
                                            placement="top",
                                        ),
                                        dbc.Input(
                                            type="text",
                                            value=SETTINGS["store2"],
                                            placeholder="Store 2",
                                            id="store-input-2",
                                        ),
                                        dbc.Tooltip(
                                            "Selector for Store with <span> tag in the title",
                                            target="store-input-2",
                                            placement="top",
                                        ),
                                        dbc.Input(
                                            type="text",
                                            value=SETTINGS["name"],
                                            placeholder="Name",
                                            id="name-input",
                                        ),
                                        dbc.Tooltip(
                                            "Selector for Name tag",
                                            target="name-input",
                                            placement="top",
                                        ),
                                        dbc.Input(
                                            type="text",
                                            value=SETTINGS["brand1"],
                                            placeholder="Brand 1",
                                            id="brand-input-1",
                                        ),
                                        dbc.Tooltip(
                                            "Selector for Brand with <a> tag in the title",
                                            target="brand-input-1",
                                            placement="top",
                                        ),
                                        dbc.Input(
                                            type="text",
                                            value=SETTINGS["brand2"],
                                            placeholder="Brand 2",
                                            id="brand-input-2",
                                        ),
                                        dbc.Tooltip(
                                            "Selector for Brand with <span> tag in the title",
                                            target="brand-input-2",
                                            placement="top",
                                        ),
                                        dbc.Input(
                                            type="text",
                                            value=SETTINGS["dv"],
                                            placeholder="Date valid",
                                            id="dv-input",
                                        ),
                                        dbc.Tooltip(
                                            "Selector for Date valid tag",
                                            target="dv-input",
                                            placement="top",
                                        ),
                                        dbc.Input(
                                            type="text",
                                            value=SETTINGS["price1"],
                                            placeholder="Price 1",
                                            id="price-input-1",
                                        ),
                                        dbc.Tooltip(
                                            "Selector for Price/Unit tag in the bottom-left",
                                            target="price-input-1",
                                            placement="top",
                                        ),
                                        dbc.Input(
                                            type="text",
                                            value=SETTINGS["price2"],
                                            placeholder="Price 2",
                                            id="price-input-2",
                                        ),
                                        dbc.Tooltip(
                                            "Selector for Price tag in the top-right",
                                            target="price-input-2",
                                            placement="top",
                                        ),
                                        dbc.Input(
                                            type="text",
                                            value=SETTINGS["price3"],
                                            placeholder="Price 3",
                                            id="price-input-3",
                                        ),
                                        dbc.Tooltip(
                                            "Selector for Note tag in the bottom-left",
                                            target="price-input-3",
                                            placement="top",
                                        ),
                                    ],
                                    id="html-selectors",
                                ),
                            ],
                            className="mb-4",
                        ),
                        className="pt-2",
                        label="HTML",
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Button(
                        "Save",
                        color="primary",
                        n_clicks=0,
                        className="me-1",
                        outline=True,
                        id="save-button",
                        disabled=False,
                    ),
                ],
                className="d-grid gap-2 col-6 mx-auto",
            ),
        ],
        style=SIDEBAR_STYLE,
    )

    content = html.Div(id="page-content", style=CONTENT_STYLE)

    app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

    main = html.Div(
        [
            html.Div(
                [
                    dbc.Row(
                        id="top-row-0",
                    ),
                    dbc.Row(
                        id="top-row-1",
                    ),
                    dbc.Row(id="top-row-2"),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        dbc.Label("Shopping list"),
                                        dbc.Textarea(
                                            style={"height": "16rem"},
                                            draggable=False,
                                            placeholder="Comment out the items you don't want to buy today - prepend the '#' symbol to the name",
                                            id="shopping-list",
                                        ),
                                    ]
                                )
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        dbc.Label("Blacklist"),
                                        dbc.Textarea(
                                            style={"height": "16rem"},
                                            draggable=False,
                                            placeholder="Put items you don't want to see in search results here. Temporarily unlist an item by prepending '#' to the name",
                                            id="item-blacklist",
                                        ),
                                    ]
                                )
                            ),
                        ],
                        class_name="mb-4",
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                "Scrape",
                                color="primary",
                                n_clicks=0,
                                className="me-1",
                                id="scrape-button",
                            ),
                            dbc.Button(
                                "Stop",
                                color="primary",
                                outline=True,
                                n_clicks=0,
                                className="me-1",
                                id="stop-button",
                                style={"visibility": "hidden"},
                            ),
                            dcc.Input(id="hidden-in", style={"visibility": "hidden"}),
                            html.Div(id="hidden-out", style={"visibility": "hidden"}),
                            dbc.Button(
                                "Open results",
                                color="success",
                                n_clicks=0,
                                className="me-1",
                                id="results-button",
                                style={"visibility": "hidden"},
                            ),
                        ],
                        className="d-grid gap-2 col-5 mx-auto",
                    ),
                ]
            ),
            html.Div(
                [
                    html.Hr(),
                    dbc.Label("Starting", id="label-1"),
                    html.Span(id="span"),
                    dbc.Label(id="label-2"),
                    dbc.Progress(
                        value=100,
                        id="progress",
                        animated=True,
                        striped=True,
                    ),
                ],
                id="progress-container",
                style={"visibility": "hidden"},
            ),
        ],
        id="container",
    )

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
        try:
            if n_clicks:
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

                with Driver(path_, headless=True) as driver:
                    set_progress(("Setting location", "", "", 10))
                    set_location(driver, sl[0], zip_)
                    set_progress(("Location set", "", "", 25))

                    set_progress(("Scraping", "", "", 60))
                    data = launch_scraper(driver, url, moe, sl, zip_, store_data)
                set_progress(("Done scraping", "", "", 80))

                set_progress(("Processing data", "", "", 90))
                file = generate_output(data, lp, ib)
                set_progress(("Done", "", "", 95))

                set_progress(("", "", "", 100))

                return get_alert("Done", "success"), {"visibility": "visible"}, file
        except FileNotFoundError as e:
            set_progress(("", "", "", 100))

            return (
                get_alert(
                    str(e),
                    "danger",
                ),
                no_update,
                no_update,
            )
        except Exception:
            set_progress(("", "", "", 100))

            return (
                get_alert(
                    "Scraping unsuccessful. Please check the settings, HTML tags and save any changes",
                    "danger",
                ),
                no_update,
                no_update,
            )

    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname == "/":
            return main

        return html.Div(
            [html.A("Go Home", href="/")],
            className="p-3",
        )

    Timer(1, launch_app_mode).start()

    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    app.run_server(debug=False)  # debug=True, use_reloader=False


if __name__ == "__main__":
    App()
