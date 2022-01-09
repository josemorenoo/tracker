import dash
from dash import dcc
from dash import html

def create_dash():
    # create dash instance
    dash_app = dash.Dash(__name__)
    server = dash_app.server
    return dash_app, server

def add_layout(dash_app, figures):
    plot_divs = []

    # add each figure provided as its own div
    for fig_id, fig in enumerate(figures):
        plot_divs.append(html.Div([
            dcc.Graph(
                id=str(fig_id),
                figure=fig
            )
        ]))

    # create the dashboard page
    dash_app.layout = html.Div(children=plot_divs)
    

def run_dash(dash_app):
    # this needs to run last AFTER you configure the dash_app object layout
    dash_app.run_server(debug=True)
