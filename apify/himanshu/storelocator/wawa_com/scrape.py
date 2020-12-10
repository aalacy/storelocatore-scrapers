import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from random import choice
import re
import json
import ssl
import urllib3
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('wawa_com')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url", ])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    urllib3.disable_warnings()
    base_url = "https://www.wawa.com"
    
    sess = requests.session()
    base_response = sess.get(base_url)
    response = sess.get("https://www.wawa.com/site-map")
    logger.info(sess.cookies.get_dict())
    cookies_json = sess.cookies.get_dict()
    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(",", ";")
    # headers = {
    # 'User-Agent': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    # 'Cookie': cookies_string,
    # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    # }
    # headers = {
    headers  = {
    'Host':'www.wawa.com',
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv':'78.0) Gecko/20100101 Firefox/78.0",
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'en-US,en;q=0.5',
    'Accept-Encoding':'gzip, deflate, br',
    'DNT':'1',
    'Connection':'keep-alive',
    'Upgrade-Insecure-Requests':'1'}
    
    r = session.get("https://www.wawa.com/site-map", headers=headers)
    
    soup = BeautifulSoup(r.text,"lxml")
    addresses = []
    for link in soup.find_all("ul",{"class":"CMSSiteMapList"})[-1].find_all("a",{"class":"CMSSiteMapLink"}):
        locator_domain = base_url
        store_number = link['href'].split("/")[2]
        page_url = base_url + link['href']
        r = session.get(page_url, headers = headers)
        cookies_json = session.cookies.get_dict()
        cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(",", ";")
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Content-Type': 'application/json',
        'Cookie': cookies_string,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' 
        }
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        location_name = soup.find("span",{"itemprop":"name"}).text.strip()
        try:
            street_address = soup.find("span",{"itemprop":"streetAddress"}).text.strip()
        except:
            street_address ="<MISSING>"
        try:
            city = soup.find("span",{"itemprop":"addressLocality"}).text.strip()
        except:
            city:"<MISSING>"
        try:
            state = soup.find("span",{"itemprop":"addressRegion"}).text.strip()
        except:
            state= "<MISSING>"
        try:
            zipp = soup.find("span",{"itemprop":"postalCode"}).text.strip()
        except:
            zipp = "<MISSING>"
        try:
            phone = soup.find("span",{"itemprop":"telephone"}).text.replace("Phone Number:","").strip()
        except:
            phone = "<MISSING>"
        try:
            hours_of_operation = soup.find("meta",{"itemprop":"openinghours"})["content"]
        except:
            hours_of_operation = "<MISSING>"
        country_code="US"
        try:
            latitude = soup.find("meta",{"itemprop":"latitude"})["content"]
            longitue = soup.find("meta",{"itemprop":"longitude"})["content"]
        except:
            latitude="<MISSING>"
            longitue= "<MISSING>"
        location_type = "<MISSING>"
        store_number= location_name.split("#")[-1].strip()
        store = [locator_domain, location_name.strip(), street_address.strip(), city.strip(), state.strip(), zipp.strip(), country_code,
                        store_number, phone.strip(), location_type, latitude, longitue, hours_of_operation.replace("Hours:", "").strip(), page_url]

        if str(store[2]) + str(store[-1]) not in addresses:
            addresses.append(str(store[2]) + str(store[-1]))
            store = [x if x else "<MISSING>" for x in store]
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
