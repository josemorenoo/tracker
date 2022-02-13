# this is Ninis space, to be touched by no one other than nini
from datetime import datetime
import os
from PIL import Image, ImageDraw

import scripts.reporter.periodic_report as periodic_report

print("\nWelcome to Nini's sandbox. \n")

wdir = os.getcwd()
output_dir = wdir[0:-7] + "junk/"

print("output dir: ", output_dir)

size = (60, 60)
color = 'red'
img = Image.new('RGB', size, color)

drawing = ImageDraw.Draw(img)
drawing.text( (10, 10), "Hello da nene", fill = (0, 0, 0))

img_name = "redbox.png"
img.save(output_dir + "redbox.png")

# pseudocode

def add_price_deltas_to_existing_img(img_date: datetime):

    # first get the name of the top 10 coins (Jose)

    # first, load the summary report for the same date the img was made
    summary_report = periodic_report.get_summary_report(img_date)

    # each of these lists contains 10 token names,
    # there are three lists because there are three graphs we support, currently
    # Note that lists are reversed to match the order of tokens as they appear in the horizontal bar graphs
    top_commits_chart_tokens_represented = [token for token in summary_report['top_by_num_commits'].values()][::-1]
    top_loc_chart_tokens_represented = [token for token in summary_report['top_by_new_lines'].values()][::-1]
    top_authors_chart_tokens_represented = [token for token in summary_report['top_by_num_distinct_authors'].values()][::-1]

    # get the price change (Jose)

    # this is a function used in each of the three list-comprehensions used below,
    # it gets the daily_delta_percentage for a given token name from the summary_report
    get_price_percentage_delta = lambda token: summary_report['tokens_represented'][token]['daily_delta_percentage']

    # each of these lists has 10 percentage values, one for each token in each graph
    commits_price_deltas = [get_price_percentage_delta(token) for token in top_commits_chart_tokens_represented]
    locs_price_deltas = [get_price_percentage_delta(token) for token in top_loc_chart_tokens_represented]
    authors_price_deltas = [get_price_percentage_delta(token) for token in top_authors_chart_tokens_represented]

    # create image of prices (Nicole) -- need [coin1, coin2, coin3] and [price1, price2, price3]

    # combine image of prices with stats image (Nicole)



# img_display = Image.open(output_dir+ img_name)
# img.show()