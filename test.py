import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import string
import re
import datetime
import time
import os

all_links = []
location = []
events = []
f1 = []
f2 = []
winner = []
f1_odds = []
f2_odds = []
label = []
favourite = []

def scrape_data():
    # Fetch the HTML content from the URL
    url = "https://www.betmma.tips/mma_betting_favorites_vs_underdogs.php?Org=1"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    data = requests.get(url, headers=headers, timeout=30)

    # set up page to extract table
    #data = requests.get("https://www.betmma.tips/mma_betting_favorites_vs_underdogs.php?Org=1")
    soup = BeautifulSoup(data.text, 'html.parser')

    # table with 98% width 
    table = soup.find('table', {'width': "98%"})
    # find all links in that table
    #links = table.find_all('a', href=True)
    links = table.find_all('a', href=True, limit=5)  # Limit to 5 links for testing

    # append all links to a list 
    for link in links:
        all_links.append("https://www.betmma.tips/"+link.get('href'))

    # test for one use case
    for link in all_links:
        print(f"Now scraping: {link}")

        data = requests.get(link)
        soup = BeautifulSoup(data.text, 'html.parser')
        time.sleep(1)
        # specific table with the information
        rows = soup.find_all('table', {'cellspacing': "5"})

        # Move outside the row loop
        h1 = soup.find("h1")
        h2 = soup.find("h2")
        event_name = h1.text if h1 else "Unknown Event"
        location_info = h2.text if h2 else "Unknown Location"

        for row in rows:

            # check for draw, if draw, then skip
            # dictionary of won and lost
            odds = row.find_all('td', {'align': "center", 'valign': "middle"})
            # to avoid taking in draws
            if odds[0].text not in ['WON', 'LOST']:
                continue

            # Use the cached values
            events.append(event_name)
            location.append(location_info)

            odds_f1 = float(odds[2].text.strip(" @"))
            odds_f2 = float(odds[3].text.strip(" @"))

            f1_odds.append(odds_f1)
            f2_odds.append(odds_f2)

            # how to generate label
            odds_dict = {}
            odds_dict[odds[0].text] = odds_f1
            odds_dict[odds[1].text] = odds_f2 

            if odds_dict["WON"] > odds_dict["LOST"]:
                label.append("Underdog")
            else:
                label.append("Favourite")

            if odds_f1 > odds_f2:
                favourite.append("f2")
            else:
                favourite.append("f1")


            fighters = row.find_all('a', attrs={'href': re.compile("^fighter_profile.php")})
            f1.append(fighters[0].text)
            f2.append(fighters[1].text)
            winner.append(fighters[2].text)
    return None

def create_df():
    
    # creating dataframe
    df = pd.DataFrame()
    df["Events"] = events
    df["Location"] = location
    df["Fighter1"] = f1
    df["Fighter2"] = f2
    df["Winner"] = winner
    df["fighter1_odds"] = f1_odds
    df["fighter2_odds"] = f2_odds
    df["Favourite"] = favourite
    df["Label"] = label
    print(f"Successfully scraped {df.shape[0]} fights and last fight card was {df.iloc[-1, :]['Events']} {df.iloc[-1, :]['Location']}")
    print(df["Label"].value_counts()/len(df))
    
    return df

# Run the scraping function and create the DataFrame
scrape_data()
df = create_df()

# Save the DataFrame to a CSV file
#df.to_csv('data.csv', index=False)
df.to_csv('test.csv', index=False) # Save the DataFrame to a CSV file for testing
