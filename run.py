# visit http://127.0.0.1:8050/ in your web browser.

from datetime import datetime
import json

import dash
from dash import dcc
from dash import html

from src.setup_data import load_data
from src.myplotly.plots import Plots
    
# setup
read_from_pickle = True
token="LRC"
start_date = datetime(2022, 1, 20, 12, 00, 00)
end_date = datetime(2022, 1, 25, 12, 00, 00)
timeframe = "month"

# get repo list
repos = json.load(open('src/config/repos.json'))
project_repos = repos[token]['repos']


token_data_df, project_commits_list, project_commits_df = load_data(
    token,
    project_repos,
    start_date,
    end_date,
    pickle_data_interval = timeframe, # see data/*/x_commits.pickle for value to put here
    read_from_pickle = read_from_pickle,
    write_to_pickle = not read_from_pickle
)

print(f"{len(project_commits_list)} commits found between {start_date} and {end_date}")


# this is a list of FUNCTIONS, each one takes in the same three parameters and outputs a fig
# they are called below in a loop, this makes it easier to add and remove plots to show on the dashboard
plotting_functions = [
    Plots.create_aggregate_commit_count_plot,
    Plots.create_lines_of_code_plot,
    Plots.create_number_of_authors_plot
]

# initialize the figures list with the commits function, which takes an extra parameter
figures = [Plots.create_commits_plot(token, token_data_df, project_commits_list, project_commits_df)]

# all the other functions take the same three parameters so just call them in a loop and figs to list
figures.extend([f(token, token_data_df, project_commits_list) for f in plotting_functions])

# create dash instance
app = dash.Dash(__name__)
server = app.server


# add each figure provided as its own div
plot_divs = []
for fig_id, fig in enumerate(figures):
    plot_divs.append(html.Div([
        dcc.Graph(
            id=str(fig_id),
            figure=fig
        )
    ]))


# create the dashboard page
app.layout = html.Div(children=plot_divs)


"""
# matplotlib
hp = HairyPlotter()
hp.show_commmit_plot(token_data_df, project_commits_list)
"""

if __name__ == '__main__':
    app.run_server(debug=True)


    