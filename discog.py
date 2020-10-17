from datetime import datetime
import json
import os
from openpyxl import Workbook
from openpyxl.styles import Font
import re
import requests
import time


def timer(func):
    """
    Print the runtime of the decorated function
    :param func: function that we want to be timed
    :return: value of function, but prints string of how long function ran
    """
    import functools
    import time
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.time()
        value = func(*args, **kwargs)
        end_time = time.time()
        run_time = end_time - start_time
        if run_time > 3659:
            hours = int(run_time/3600)
            print(f"Finished {func.__name__} in {hours:.0f} hours, {(run_time-hours*3600)/60:.0f} minutes and {run_time%60:.0f} secs")
        elif run_time > 59:
            print(f"Finished {func.__name__} in {run_time/60:.0f} minutes and {run_time%60:.0f} secs")
        else:
            print(f"Finished {func.__name__} in {run_time:.2f} secs")
        return value

    return wrapper_timer


def collection_call(next_page=1, page_call=''):
    """
    Makes an API call to get collection
    :param next_page: boolean if this is the first call
    :param string of api call
    :return: list of details for collection item, pagination dict
    """
    user_name = os.getenv('USER_NAME')
    token = os.getenv('DISCOGS_TOKEN')
    if next_page == 1:
        get_url = 'https://api.discogs.com/users/{}/collection/folders/0/releases?token={}'.format(user_name, token)
    else:
        get_url = page_call

    r = requests.get(get_url)
    response = r.json()

    return response.get("releases"), response.get("pagination")


def collection_grab():
    """
    Iterates over discogs collection API call to build a list() of titles
    :return: completed list of all items in Discogs collection
    """
    titles = list()

    init_titles, pagination = collection_call()
    titles += init_titles

    page_tries = pagination.get("pages")
    next_call = pagination.get("urls", {}).get("next")

    if page_tries == 1:
        print("Titles less than 50")
    else:
        for page in range(2, page_tries+1):
            new_titles, new_page = collection_call(page, next_call)
            titles += new_titles
            next_call = new_page.get("urls", {}).get("next")

    print("Total collection is {} items".format(len(titles)))

    return titles


def title_flatten(title_dict):
    """
    Flattens the title dictionary, removing some details
    :param title_dict: dict() of json title response from Discogs
    :return:
    """
    time.sleep(2)
    title_flat = dict()
    bi = title_dict.get("basic_information")
    title_id = title_dict.get("id")
    discog_artist = bi.get("artists", {})[0]["name"]
    artist = re.sub('.(\d+\))', '', discog_artist).rstrip()
    title = bi.get("title")

    # IDs

    title_flat["id"] = title_id
    title_flat["master_id"] = bi.get("master_id")

    # Time
    date_long = title_dict.get("date_added").split("T")
    title_flat["date_added"] = date_long[0]
    title_flat["time_added"] = date_long[1]

    # Release Details
    title_flat["artist"] = artist
    title_flat["artist_id"] = bi.get("artists", {})[0]["id"]
    title_flat["title"] = title
    title_flat["year"] = bi.get("year")
    title_flat["format"] = bi.get("formats", {})[0]["name"]
    title_flat["format_info"] = bi.get("formats", {})[0].get("text", "N/A")
    title_flat["genres"] = str(bi.get("genres"))[1:-1]
    title_flat["styles"] = str(bi.get("styles"))[1:-1]

    # Collection Notes
    title_flat["notes"] = title_dict.get("notes", {})[0]["value"]

    # Get Lowest Price
    rs_url = requests.get('https://api.discogs.com/marketplace/stats/{}?curr_abbr=USD&token={}'.format(title_id,
                                                                                    os.getenv('DISCOGS_TOKEN')))
    release_stats = rs_url.json()
    if not release_stats.get("num_for_sale"):
        print("{} by {} has no copies for sale".format(title, artist))
        lowest_price = 0.0
    else:
        lowest_price = release_stats.get("lowest_price", {}).get("value", 0.0)

    title_flat["lowest_price"] = lowest_price

    return title_flat


def collection_lowest_price(title_list):
    """
    Prints out total value (based on lowest available price in market) for your collection
    :param title_list:
    :return:
    """
    missing = list()
    prices = list()

    for title in title_list:
        price = title.get("lowest_price")
        if not price:
            missing.append(title.get("title"))
        else:
            prices.append(price)

    tot_value = round(sum(prices), 2)
    str_missing = str(missing)[1:-1]

    print("Total value is {} but prices are missing from {}".format(tot_value, str_missing))

    return


def list_to_xl(title_list):
    """
    Iterates flattend lists and converts them to excel, saved in current folder
    :param title_list:
    :return:
    """
    # Creating Workbook
    wb = Workbook()
    ws = wb.active

    # Setting Up Headers
    ws['A1'] = 'ID'
    ws['B1'] = 'Artist'
    ws['C1'] = 'Title'
    ws['D1'] = 'Year'
    ws['E1'] = 'Format'
    ws['F1'] = 'Format Info'
    ws['G1'] = 'Genres'
    ws['H1'] = 'Styles'
    ws['I1'] = 'Lowest Price'
    ws['J1'] = 'Date Added'
    ws['K1'] = 'Time Added'
    ws['L1'] = 'Artist ID'
    ws['M1'] = 'Master ID'
    ws['N1'] = 'Notes'

    a1 = ws['A1']
    b1 = ws['B1']
    c1 = ws['C1']
    d1 = ws['D1']
    e1 = ws['E1']
    f1 = ws['F1']
    g1 = ws['G1']
    h1 = ws['H1']
    i1 = ws['I1']
    j1 = ws['J1']
    k1 = ws['K1']
    l1 = ws['L1']
    m1 = ws['M1']
    n1 = ws['N1']

    headers = [a1, b1, c1, d1, e1, f1, g1, h1, i1, j1, k1, l1, m1, n1]
    for cell in headers:
        cell.font = Font(size=14, bold=True)
    for row_num, row in enumerate(title_list, 2):
        ws['A{}'.format(row_num)] = row.get("id")
        ws['B{}'.format(row_num)] = row.get('artist')
        ws['C{}'.format(row_num)] = row.get('title')
        ws['D{}'.format(row_num)] = row.get('year')
        ws['E{}'.format(row_num)] = row.get('format')
        ws['F{}'.format(row_num)] = row.get('format_info')
        ws['G{}'.format(row_num)] = row.get('genres')
        ws['H{}'.format(row_num)] = row.get('styles')
        ws['I{}'.format(row_num)] = row.get('lowest_price')
        ws['J{}'.format(row_num)] = row.get('date_added')
        ws['K{}'.format(row_num)] = row.get('time_added')
        ws['L{}'.format(row_num)] = row.get('artist_id')
        ws['M{}'.format(row_num)] = row.get('master_id')
        ws['N{}'.format(row_num)] = row.get('notes')

    # Saving
    today = str(datetime.today())[:10].replace('-','_')
    wb.save("discogs_collection{}.xlsx".format(today))

    return
