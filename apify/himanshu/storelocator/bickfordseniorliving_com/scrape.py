import csv
from sgrequests import SgRequests
import json
# from datetime import datetime
# import phonenumbers
from bs4 import BeautifulSoup
import re
# import unicodedata
# import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bickfordseniorliving_com')




session = SgRequests()

def write_output(data):
    with open('data.csv',newline="", mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = "https://www.bickfordseniorliving.com/"
    addresses = []
    country_code = "US"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = session.post("https://www.bickfordseniorliving.com/branch-finder",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    token = soup.find("input",{"name":"_token"})["value"]
    branches_list = ["Illinois","Indiana","Iowa","Kansas","Michigan","Missouri","Nebraska","Ohio","Pennsylvania","Virginia"]
    for state in branches_list:
        data= {
            "searchString": str(state),
            "radius": "90",
            "_token": str(token)
        }
        # logger.info(state)
        r = session.post("https://www.bickfordseniorliving.com/search",data=data,headers=headers).json()
        branch_list = BeautifulSoup(r["branchList"],"lxml")
        marker_data = r["markerData"]
        lat_list=[]
        lng_list = []
        for coord in marker_data:
            lat_list.append(coord["lat"])
            lng_list.append(coord['lon'])
            
        for loc in branch_list.find_all("div",class_="searchBranch"):
            
            full_address = list(loc.find("div",class_="branch_info").stripped_strings)
            location_name = full_address[0]
            street_address = full_address[2]
            city = full_address[3].split(",")[0]
            state = full_address[3].split(",")[1].split()[0]
            zipp = full_address[3].split(",")[1].split()[-1]
            phone = full_address[5]
            location_type = full_address[1]
            store_number = "<MISSING>"
            page_url = "https://www.bickfordseniorliving.com"+loc.find("a",text=re.compile("view branch"))["href"]
            if lat_list:
                latitude =lat_list.pop(0)
            if lng_list:
                longitude = lng_list.pop(0)
            hours_of_operation = "<MISSING>"

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


       


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
