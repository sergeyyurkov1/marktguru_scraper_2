from dash import dcc, html
import dash_bootstrap_components as dbc

from settings import SETTINGS


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "max-height": "100vh",
}

sidebar = html.Div(
    [
        dcc.Store(id="store", storage_type="local"),
        html.Div(
            [
                html.H2(
                    "MarktGuru Scraper", className="display-6", id="sidebar-header"
                ),
                html.Hr(),
            ],
            id="sidebar-header-container",
        ),
        html.Div(
            [
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
                                    outline=True,
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
                                            className="mb-2",
                                        ),
                                    ],
                                    id="tab-1",
                                ),
                            ],
                            className="pt-2",
                            label="Settings",
                        ),
                        dbc.Tab(
                            html.Div(
                                [
                                    dbc.Label("Selectors (after <li> tag)"),
                                    html.Div(
                                        [
                                            dbc.Input(
                                                type="text",
                                                value=SETTINGS["store1"],
                                                placeholder="Store 1",
                                                id="l-input-1",
                                            ),
                                            dbc.Tooltip(
                                                "Selector for Store with <a> tag in the title",
                                                target="l-input-1",
                                                placement="top",
                                            ),
                                            #         dbc.Input(
                                            #             type="text",
                                            #             value=SETTINGS["store2"],
                                            #             placeholder="Store 2",
                                            #             id="store-input-2",
                                            #         ),
                                            #         dbc.Tooltip(
                                            #             "(Fallback) Selector for Store with <span> tag in the title",
                                            #             target="store-input-2",
                                            #             placement="top",
                                            #         ),
                                            #         dbc.Input(
                                            #             type="text",
                                            #             value=SETTINGS["name"],
                                            #             placeholder="Name",
                                            #             id="name-input",
                                            #         ),
                                            #         dbc.Tooltip(
                                            #             "Selector for Name tag",
                                            #             target="name-input",
                                            #             placement="top",
                                            #         ),
                                            #         dbc.Input(
                                            #             type="text",
                                            #             value=SETTINGS["brand1"],
                                            #             placeholder="Brand 1",
                                            #             id="brand-input-1",
                                            #         ),
                                            #         dbc.Tooltip(
                                            #             "Selector for Brand with <a> tag in the title",
                                            #             target="brand-input-1",
                                            #             placement="top",
                                            #         ),
                                            #         dbc.Input(
                                            #             type="text",
                                            #             value=SETTINGS["brand2"],
                                            #             placeholder="Brand 2",
                                            #             id="brand-input-2",
                                            #         ),
                                            #         dbc.Tooltip(
                                            #             "(Fallback) Selector for Brand with <span> tag in the title",
                                            #             target="brand-input-2",
                                            #             placement="top",
                                            #         ),
                                            #         dbc.Input(
                                            #             type="text",
                                            #             value=SETTINGS["dv"],
                                            #             placeholder="Date valid",
                                            #             id="dv-input",
                                            #         ),
                                            #         dbc.Tooltip(
                                            #             "Selector for Date valid tag",
                                            #             target="dv-input",
                                            #             placement="top",
                                            #         ),
                                            #         dbc.Input(
                                            #             type="text",
                                            #             value=SETTINGS["price1"],
                                            #             placeholder="Price 1",
                                            #             id="price-input-1",
                                            #         ),
                                            #         dbc.Tooltip(
                                            #             "Selector for Price/Unit tag in the bottom-left",
                                            #             target="price-input-1",
                                            #             placement="top",
                                            #         ),
                                            #         dbc.Input(
                                            #             type="text",
                                            #             value=SETTINGS["price2"],
                                            #             placeholder="Price 2",
                                            #             id="price-input-2",
                                            #         ),
                                            #         dbc.Tooltip(
                                            #             "(Fallback) Selector for Price tag in the top-right",
                                            #             target="price-input-2",
                                            #             placement="top",
                                            #         ),
                                            #         dbc.Input(
                                            #             type="text",
                                            #             value=SETTINGS["price3"],
                                            #             placeholder="Price 3",
                                            #             id="price-input-3",
                                            #         ),
                                            #         dbc.Tooltip(
                                            #             "(Fallback) Selector for Note tag in the bottom-left (in case no units are found)",
                                            #             target="price-input-3",
                                            #             placement="top",
                                            #         ),
                                        ],
                                        id="location-selectors",
                                    ),
                                ],
                                className="mb-4",
                                id="tab-2",
                            ),
                            className="pt-2",
                            label="Location",
                        ),
                        dbc.Tab(
                            html.Div(
                                [
                                    dbc.Label("Selectors (after <li> tag)"),
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
                                                "(Fallback) Selector for Store with <span> tag in the title",
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
                                                "(Fallback) Selector for Brand with <span> tag in the title",
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
                                className="mb-4",
                                id="tab-3",
                            ),
                            className="pt-2",
                            label="HTML",
                        ),
                    ]
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
                    className="me-1",
                    id="save-button",
                    disabled=False,
                ),
            ],
            className="d-grid gap-2 col-6 mx-auto",
        ),
    ],
    style=SIDEBAR_STYLE,
)
