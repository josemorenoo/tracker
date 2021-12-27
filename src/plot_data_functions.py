# functions useful for plotting data

# example on plotting dates in x axis:
# https://www.tutorialspoint.com/plotting-dates-on-the-x-axis-with-python-s-matplotlib




import matplotlib  
# needed on mac otherwise crashes
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

from statistics_functions import calculate_daily_commit_count
import pickle
import pandas as pd
import os
from typing import List,Any
from datetime import datetime


def main():
    print("\n\nTesting plots")

    # load pickle files
    directory = os.getcwd() + "/"
    
    with open(directory + 'one_week_project_commits_pickle' , 'rb') as pickle_file:
        project_commits = pickle.load(pickle_file)
    with open(directory + 'one_week_token_data_pickle' , 'rb') as pickle_file:
        token_data = pickle.load(pickle_file)


    #print("Time in token_data")
    #print(*token_data.index.tolist(), sep="\n")
    
    #print(token_data.describe())
    
    #print("\n\n")
    #print(*token_data['close'].tolist(), sep="\n")
    #print(token_data.head(3))

    #print("Time in commits")
    #print(*[c.rounded_commit_time_5min for c in project_commits], sep="\n")

    plot_daily_count(token_data, project_commits, plot_price=True)
    #show_commmit_plot(token_data, project_commits)




    ############ end of code #########
    plt.show()
    print("the end. \n\n")    
    
    
    
#def show_histogram_commit_count(token_data: pd.DataFrame, commits: List[Any]):
#    #p = token_data.plot(y='close', use_index=True)
#    num_bins = 100
#    plt.hist()
    
def generate_price_plot(token_data: pd.DataFrame):
    return token_data.plot(y='close', use_index=True)

    
def show_commmit_plot(token_data: pd.DataFrame, commits: List[Any]):
    price_plot = generate_price_plot(token_data)
    for commit in commits:
        price_plot.axvline(x=commit.rounded_commit_time_5min, color='g', linestyle='--', linewidth=0.1)
    plt.show()

    
def plot_daily_count(token_data: pd.DataFrame, commits: List[Any], plot_price=False):
    # plot the daily count of commits over time
    
    # first, calculate the daily price
    fig, ax1 = plt.subplots()
    sorted_days, sorted_commit_counts = calculate_daily_commit_count(commits)
    
    ax1.plot(sorted_days, sorted_commit_counts)  


if __name__ == "__main__":
    main()
    

