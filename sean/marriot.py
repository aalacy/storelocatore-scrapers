import requests
import lxml
from bs4 import BeautifulSoup as bs
import csv

## Initialize our lists
storeurls = []
storeids = []
storenames = []
storeaddress = []
storephonenumbers = []
storecities = []
storestates = []
storezips = []
storecountrycodes = []
storelats = []
storelongs = []


## Load up the back door API page that contains all the stores

## May possibly need to add store URL

url = 'https://www.marriott.com/sitemap.us.hws.1.xml'
r = requests.get(url)
source = r.text
soup = bs(source, "lxml-xml")

def parsestores():
    stores = soup.find_all("loc")

    for store in stores:
        store = store.text
        print(store)
        try:
            store_resp = requests.get(store)
        except:
            time.sleep(10)
            continue
        store_soup = bs(store_resp.text, "lxml")

        address = store_soup.find('address')
        try:
            countrycode = address.find_all('span')[7].text
        except Exception as e:
            countrycode = 'bunk'
            ## This is the case when country code doesn't exist in country address format

        if 'USA' in countrycode or 'CA' in countrycode:

            storeurls.append(store)

            try:
                storename = store_soup.find('span',{'itemprop':'name'}).text
                storenames.append(storename)
            except:
                storenames.append('N/A')

            try:
                streetaddress = address.find_all('span')[1].text
                storeaddress.append(streetaddress)
            except:
                storeaddress.append('N/A')


            try:
                storecity = address.find_all('span')[3].text
                storecities.append(storecity)
            except:
                storecities.append('N/A')

            try:
                storestate = address.find_all('span')[5].text
                storestates.append(storestate)
            except:
                storestates.append('N/A')

            try:
                storezip = address.find_all('span')[6].text
                storezips.append(storezip)
            except:
                storezips.append('N/A')

            try:
                countrycode = address.find_all('span')[7].text
                storecountrycodes.append(countrycode)
            except:
                storecountrycodes.append('N/A')
            try:
                phone = store_soup.find('span',{'itemprop':'telephone'}).text
                storephonenumbers.append(phone)
            except:
                storephonenumbers.append('N/A')


        else:
            ## Not an American or Canadian unit
            continue

    to_csv()

def to_csv():
    ## If all lists are equal in length, make to_csv
    print('We are writing the csv file')

    if len(storenames) == len(storeaddress) == len(storecities) == len(storestates) == len(storezips):

        Columnnames = ["locator_domain","location_name","street_address","city","state","zip","county_code","phone"]
        file_name = 'marriot.csv'

        rows = zip(storeurls,storenames,storeaddress,storecities,storestates,storezips,storecountrycodes,storephonenumbers)

        with open(file_name, 'w', encoding='utf-8', newline='') as csvfile:
            links_writer = csv.writer(csvfile)
            links_writer.writerow(Columnnames)
            for item in rows:
                links_writer.writerow(item)
        print("csv file saved")



parsestores()
