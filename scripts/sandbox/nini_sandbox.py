# this is Ninis space, to be touched by no one other than nini
from datetime import datetime
import json
from typing import List
import numpy as np
from matplotlib import pyplot as plt
from webapp.setup_data import load_data
from webapp.stats_util import Stats

from sklearn.linear_model import LinearRegression
    
# setup
read_from_pickle = True
token="LRC"
start_date = datetime(2021, 6, 3, 12, 00, 00)
end_date = datetime(2022, 3, 3, 12, 00, 00)
timeframe = "june2021_march2022" # [day, week, month, year]

# to do: figure out a better way of importing data. I want to look at multiple timestamps

OUTPUT_DIR = "scripts/sandbox/junk/" # path from root of repo

def nini_main():
    print("\nWelcome to Nini's sandbox. \n")

    print("Nini main")
    # get repo list
    repos = json.load(open('config/repos.json', encoding="utf8"))
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
    
    
    # let's see the available keys
    #print("\nToken data keys: ", token_data_df.keys)
    #print("\nProject commits keys: ", project_commits_df.keys)
    #print("\nCommits list: ", project_commits_list)
    
    
    plot_price_againts_commits(token_data_df, project_commits_list)
    plt.show()
    return 0 # end of main

def plot_price_againts_commits(token_data_df, project_commits_list):
    stats = Stats()

    # get list of # of commits (and accompanying time stamp)
    ts_list, daily_counts_list = stats.calculate_commit_count_in_range(project_commits_list,  '1day')
    
    # get list of closing price
    close_prices = get_closing_price_from_ts(ts_list, token_data_df)

    # do a linear fit 
    fitted_prices, r_sq = linear_fit(daily_counts_list, close_prices)
    
    print("Offset: ", 0, "R2 score: ", r_sq)
    
    # plot them against each other
    plot_potential_correlation(daily_counts_list, close_prices, fitted_prices, 
                               "Daily Commit Count", "Close Price U$", 10, True)
    
    
    # Now let me see if anything interesting happens if I look one day in advance, two days in advance..
    offsets = [1, 7, 30, 60, 90, 120]
    
    for offset in offsets:
        #offset = 2
        x = daily_counts_list[:-offset] 
        y = close_prices[offset:] 
        y_fit, r_sq = linear_fit(x, y)
        plot_potential_correlation(x, y, y_fit, "Daily Commit Count", "Close Price U$", offset+10, True )
        print("Offset: ", offset, "R2 score: ", r_sq)
    
    
    
    
    return 0

def plot_potential_correlation(x, y, y_fit, x_name, y_name, fig_count=1, show_fit=True):
    plt.figure(fig_count)
    plt.scatter(x, y)
    if show_fit:
        plt.plot(x, y_fit, color="black")
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.title(token)
    
    
    

def linear_fit(x_data, y_data):
    """Function to perform a simple linear regression using the sklearn functions. Returns fitted y and rsquared

    Args:
        x_data (_type_): _description_
        y_data (_type_): _description_

    Returns:
        _type_: _description_
    """
    lr_model = LinearRegression()
    lr_model.fit(np.array(x_data).reshape(-1, 1), np.array(y_data))
    r_sq = lr_model.score(np.array(x_data).reshape(-1, 1), np.array(y_data))
    y_fitted = linear(x_data, lr_model.coef_, lr_model.intercept_)

    return y_fitted, r_sq

def get_closing_price_from_ts(ts_list, token_data_df):
    """Function to get the closing price given a timestamp in milliseconds

    Args:
        ts_list (_type_): _description_

    Returns:
        _type_: _description_
    """
    close_prices = []
    
    for ts in ts_list:
        ts_s = int(ts/1000) # need to convert from ms to s
        dt = datetime.fromtimestamp(ts_s) # get datetime object so that we can use the key to find the price
        date_string = dt.strftime("%Y-%m-%d")
        close_prices.append(token_data_df.Close[date_string])
    return close_prices


def linear(x, a, b):
    return a*x + b
    

if __name__ == "__main__":
    nini_main()
