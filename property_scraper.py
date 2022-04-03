import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import argparse
import pandas
from time import sleep
import sys


titles = ["Price", "Beds", "Full Baths", "Half Baths", "Adress", "Site"]
all_homes = []


def load_homes(zip_code):
    site = f"https://www.century21.com/real-estate/{zip_code}/LZ{zip_code}/?"
    
    options = Options()  
    options.add_argument("--headless")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    try:
        print("Connecting to Century21.com\n")
        sleep(2)
        driver.get(site)
        print("Connection successful\n")
        sleep(2)

    except:
        # connection failed
        print("Connection Failed\n")


    # Need to click on the gallery view buttons so that all the homes show on the web page.
    sleep(2)
    grid_view = driver.find_element(By.ID, "gallery-view-button")
    grid_view.click()
    sleep(1)

    # Scroll to the bottom of the page since the page will only load the homes if you scroll down.
    page_height = driver.execute_script("return document.body.scrollHeight")
    element = driver.find_element(By.TAG_NAME, "body")

    print("Loading homes on page\n")

    while True:
        element.send_keys(Keys.END)

        sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == page_height:
            break
        page_height = new_height

    house_info(driver.page_source)


def house_info(page):
    soup = BeautifulSoup(page, "html.parser")

    results = soup.find_all("div", {"class":"property-card-primary-info"})

    print("Collecting data for homes...\n")
    sleep(2)

    # Collect each home information and save it as a dictionary.
    for items in results:
        home_info = []
        try:
            home_info.append(items.find("a", {"class":"listing-price"}).text.replace("\n","").replace(" ",""))
        except AttributeError:
            home_info.append(None)

        try:
            home_info.append(items.find("div",{"class":"property-beds"}).text.replace("\n", ""))
        except AttributeError:
            home_info.append(None)

        try:
            home_info.append(items.find("div",{"class":"property-baths"}).text.replace("\n", ""))
        except AttributeError:
            home_info.append(None)

        try:
            home_info.append(items.find("div", {"class":"property-half-baths"}).text.replace("\n", ""))
        except AttributeError:
            home_info.append(None)

        try:
            address = items.find("div",{"class":"property-address"}).text.split()
            home_info.extend(
                (
                    ' '.join(address),
                    "https://www.century21.com" + items.find('a').get('href'),
                )
            )

        except AttributeError:
            home_info.append(None)

        all_homes.append(dict(zip(titles, home_info)))

    print("Data collection completed\n")
    sleep(2)
    print(f"{len(all_homes)} homes found\n")
    sleep(2)
    print("Data saved into Output.csv\n")

    # Save the dictionaries to a csv file.
    df = pandas.DataFrame(all_homes)
    df.to_csv('Output.csv') 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_code", help="Zip code of the area you want the homes for sale.")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
    else:
        load_homes(args.zip_code)

if __name__ == "__main__":
    main()


# new package
### webdriver-manager