import requests
import lxml
from bs4 import BeautifulSoup as bs
import csv

## Initialize our lists
storeurls = []
storenames = []
storeaddress = []
storecities = []
storestates = []
storezips = []
storelats = []
storelongs = []
countrycodes = []


## Load up the back door API page that contains all the stores

## May possibly need to add store URL

url = 'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores'
r = requests.get(url)
source = r.text
soup = bs(source, "lxml-xml")

def parsestores():
    stores = soup.find_all("Store")
    for store in stores:
        ## Capture data at each store level

        name = store.find('Name').text
        storenames.append(name)

        address = store.find('Address1').text
        storeaddress.append(address)

        city = store.find('City').text
        storecities.append(city)

        state = store.find('State').text
        storestates.append(state)

        zip = store.find('Zip').text
        storezips.append(zip)

        lat = store.find('Latitude').text
        storelats.append(lat)

        long = store.find('Longitude').text
        storelongs.append(long)

        ## Always append the current URL for this page
        storeurls.append(url)

        ## Always append US as country code
        countrycodes.append('US')
    to_csv()

def to_csv():
    ## If all lists are equal in length, make to_csv

    if len(storenames) == len(storeaddress) == len(storecities) == len(storestates) == len(storezips):

        Columnnames = ["locator_domain","location_name","street_address","city","state","zip","country_code","latitude","longitude"]
        file_name = 'shopnsavefood.csv'

        rows = zip(storeurls,storenames,storeaddress,storecities,storestates,storezips,countrycodes,storelats,storelongs)

        with open(file_name, 'w', encoding='utf-8', newline='') as csvfile:
            links_writer = csv.writer(csvfile)
            links_writer.writerow(Columnnames)
            for item in rows:
                links_writer.writerow(item)
        print("csv file saved")



parsestores()
