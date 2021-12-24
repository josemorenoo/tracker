# functions useful for plotting data
import matplotlib  
# needed on mac otherwise crashes
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

import pickle

import os

def main():
    print("\n\nTesting plots")

    # load pickle files
    directory = os.getcwd()
    
    with open(directory + '../one_day_token_data_pickle' , 'rb') as pickle_file:
        token_data = pickle.load(pickle_file)
    with open(directory + '../one_day_commits_time_data_pickle' , 'rb') as pickle_file:
        commits_time_data = pickle.load(pickle_file)

    print("the end. \n\n")    
    
    


if __name__ == "__main__":
    main()
    

