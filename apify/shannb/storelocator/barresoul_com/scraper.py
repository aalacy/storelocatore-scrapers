import requests
from bs4 import BeautifulSoup
import csv
import xlsxwriter
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('barresoul_com')




base_url = 'https://www.barresoul.com'

soup = BeautifulSoup(requests.get(base_url).content, 'html.parser').find(class_="folder")

locations = soup.div.contents

location_urls = []

barre_stores = []

for location in locations:

    if location == '\n':
        continue

    barre_store = {}
    soup = BeautifulSoup(requests.get(base_url+location.a.get("href")).content, 'html.parser')

    address = soup.find_all("h3")[2].strong.get_text().split("<br/>")[0].split(",")

    barre_store["locator_domain"] = base_url+location.a.get("href")
    barre_store["street_address"] = address[0]
    barre_store["state"] = address[1].split(" ")[0]
    barre_store["zip_code"] = address[1].split(" ")[1]

    logger.info(barre_store)
    barre_stores.append(barre_store)

    

