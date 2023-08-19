# Standard Libraries
import os
import csv
from datetime import datetime
import re
import requests
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# External Libraries
from bs4 import BeautifulSoup
import pandas as pd

# Set the current date for use in the filename
current_date = datetime.now()
formatted_date = current_date.strftime('%m-%d-%y')

# Access Environmental Variables
file_main_stock_csv=os.getenv('file_main_stock_csv') # This is .csv of the Nasdaq sorted by market cap
output_dir = os.getenv('output_directory')

# Replace this section with your own list of stocks 
stock_tickers = os.environ.get('stock_tickers_string', '')
if stock_tickers:
    stock_tickers = stock_tickers.split(',')
    print(stock_tickers)
else:
    print("No stock tickers found in the environment variable.")

# Create the output file name
filename = "_stock_list_12_mo_EPS_history.csv"
csv_filename = output_dir + formatted_date + filename
csv_columns = ["Ticker Symbol", "12 Month EPS Date", "EPS Value"]


# Create a dictionary to store the results
eps_results = {}

def twelve_month_eps_diluted_scraper(ticker_symbol):
    #ticker_symbol = "HD"
    #stock_name2 = "home-depot"

    # Open up spreadsheet and convert it into a pandas dataframe
    df = pd.read_csv(file_main_stock_csv)

    # Search for the row in the Symbol column that matches the ticker symbol, then find the value in the name column
    stock_name = df.loc[df['Symbol'] == ticker_symbol, 'Name'].values[0]
    #print(stock_name)

    # Clean up the name of the stock of various iterations
    stock_name2 = stock_name.replace('Inc.','').replace('plc.','').replace('Ordinary Shares','').replace('and','').replace('Incorporated','').replace('(new)','').replace('Communications','').replace('(DE)','').replace('Company','').replace('Co.','').replace('Incorporated', '').replace('Corporation','').replace('Common Stock','').replace('.com','').replace('Class A', '').replace('Class C', '').replace('Capital Stock','').replace('&', '').replace('(The)', '')

    # How to generate the URL: EPS
    url_part1 = "https://www.macrotrends.net/stocks/charts/"
    url_part2 = "/"
    url_part3 = "/eps-earnings-per-share-diluted"

    modified_url1 = url_part1 + ticker_symbol + url_part2
    modified_url2 = modified_url1 + stock_name2 + url_part3

    print(modified_url2)

    url = modified_url2


    # Set the header agent so the website thinks we're accessing the website through a browser not a bot
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

    # Doing an HTML request and storing the contents of the HTML into Beautiful Soup
    html_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(html_page.content, 'lxml')

    # Scrape the name of the stock and page title
    header_info = soup.find_all("div", id="main_content_container")[0]
    stock_title = soup.find_all("h2")[0]

    # Scrape the 1st paragraph and the unordered list
    list_contents = []

    bullets = soup.find_all('li')
    for bullet in bullets:
        bullet = str(bullet.text)
        list_contents.append(bullet)
        #print(bullet.text)

    # Print the contents of the 16th element of the list
    print(list_contents[16])

    # Store the 12 month EPS in a variable
    second_bullet = list_contents[16]
    #print(second_bullet)

    # Parse the text to extract the date
    pre_date = "ending"
    post_date = "was"
    s=str(re.escape(pre_date))
    e=str(re.escape(post_date))
    date_string = re.findall(s+"(.*)"+e,second_bullet)[0]
    #print("Dirty Date: " + date_string)

    # Trim the empty space at the beginning and end of the date and remove the ','
    date_trimmed = date_string.lstrip()
    date_trimmed = date_trimmed.rstrip()
    date_cleaned = re.sub(",","",date_trimmed)
    #print("Cleaned date: ", date_cleaned)
    #print("Count letters in cleaned date: ", len(date_cleaned))

    # Convert the date from string into date time object
    datetime_converted = datetime.strptime(date_cleaned, '%B %d %Y')
    #print(type(datetime_converted))
    #print(datetime_converted)

    # Drop the hour, minutes, and seconds
    datetime_cleaned = datetime_converted.date()
    print(datetime_cleaned)

    # Re-order the date
    date_time_final = datetime_cleaned.strftime("%m/%d/%y")
    print("12 Mo EPS Date: ", date_time_final)


    # Parse the text to extract the EPS
    pre_eps = "was"
    post_eps = ","
    s=str(re.escape(pre_eps))
    e=str(re.escape(post_eps))
    eps_string =re.findall(s+"(.*)"+e,second_bullet)[0]
    print("12 Mo EPS Price (as string): ", eps_string)

    # Drop the $ and then convert the string into a float
    eps_float = float(eps_string.replace("$", ""))
    print("12 Mo EPS Price (as float): ", eps_float)

    return date_time_final, eps_float


# Iterate through each stock ticker
for ticker in stock_tickers:
    try:
        # Call your function and store the result in the dictionary
        eps_date, eps_value = twelve_month_eps_diluted_scraper(ticker)
        eps_results[ticker] = (eps_date, eps_value)
    except Exception as e:
        error_message = f"Error processing {ticker}: {e}"
        print(error_message)
        eps_results[ticker] = (error_message, "")  # Store error message in the dictionary

# Print the collected EPS results along with the 12-month EPS date
for ticker, (eps_date, eps_value) in eps_results.items():
    try:
        print(f"{ticker}: 12-Month EPS Date: {eps_date}, EPS Value: {eps_value}")
    except Exception as e:
        print(f"Error processing {ticker}: {e}")

# Write the collected EPS results to the CSV file
with open(csv_filename, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(csv_columns)  # Write the column headings
    for ticker, (eps_date, eps_value) in eps_results.items():
        try:
            writer.writerow([ticker, eps_date, eps_value])
        except Exception as e:
            print(f"Error writing data for {ticker}: {e}")

print("CSV file created successfully.")