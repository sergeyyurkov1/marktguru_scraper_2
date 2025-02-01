import dash_bootstrap_components as dbc
from dash import dcc, html

from settings import SETTINGS

sidebar = html.Div(
    [
        dcc.Store(id="store", storage_type="local"),
        # ---------------------------
        html.Div(
            [
                html.H2(
                    "MarktGuru Scraper", className="display-7", id="sidebar-header"
                ),
                html.Hr(),
            ],
            id="sidebar-header-container",
        ),
        # ---------------------------
        html.Div(
            [
                html.Div(
                    [
                        dbc.Label("Search URL"),
                        dbc.Input(
                            value="https://www.marktguru.de/search",
                            size="md",
                            id="url-input",
                            readonly=True,
                        ),
                    ],
                    className="mb-3",
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
                                    outline=True,
                                    n_clicks=0,
                                    id="check-button",
                                ),
                            ],
                            style={"background-color": "white"},
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
                                        html.Div(
                                            [
                                                dbc.Label("ZIP code"),
                                                dbc.Input(
                                                    value=SETTINGS["zip"],
                                                    size="md",
                                                    id="zip-input",
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        html.Div(
                                            [
                                                dbc.Label("Display lowest price by"),
                                                dbc.RadioItems(
                                                    options=[
                                                        {
                                                            "label": "Search item",
                                                            "value": "Item",
                                                        },
                                                        {
                                                            "label": "Product name",
                                                            "value": "Name",
                                                        },
                                                    ],
                                                    value=SETTINGS["lp"],
                                                    id="lp-input",
                                                    inline=True,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        html.Div(
                                            [
                                                # dbc.Label(""),
                                                dbc.Checkbox(
                                                    id="filter",
                                                    label="Apply auto filtering",
                                                    value=False,
                                                ),
                                                dbc.Tooltip(
                                                    "Filters results that are close to items searched. Can be used together with the blacklist.",
                                                    target="filter",
                                                    placement="bottom",
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                    ],
                                    id="tab-1",
                                ),
                            ],
                            className="p-2 ",
                            label="Settings",
                            style={"background-color": "white"},
                        ),
                        # dbc.Tab(
                        #     html.Div(
                        #         [
                        #             dbc.Label("Selectors"),
                        #         ],
                        #         id="tab-2",
                        #     ),
                        #     label="Location",
                        # ),
                        dbc.Tab(
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dbc.Label(
                                                "Selectors (after <li> tag)",
                                            ),
                                            html.I(
                                                id="open-centered",
                                                className="bi bi-info-circle-fill",
                                                style={"color": "var(--bs-orange)"},
                                            ),
                                        ],
                                        id="label-i",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Input(
                                                type="text",
                                                value=SETTINGS["store1"],
                                                placeholder="Store 1",
                                                id="store-input-1",
                                            ),
                                            dbc.Tooltip(
                                                "Selector for Store tag",
                                                target="store-input-1",
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
                                                "Selector for Brand tag",
                                                target="brand-input-1",
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
                                                "(Fallback) Selector for Price tag in the top-right",
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
                                                "(Fallback) Selector for Note tag in the bottom-left (in case no units are found)",
                                                target="price-input-3",
                                                placement="top",
                                            ),
                                        ],
                                        id="html-selectors",
                                    ),
                                ],
                                id="tab-3",
                            ),
                            className="p-2",
                            label="HTML",
                            style={"background-color": "white"},
                        ),
                    ],
                ),
            ],
            id="fixed",
            className="mb-4",
        ),
        html.Div(
            [
                dbc.Button(
                    "Save",
                    color="primary",
                    n_clicks=0,
                    id="save-button",
                    disabled=False,
                ),
                dbc.Button(
                    "Reset",
                    color="primary",
                    n_clicks=0,
                    id="reset-button",
                    disabled=False,
                    outline=True,
                ),
            ],
            id="sr-buttons",
        ),
    ],
    id="sidebar",
)
