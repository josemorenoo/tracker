# visit http://127.0.0.1:8050/ in your web browser.

from datetime import datetime

from coincommit.setup_data import load_data
from coincommit.myPlotly.dash_util import *
from coincommit.myPlotly.plots import *
#from HairyPlotter import HairyPlotter


if __name__ == "__main__":
    # setup
    read_from_pickle = True
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
        create_aggregate_commit_count_plot,
        create_lines_of_code_plot,
        create_number_of_authors_plot
    ]

    # initialize the figures list with the commits function, which takes an extra parameter
    figures = [create_commits_plot(token, token_data_df, project_commits_list, project_commits_df)]

    # all the other functions take the same three parameters so just call them in a loop and figs to list
    figures.extend([f(token, token_data_df, project_commits_list) for f in plotting_functions])
    
    # plot them
    dash_app, server = create_dash()
    add_layout(dash_app, figures)
    run_dash(dash_app)
    

    """
    # matplotlib
    hp = HairyPlotter()
    hp.show_commmit_plot(token_data_df, project_commits_list)
    """


    