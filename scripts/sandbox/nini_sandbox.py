# this is Ninis space, to be touched by no one other than nini
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont

import scripts.reporter.periodic_report as periodic_report
import scripts.reporter.report_util as report_util  

print("\nWelcome to Nini's sandbox. \n")

output_dir = "scripts/sandbox/junk/" # path from root of repo

print("output dir: ", output_dir)

size = (60, 60)
color = 'red'
img = Image.new('RGB', size, color)
drawing = ImageDraw.Draw(img)
drawing.text( (10, 10), "Hello da nene", fill = (0, 0, 0))
img_name = "redbox.png"
img.save(output_dir + "redbox.png")





def add_price_deltas_to_existing_img(img_date: datetime):

    # first, load the summary report for the same date the img was made
    summary_report = report_util.get_summary_report(img_date)
    
    # each of these lists contains 10 token names,
    # there are three lists because there are three graphs we support, currently
    # Note that lists are reversed to match the order of tokens as they appear in the horizontal bar graphs
    top_commits_chart_tokens_represented = [token_info['token'] for token_info in summary_report['top_by_num_commits']][::-1]
    top_loc_chart_tokens_represented = [token_info['token'] for token_info in summary_report['top_by_new_lines']][::-1]
    top_authors_chart_tokens_represented = [token_info['token'] for token_info in summary_report['top_by_num_distinct_authors']][::-1]

    # get the price change (Jose)

    # this is a function used in each of the three list-comprehensions used below,
    # it gets the daily_delta_percentage for a given token name from the summary_report
    get_price_percentage_delta = lambda token: summary_report['tokens_represented'][token]['daily_delta_percentage']

    # each of these lists has 10 percentage values, one for each token in each graph
    commits_price_deltas = [get_price_percentage_delta(token) for token in top_commits_chart_tokens_represented]
    #locs_price_deltas = [get_price_percentage_delta(token) for token in top_loc_chart_tokens_represented]
    #authors_price_deltas = [get_price_percentage_delta(token) for token in top_authors_chart_tokens_represented]

    # load graphs with top commits, top lines of code and top authors
    top_commits_im_raw = Image.open('reports/daily/2022-02-12/top_commits.png')
    top_loc_im_raw = Image.open('reports/daily/2022-02-12/top_loc.png')
    top_authors_im_raw = Image.open('reports/daily/2022-02-12/top_distinct_authors.png')
    # crop original graph images to avoid having a lot of space on the right where the price will be inserted.
    top_commits_im = top_commits_im_raw.crop((0, 0, 630, top_commits_im_raw.height))
    top_loc_im = top_loc_im_raw.crop((0, 0, 630, top_loc_im_raw.height))
    top_authors_im = top_authors_im_raw.crop((0, 0, 630, top_authors_im_raw.height))
    
    width, height = top_commits_im.size
    print("Image width, height: ", width, height)

    #  ------- Create image of price daily changes ------------   
    # start the image
    price_image = Image.new('RGB', (150, height), color=(17, 17, 17) )    # same height as original graph
    n_tokens = len(top_authors_chart_tokens_represented) # number of tokens
    price_drawing = ImageDraw.Draw(price_image)
    
    # formatting
    myFont = ImageFont.truetype('arial.ttf', 17)
    spacing = 33 # space between each price
    y_offset = 105 # offset from top of image
    x_offset = 5 # offset from left of (new) image -- nice to use to center the DELTA PRICE text with the actual numbers
    
    # Insert "Price Change" Text on top of numbers
    price_drawing.text( (0, y_offset - 30), "\u0394 Price", fill = (255,255, 255), font=myFont)
    # insert the actual numbers
    for i in range(0, n_tokens):
        price_change = commits_price_deltas[-i-1]
        # make font red for negative changes, green for positive changes
        if price_change >= 0:
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)
        price_drawing.text( (x_offset, y_offset + spacing*i), str(price_change)+" %", fill =color, font=myFont)
    
    # ---------- combine image of prices with stats image ------------
    top_commits_and_price = Image.new('RGB', (top_commits_im.width + price_image.width, height))
    top_commits_and_price.paste(top_commits_im, (0, 0))
    top_commits_and_price.paste(price_image, (top_commits_im.width, 0))
    
    top_loc_and_price = Image.new('RGB', (top_loc_im.width + price_image.width, height))
    top_loc_and_price.paste(top_loc_im, (0, 0))
    top_loc_and_price.paste(price_image, (top_loc_im.width, 0))
    
    top_authors_and_price = Image.new('RGB', (top_authors_im.width + price_image.width, height))
    top_authors_and_price.paste(top_authors_im, (0, 0))
    top_authors_and_price.paste(price_image, (top_authors_im.width, 0))
    
    print("Token: ", top_authors_chart_tokens_represented)
    print("deltas: ", commits_price_deltas)
    
    top_commits_and_price.show()
    top_authors_and_price.show()
    top_loc_and_price.show()

# add price deltas to existing commits count image
img_date = datetime(2022, 2, 12)
add_price_deltas_to_existing_img(img_date)


# img_display = Image.open(output_dir+ img_name)
# img.show()