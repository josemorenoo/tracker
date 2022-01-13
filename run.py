# visit http://127.0.0.1:8050/ in your web browser.

from datetime import datetime

import dash
from dash import dcc
from dash import html

from coincommit.setup_data import load_data
from coincommit.myplotly.plots import Plots
#from hairy_plotter import HairyPlotter
    
# setup
read_from_pickle = False
token="LRC"
start_date = datetime(2022, 1, 11, 12, 00, 00)
end_date = datetime(2022, 1, 12, 12, 00, 00)
timeframe = "day"

'''
project_repos = [
    'https://github.com/bitcoin/bitcoin',
    'https://github.com/bitcoin/bips'
]
'''


project_repos = [
    'https://github.com/Loopring/loopring-explorer',
    #'https://github.com/Loopring/loopring-web-v2',
    #'https://github.com/Loopring/loopring_sdk',
    #'https://github.com/Loopring/dexwebapp',
    #'https://github.com/Loopring/whitepaper'
]

token_data_df, project_commits_list, project_commits_df = load_data(
    token,
    project_repos,
    start_date,
    end_date,
    pickle_data_interval = timeframe, # see data/*/x_commits.pickle for value to put here
    read_from_pickle = read_from_pickle,
    write_to_pickle = not read_from_pickle
)

print(f"commits found for {start_date} through {end_date}: {len(project_commits_list)}")


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
app.layout = html.Div(children=plot_divs)


"""
# matplotlib
hp = HairyPlotter()
hp.show_commmit_plot(token_data_df, project_commits_list)
"""

if __name__ == '__main__':
    app.run_server(debug=True)


    