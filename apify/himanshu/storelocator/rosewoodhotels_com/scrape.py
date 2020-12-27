import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rosewoodhotels_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess =[ ]
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.rosewoodhotels.com"
    r = session.get("https://www.rosewoodhotels.com/en/luxury-hotels-and-resorts",headers=headers)
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
  
    for link in soup.find("div",{"class":"find-all-hotels hotels-list-3 hotels-list-tab-2 hotels-list-mobile-1 aem-GridColumn aem-GridColumn--default--12"}).find("ul").find_all("a"):
        page_url = (link['href'])
        location_request = session.get( link["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        try:
            location_details = list(location_soup.find("span",{"itemprop":"streetAddress"}).stripped_strings)
            addressCountry = location_soup.find("span",{"itemprop":"addressCountry"}).text
            location_name = location_soup.find("span",{"itemprop":"name"}).text
            latitude = location_soup.find("meta",{"itemprop":"latitude"})['content']
            longitude = location_soup.find("meta",{"itemprop":"longitude"})['content']
            street_address = location_details[-1].split(",")[0]
            city = location_details[-1].split(",")[1]
            state = location_details[-1].split(",")[2].replace("Hawaii",'').split()[0]
            if location_details[-1].split(",")[2].replace("Hawaii",'').split()[1:]:
                zipp = location_details[-1].split(",")[2].replace("Hawaii",'').split()[-1]
            else:
                zipp = "V6C 1P7"
            try:
                phone = location_soup.find("span",{"class":"location-phno"}).text
                phone = re.sub(r"\s+", " ", phone)
            except:
                phone= "<MISSING>"

            store = []
            store = [base_url, location_name, street_address, city, state, zipp, addressCountry.replace("USA","US").replace("Canada","CA"),
                        "<MISSING>", phone,  "<MISSING>", latitude, longitude, "<MISSING>", page_url]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            if "https://www.rosewoodhotels.com/en/kona-village"  == store[-1]:
                continue3

            yield store
        except:
            pass

        
    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
