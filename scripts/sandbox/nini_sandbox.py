# this is Ninis space, to be touched by no one other than nini
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont
from typing import List

import scripts.reporter.periodic_report as periodic_report
import scripts.reporter.report_util as report_util  

print("\nWelcome to Nini's sandbox. \n")

OUTPUT_DIR = "scripts/sandbox/junk/" # path from root of repo

print("output dir: ", OUTPUT_DIR)

size = (60, 60)
color = 'red'
img = Image.new('RGB', size, color)
drawing = ImageDraw.Draw(img)
drawing.text( (10, 10), "Hello da nene", fill = (0, 0, 0))
img_name = "redbox.png"
img.save(OUTPUT_DIR + "redbox.png")


def create_price_supplemental_image(price_deltas: List[float], height: int = 500, width: int = 150):
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLACKGROUND = (17, 17, 17)

    # create the image
    price_image = Image.new('RGB', (width, height), color=BLACKGROUND)    # same height as original graph
    price_drawing = ImageDraw.Draw(price_image)
    
    # formatting
    my_font = ImageFont.truetype('arial.ttf', 17)
    spacing = 33 # space between each price
    y_offset = 105 # offset from top of image
    x_offset = 5 # offset from left of (new) image -- nice to use to center the DELTA PRICE text with the actual numbers
    
    # Insert "Price Change" Text on top of numbers
    price_drawing.text( (0, y_offset - 30), "\u0394 Price", fill = (255,255, 255), font=my_font)

    # insert the price deltas
    for i in range(0, len(price_deltas)): # num tokens
        price_change = price_deltas[-i-1]
        
        # make font red for negative changes, green for positive changes
        color = GREEN if price_change >= 0 else RED
        price_drawing.text((x_offset, y_offset + spacing*i), str(price_change)+" %", fill=color, font=my_font)
        
    return price_image


def combine_graph_and_price_img(bar_graph_img, price_img):
    combined_img = Image.new('RGB', (bar_graph_img.width + price_img.width, bar_graph_img.height))
    combined_img.paste(bar_graph_img, (0, 0))
    combined_img.paste(price_img, (bar_graph_img.width, 0))
    return combined_img


def add_price_deltas_to_existing_img(report_date: datetime, mode="DAILY"):
    report_date_str = report_date.strftime("%Y-%m-%d")

    # first, load the summary report for the same date the img was made
    summary_report = report_util.get_summary_report(report_date)
    
    # each of these lists contains 10 token names,
    # there are three lists because there are three graphs we support, currently
    # Note that lists are reversed to match the order of tokens as they appear in the horizontal bar graphs
    top_commits_chart_tokens_represented = [token_info['token'] for token_info in summary_report['top_by_num_commits']][::-1]
    top_loc_chart_tokens_represented = [token_info['token'] for token_info in summary_report['top_by_new_lines']][::-1]
    top_authors_chart_tokens_represented = [token_info['token'] for token_info in summary_report['top_by_num_distinct_authors']][::-1]

    # this is a function used in each of the three list-comprehensions used below,
    # it gets the daily_delta_percentage for a given token name from the summary_report
    get_price_percentage_delta = lambda token: summary_report['tokens_represented'][token]['daily_delta_percentage']
    commits_price_deltas = [get_price_percentage_delta(token) for token in top_commits_chart_tokens_represented]
    locs_price_deltas = [get_price_percentage_delta(token) for token in top_loc_chart_tokens_represented]
    authors_price_deltas = [get_price_percentage_delta(token) for token in top_authors_chart_tokens_represented]

    def open_existing_img(chart_name: str, report_date_str: datetime, mode: str):
        # load graphs with top commits, top lines of code and top authors
        return Image.open(f'reports/{mode.lower()}/{report_date_str}/{chart_name}')
    top_commits_im_raw = open_existing_img('top_commits.png', report_date_str, mode)
    top_loc_im_raw = open_existing_img('top_commits.png', report_date_str, mode)
    top_authors_im_raw = open_existing_img('top_commits.png', report_date_str, mode)

    def crop_original_photo(original_img):
        # crop original graph images to avoid having a lot of space on the right where the price will be inserted.
        return original_img.crop((0, 0, 630, original_img.height))
    top_commits_im = crop_original_photo(top_commits_im_raw)
    top_loc_im = crop_original_photo(top_loc_im_raw)
    top_authors_im = crop_original_photo(top_authors_im_raw)


    #  ------- Create image of price daily changes ------------ 
    width, height = top_commits_im.size
    print("Image width, height: ", width, height)  

    top_commits_price_im = create_price_supplemental_image(commits_price_deltas, height)
    top_loc_price_im = create_price_supplemental_image(locs_price_deltas, height)
    top_authors_price_im = create_price_supplemental_image(authors_price_deltas, height)
    
    # ---------- combine image of prices with stats image ------------
    top_commits_and_price_img = combine_graph_and_price_img(top_commits_im, top_commits_price_im)
    top_loc_and_price_img = combine_graph_and_price_img(top_loc_im, top_loc_price_im)
    top_authors_and_price_img = combine_graph_and_price_img(top_authors_im, top_authors_price_im)

    print("\nToken: ", top_commits_chart_tokens_represented)
    print("deltas: ", commits_price_deltas)

    print("\nToken: ", top_loc_chart_tokens_represented)
    print("deltas: ", locs_price_deltas)

    print("\nToken: ", top_authors_chart_tokens_represented)
    print("deltas: ", authors_price_deltas)
    
    
    # save file
    IMG_OUTPUT_DIR = f'reports/daily/{report_date_str}'
    top_commits_and_price_img.save(f"{IMG_OUTPUT_DIR}/top_commits_and_price.png")
    top_loc_and_price_img.save(f"{IMG_OUTPUT_DIR}/top_commits_and_price.png")
    top_authors_and_price_img.save(f"{IMG_OUTPUT_DIR}/top_commits_and_price.png")
    
    #top_commits_and_price_img.show()
    #top_authors_and_price_img.show()
    #top_loc_and_price_img.show()

if __name__ == "__main__":
    # add price deltas to existing commits count image
    img_date = datetime(2022, 2, 12)
    add_price_deltas_to_existing_img(img_date)

