from selenium.webdriver.support.wait import WebDriverWait
import csv
from sgselenium import SgSelenium
import requests
from bs4 import BeautifulSoup as bs
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    address = []
    driver = SgSelenium().firefox()
    driver.get('https://www.miniustorage.com/all-locations/')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    soup = bs(driver.page_source, "lxml")
    base_url = "https://www.miniustorage.com/"
    data = soup.find("div",class_="pagePlayer").find_all("div",{"class":"locByStateFacility"})
    for q in data:
        page_url = q.find("a",class_=re.compile("up_info_"))['href']
        # print(page_url)
        soup1 = bs(requests.get(page_url,headers=headers).text,'lxml')
        lat=''
        log=''
        try:
            lat = soup1.find("a",{"href":re.compile("https://www.google.com/maps")})['href'].split("@")[1].split(",")[0]
            log= soup1.find("a",{"href":re.compile("https://www.google.com/maps")})['href'].split("@")[1].split(",")[1]
        except:
            lat='<MISSING>'
            log='<MISSING>'
        street_address = soup1.find("span",class_="loc_add1").text.strip().replace(",",'')
        city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip().replace(",",'')
        state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip()
        zipp = soup1.find("span",{"itemprop":"postalCode"}).text.strip()
        phone = soup1.find("div",{"itemprop":"telephone"}).find("a").text.strip()
        location_name = soup1.find("div",class_="locName").text.strip()
        hours_of_operation = " ".join(list(soup1.find("div",{"itemprop":"openingHours"}).stripped_strings))
        # print(phone)
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append( "US")
        store.append("<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append( "<MISSING>")
        store.append(lat if lat else "<MISSING>")
        store.append(log if log else "<MISSING>")
        store.append(hours_of_operation.replace('Office Hours: ','') if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        # print("~~~~~~~~~~~~~~~~~ ",store)
        # if store[2] in addressesss :
        #     continue
        # addressesss.append(store[2])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
