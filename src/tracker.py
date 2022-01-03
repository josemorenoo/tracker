# visit http://127.0.0.1:8050/ in your web browser.

from datetime import datetime
import dash
from dash import dcc
from dash import html
import plotly.express as px


from setup import load_data
#from HairyPlotter import HairyPlotter


if __name__ == "__main__":
    # setup
    read_from_pickle = True
    token="LRC"
    start_date = datetime(2021, 12, 1, 12, 00, 00)
    end_date = datetime(2021, 12, 2, 12, 00, 00)

    project_repos = [
        'https://github.com/Loopring/loopring-web-v2',
        'https://github.com/Loopring/loopring_sdk',
        'https://github.com/Loopring/dexwebapp',
        'https://github.com/Loopring/whitepaper'
    ]

    token_data_df, project_commits_list = load_data(
        token,
        project_repos,
        start_date,
        end_date,
        pickle_data_interval = 'day',
        read_from_pickle = read_from_pickle,
        write_to_pickle = not read_from_pickle
    )

    # create dash instance
    dash_app = dash.Dash(__name__)
    

    # add price plot
    fig = px.line(token_data_df, x='datetime', y="close")
    # fig.add_trace(go.Scatter(mode="markers", x=df["Date"], y=df["AAPL.Close"], name="daily"))

    dash_app.layout = html.Div([
        dcc.Graph(
            id='price-vs-some-metric',
            figure=fig
        )
    ])

    # this needs to run last AFTER you configure the dash_app object layout
    dash_app.run_server(debug=True)

    """
    # matplotlib
    hp = HairyPlotter()
    hp.show_commmit_plot(token_data_df, project_commits_list)
    """


    