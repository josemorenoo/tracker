# visit http://127.0.0.1:8050/ in your web browser.

from datetime import datetime

from setup import load_data
from myPlotly.dash_util import *
from myPlotly.plots import *
#from HairyPlotter import HairyPlotter


if __name__ == "__main__":
    # setup
    read_from_pickle = True
    token="LRC"
    start_date = datetime(2021, 1, 1, 12, 00, 00)
    end_date = datetime(2022, 1, 1, 12, 00, 00)
    timeframe = "year"

    project_repos = [
        'https://github.com/Loopring/loopring-web-v2',
        'https://github.com/Loopring/loopring_sdk',
        'https://github.com/Loopring/dexwebapp',
        'https://github.com/Loopring/whitepaper'
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


    # generate plotly figs
    commits_fig = create_commits_plot(token, token_data_df, project_commits_list, project_commits_df)
    agg_commits_fig = create_aggregate_commit_count_plot(token, token_data_df, project_commits_list)
    agg_loc_fig = create_lines_of_code_plot(token, token_data_df, project_commits_list)
    figures = [commits_fig, agg_loc_fig, agg_commits_fig]
    
    # plot them
    dash_app = create_dash()
    add_layout(dash_app, figures)
    run_dash(dash_app)
    

    """
    # matplotlib
    hp = HairyPlotter()
    hp.show_commmit_plot(token_data_df, project_commits_list)
    """


    