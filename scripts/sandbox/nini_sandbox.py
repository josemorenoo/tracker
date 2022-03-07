# this is Ninis space, to be touched by no one other than nini
from datetime import datetime
import json
import os
from PIL import Image, ImageDraw, ImageFont
from typing import List


from webapp.setup_data import load_data
from webapp.frontend.plots import Plots
    
# setup
read_from_pickle = False
token="XYO"
start_date = datetime(2021, 2, 20, 12, 00, 00)
end_date = datetime(2022, 2, 28, 12, 00, 00)
timeframe = "year" # [day, week, month, year]


OUTPUT_DIR = "scripts/sandbox/junk/" # path from root of repo

def nini_main():
    print("\nWelcome to Nini's sandbox. \n")

    print("Nini main")
    # get repo list
    repos = json.load(open('config/repos.json'))
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


if __name__ == "__main__":
    nini_main()
