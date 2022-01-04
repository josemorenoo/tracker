import dash
from dash import dcc
from dash import html

def create_dash():
    # create dash instance
    dash_app = dash.Dash(__name__)
    return dash_app

def add_layout(dash_app, fig):
    # create the dashboard page
    dash_app.layout = html.Div([
        dcc.Graph(
            id='price-vs-some-metric',
            figure=fig
        )
    ])

def run_dash(dash_app):
    # this needs to run last AFTER you configure the dash_app object layout
    dash_app.run_server(debug=True)
