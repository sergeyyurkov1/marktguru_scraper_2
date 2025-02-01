import dash_bootstrap_components as dbc
from dash import dcc, html

main = html.Div(
    [
        html.Div(
            [
                # Notification area
                # ---------------------------
                dbc.Row(
                    id="top-row-0",
                ),
                dbc.Row(
                    id="top-row-1",
                ),
                dbc.Row(id="top-row-2"),
                # ---------------------------
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    dbc.Label("Shopping list", class_name="h5"),
                                    dbc.Textarea(
                                        # ---------------------------
                                        style={"height": "16rem", "resize": "none"},
                                        draggable=False,
                                        placeholder="Comment out the items you don't want to buy today - prepend the '#' symbol to the name",
                                        id="shopping-list",
                                    ),
                                ],
                            ),
                            className="col-12 col-sm-6",
                            id="shopping-list-container",
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dbc.Label("Blacklist", class_name="h5"),
                                            # dbc.Checkbox(
                                            #     id="filter",
                                            #     label="Apply auto filtering",
                                            #     value=False,
                                            # ),
                                        ],
                                        id="label-textarea",
                                    ),
                                    dbc.Textarea(
                                        # ---------------------------
                                        style={"height": "16rem", "resize": "none"},
                                        draggable=False,
                                        placeholder="Put items you don't want to see in search results here. Temporarily unlist an item by prepending '#' to the name",
                                        id="item-blacklist",
                                    ),
                                ],
                            ),
                            className="col-12 col-sm-6",
                        ),
                    ],
                    # ---------------------------
                    class_name="mb-4",
                ),
                # ---------------------------
                dbc.Row(
                    [
                        dbc.Button(
                            "Scrape",
                            color="primary",
                            n_clicks=0,
                            id="scrape-button",
                            className="controls-buttons",
                        ),
                        dbc.Button(
                            "Stop",
                            color="primary",
                            outline=True,
                            n_clicks=0,
                            id="stop-button",
                            style={"visibility": "hidden"},
                            className="controls-buttons",
                        ),
                        dcc.Input(id="hidden-in", style={"visibility": "hidden"}),
                        html.Div(id="hidden-out", style={"visibility": "hidden"}),
                        dbc.Button(
                            "Open results",
                            color="success",
                            n_clicks=0,
                            id="results-button",
                            style={"visibility": "hidden"},
                            className="controls-buttons",
                        ),
                    ],
                    className="controls",
                ),
            ]
        ),
        # ---------------------------
        html.Div(
            [
                dbc.Modal(
                    [
                        dbc.ModalHeader(
                            dbc.ModalTitle("HTML Selectors"), close_button=True
                        ),
                        dbc.ModalBody(
                            html.Img(id="image", src=r"assets/default-selectors.png"),
                            id="modal-body",
                        ),
                    ],
                    id="modal-centered",
                    centered=True,
                    is_open=False,
                ),
            ]
        ),
        # ---------------------------
        html.Div(
            [
                html.Hr(),
                dbc.Label("...", id="label-1"),
                html.Span("", id="span"),
                dbc.Label("", id="label-2"),
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
