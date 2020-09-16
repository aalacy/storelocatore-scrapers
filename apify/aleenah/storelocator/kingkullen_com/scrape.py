import csv
from bs4 import BeautifulSoup
import re
import requests
import time
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)



all=[]
driver = SgSelenium().chrome()

def fetch_data():
    # Your scraper here

    headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'en-US,en;q=0.9,ms;q=0.8,ur;q=0.7,lb;q=0.6',
'Cache-Control': 'max-age=0',
'Connection': 'keep-alive',
'Content-Length': '106',
'Content-Type': 'application/x-www-form-urlencoded',
'Host': 'kingkullen.mywebgrocer.com',
'Origin': 'http://kingkullen.mywebgrocer.com',
'Referer': 'http://kingkullen.mywebgrocer.com/StoreLocator.aspx?s=740687418&g=7cc97cbf-b282-4718-810b-cdc95ab74d82&uc=370A037',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
'Cookie': 'SA_SIDSRC=154=1; UMA_SIDGUID=s=740687418&g=7cc97cbf-b282-4718-810b-cdc95ab74d82; TS0111b575=01391bcd08dba9000278fe5190d83cb0363562ecec84d654b841ca923f8d9145f8d61fdf0737c6214f402176927004db3605b3a2d3fccb3420c9eae67a4a8f1a11d17a29bd8c047ab4d0f79c85ed73477d96ce6f8b; _ga=GA1.2.1018485784.1598557924; _gid=GA1.2.447398689.1598557924; TS01ae7bf1=01391bcd0879cababf4c6076a58393dd9157d28b85cae1127239898f6a7d9e8b7ff3c0d009d4bb3b5b30352d7f725f938bb25ee2aa; _dc_gtm_UA-5496062-8=1; _dc_gtm_UA-3893611-1=1; _dc_gtm_UA-56824083-4=1; _gali=LocationsSeachInnerCell'}

    driver.get('http://kingkullen.mywebgrocer.com/StoreLocator.aspx?')
    time.sleep(3)
    url=driver.current_url

    print(url)
    res = requests.post(url,headers=headers,data='postBack=1&action=GL&stateSelIndex=1&citySelIndex=0&selStates=NY&selCities=&txtZipCode=&selZipCodeRadius=5')
    print(res)

    soup = BeautifulSoup(res.text, 'html.parser')
    #soup = BeautifulSoup(driver.page_source, 'html.parser')
    stores = soup.find('table', {'id': 'LocatorResultsTbl'}).find_all('div', {'class': 'StoreBox'})

    print(len(stores))
    for store in stores:

        ps=store.find('div', {'class': 'StoreAddress'}).find_all('p', {'class': 'tInfo'})
        street=ps[0].text
        p=ps[1].text.split(',')
        city=p[0]
        p=p[1].strip().split(' ')
        state=p[0]
        zip=p[1]
        coord=store.find('div', {'class': 'StoreAddress'}).find('a').get('href')
        lat,long=re.findall(r'll=(-?[\d\.]+),(-?[\d\.]+)',coord)[0]


        all.append([

            "https://tcmarkets.com",
            store.find('p', {'class': 'StoreTitle'}).text,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            store.find('div', {'class': 'StoreContact'}).find('p', {'class': 'tInfo'}).text,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            store.find('div', {'class': 'StoreHours'}).find('p', {'class': 'tInfo'}).text,  # timing
            "http://kingkullen.mywebgrocer.com/StoreLocator.aspx?s=740687418&g=7cc97cbf-b282-4718-810b-cdc95ab74d82&uc=370A037"])



    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
