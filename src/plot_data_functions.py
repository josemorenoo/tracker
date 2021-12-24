# functions useful for plotting data
import matplotlib  
# needed on mac otherwise crashes
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

import pickle
import pandas as pd
import os
from typing import List,Any

def main():
    print("\n\nTesting plots")

    # load pickle files
    directory = os.getcwd() + "/"
    
    with open(directory + 'one_day_project_commits_pickle' , 'rb') as pickle_file:
        project_commits = pickle.load(pickle_file)
    with open(directory + 'one_day_token_data_pickle' , 'rb') as pickle_file:
        token_data = pickle.load(pickle_file)


    print("Time in token_data")
    #print(*token_data.index.tolist(), sep="\n")
    
    print(token_data.describe())
    
    print("\n\n")
    #print(*token_data['close'].tolist(), sep="\n")
    print(token_data.head(3))

    print("Time in commits")
    print(*[c.rounded_commit_time_5min for c in project_commits], sep="\n")

    show_commmit_plot(token_data, project_commits)


    ############ end of code #########
    print("the end. \n\n")    
    
    
    
def show_histogram_commit_count(token_data: pd.DataFrame, commits: List[Any]):
    #p = token_data.plot(y='close', use_index=True)

    
    
def show_commmit_plot(token_data: pd.DataFrame, commits: List[Any]):
    p = token_data.plot(y='close', use_index=True)
    for commit in commits:
        p.axvline(x=commit.rounded_commit_time_5min, color='g', linestyle='--', linewidth=0.1)
    plt.show()


if __name__ == "__main__":
    main()
    

