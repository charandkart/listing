import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from .marketplace import amazon_data_scrap, flipkart_scrap_data, jiostore_scrap_data

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def save_web_pages(file_name):
    df = pd.read_csv(file_name)
    df['marketplace'] = df['Item Link'].apply(lambda x: x.replace("https://", "").split("/")[0])
    items = df.to_dict('records')
    for link in df['Item Link']:
        print(link)

    import os
    file = file_name.split("\\")[-1]
    directory = f"data/{file}"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Scraping and saving HTML data for each URL
    for i, item in enumerate(items, 1):
        if item['marketplace'] in ['www.amazon.in', 'jmd-asp2.jiostore.online']:
            # Configure Chrome options for headless mode
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run Chrome in headless mode
            chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration

            # Create a new Chrome browser instance
            driver = webdriver.Chrome(options=chrome_options)

            driver.get(item['Item Link'])

            # Wait for the page to fully load
            time.sleep(5)  # Wait for 5 seconds (adjust as needed)

            # Retrieve the HTML content
            html_content = driver.page_source

            soup = BeautifulSoup(html_content, 'html.parser')

            # Close the browser
            driver.quit()
        else:
            headers = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

            response = requests.get(item['Item Link'], headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
        #     html_data = soup.prettify(indent=None)
        
        # Save HTML data to a file
        filename = f"{directory}/html_data_{item['marketplace']}_{item['filename']}.html"

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(str(soup))

        print(f'Item #{i}: Saved HTML data for {item["Item Link"]} to {filename}')

    print("Saving HTML Files Completed")
    return directory

def read_web_pages(folder_path):
    # list to store the processed records
    records = list()

    # Iterate over the files in the folder
    for filename in os.listdir(folder_path):
        
        file_path = os.path.join(folder_path, filename)
        # Check if the file is a regular file
        if os.path.isfile(file_path):
            # Read the HTML data from the file
            with open(file_path, 'r', encoding='utf-8') as file:
                html_data = file.read()
            
            # Create BeautifulSoup object
            soup = BeautifulSoup(html_data, 'html.parser')
            data = {"soup": soup, "market_place": filename.split("_")[2], 'filename': filename}
            
            if (data['market_place'] == 'www.amazon.in'):
                data_ = amazon_data_scrap(data['soup'])
            elif (data['market_place'] == 'www.flipkart.com'):
                data_ = flipkart_scrap_data(data['soup'])
            elif (data['market_place'] == 'jmd-asp2.jiostore.online'):
                data_ = jiostore_scrap_data(data['soup'])
            else:
                print(data['market_place'])
                data_ = {'Product_Title': ''}
            print("Scrapped data for file: ", filename)
            records.append({'market_place': data['market_place'], 'file_name': data['filename'], **data_})

    df = pd.json_normalize(records)
    filename =  folder_path.split("/")[-1]
    if not os.path.exists("/scrapped"):
        os.makedirs("/scrapped")
    df.to_csv(f'scrapped/{filename}', index=False)

    return filename