import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

testing = False # Set to True for testing with limited data

def scrape_all_fight_data(is_testing=False):
    """
    Scrapes all fight data from betmma.tips, starting from the main events page.
    
    Args:
        is_testing (bool): If True, scrapes only a limited number of events.
        
    Returns:
        list: A list of dictionaries, where each dictionary represents a single fight.
    """
    scraped_fights = []
    # Fetch the HTML content from the URL
    url = "https://www.betmma.tips/mma_betting_favorites_vs_underdogs.php?Org=1"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status() # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', {'width': "98%"})
        limit = 5 if is_testing else None
        links = table.find_all('a', href=True, limit=limit)
        
        if is_testing:
            print(f"Testing with {len(links)} event links")
            
        event_links = ["https://www.betmma.tips/" + link.get('href') for link in links]
        
        for link in event_links:
            print(f"Now scraping: {link}")
            try:
                event_response = requests.get(link, headers=headers, timeout=30)
                event_response.raise_for_status()
                event_soup = BeautifulSoup(event_response.text, 'html.parser')
                time.sleep(1) # Be polite to the server
                
                event_name = event_soup.find("h1").text.strip() if event_soup.find("h1") else "Unknown Event"
                location_info = event_soup.find("h2").text.strip() if event_soup.find("h2") else "Unknown Location"
                
                fight_rows = event_soup.find_all('tr', {'class': ['even', 'odd']})
                
                for row in fight_rows:
                    # Find fighter names and winner first
                    fighter_links = row.find_all('a', href=re.compile(r"^fighter_profile\.php"))
                    if len(fighter_links) < 3: continue # Skip rows without enough fighter data
                    
                    fighter1_name = fighter_links[0].text.strip()
                    fighter2_name = fighter_links[1].text.strip()
                    winner_name = fighter_links[2].text.strip()
                    
                    # Find odds and result
                    odds_cells = row.find_all('td', {'align': "center", 'valign': "middle"})
                    if len(odds_cells) < 4: continue # Skip if odds data is missing
                    
                    result1 = odds_cells[0].text.strip()
                    if result1 not in ['WON', 'LOST']: continue # Skip draws/no-contests
                    
                    odds_f1 = float(odds_cells[2].text.strip(" @"))
                    odds_f2 = float(odds_cells[3].text.strip(" @"))
                    
                    # Determine favorite and if the favorite won
                    is_f1_favorite = odds_f1 < odds_f2
                    favorite_fighter_num = "f1" if is_f1_favorite else "f2"
                    winner_is_favorite = (winner_name == fighter1_name and is_f1_favorite) or \
                                       (winner_name == fighter2_name and not is_f1_favorite)
                    
                    scraped_fights.append({
                        "Events": event_name,
                        "Location": location_info,
                        "Fighter1": fighter1_name,
                        "Fighter2": fighter2_name,
                        "Winner": winner_name,
                        "fighter1_odds": odds_f1,
                        "fighter2_odds": odds_f2,
                        "Favourite": favorite_fighter_num,
                        "Label": "Favourite" if winner_is_favorite else "Underdog"
                    })
            except requests.RequestException as e:
                print(f"Could not scrape {link}: {e}")
    except requests.RequestException as e:
        print(f"Could not fetch main event page {url}: {e}")
        
    return scraped_fights
if __name__ == "__main__":
    # Run the scraping function and create the DataFrame
    fight_data = scrape_all_fight_data(is_testing=testing)
    
    if fight_data:
        df = pd.DataFrame(fight_data)
        print(f"Successfully scraped {df.shape[0]} fights.")
        if not df.empty:
             print(f"Last fight card was {df.iloc[-1]['Events']} {df.iloc[-1]['Location']}")
             print("\nWin Distribution:")
             print(df["Label"].value_counts(normalize=True))
        
        # Save the DataFrame to a CSV file
        output_filename = 'test.csv' if testing else 'data.csv'
        df.to_csv(output_filename, index=False)
        print(f"\nData saved to {output_filename}")
    else:
        print("No data was scraped.")
