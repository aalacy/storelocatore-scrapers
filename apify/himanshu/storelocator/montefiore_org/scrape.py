import csv
import time
import requests
from bs4 import BeautifulSoup
import re
import json
 

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = requests.post(url,headers=headers,data=data)
                else:
                    r = requests.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    base_url = "https://www.montefiore.org"
    addresses = []

    r = request_wrapper("https://www.montefiore.org/utilities/getdoctor_AJAX.cfm","post", headers=headers,
                        data="bolReturnJSONData=false&nMaxRowsPerPage=1000000")
    soup = BeautifulSoup(r.text, "lxml")

    for location_detail in soup.find_all("div", {"itemtype":"http://schema.org/Physician"}):

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        page_url = ""
        location_name = location_detail.find("h2",{"itemprop":"name"}).text
        if location_detail.find("div",{"itemprop":"location"}) and location_detail.find("div",{"itemprop":"streetAddress"}):
            street_address = location_detail.find("div",{"itemprop":"streetAddress"}).text
            street = "s"
            if location_detail.find("div",{"itemprop":"name"}):
                street = location_detail.find("div",{"itemprop":"name"}).text
            if street[0].isdigit():
                street_address = street+" "+street_address
            if "Suite" in street_address:
                street_address = "".join(street_address[:street_address.index("Suite")])
            if "suite" in street_address:
                street_address = "".join(street_address[:street_address.index("suite")])
            if "Floor" in street_address:
                street_address = "".join(street_address[:street_address.index("Floor")])
            if "floor" in street_address:
                street_address = "".join(street_address[:street_address.index("floor")])
            street_address=street_address.split(',')[0]
            
            if hasNumbers(street_address)==False:
                continue;
            if location_detail.find("span",{"itemprop":"addressLocality"}):
                city = location_detail.find("span",{"itemprop":"addressLocality"}).text
            if location_detail.find("span",{"itemprop":"addressRegion"}):
                state = location_detail.find("span",{"itemprop":"addressRegion"}).text
            if location_detail.find("span",{"itemprop":"postalCode"}):
                zipp = location_detail.find("span",{"itemprop":"postalCode"}).text
            if location_detail.find("span",{"itemprop":"telephone"}):
                phone = location_detail.find("span",{"itemprop":"telephone"}).text
            if location_detail.find("a",{"itemprop":"url"}):
                page_url = base_url+"/body.cfm"+location_detail.find("a",{"itemprop":"url"})["href"]

            # print("page_url : ",page_url)

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[2]) not in addresses and store[2] and country_code:
                addresses.append(str(store[2]))

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                #print("data = " + str(store))
                #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
