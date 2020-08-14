import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8",newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addressess = []

    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.budgettruck.com/"
    r = session.get("https://www.budgettruck.ca/en/locations/ca",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")

    for li in soup.find("div",{"class":"country-wrapper row"}).find("ul").find_all("li"):
        state_link = "https://www.budgettruck.ca" + li.find("a")['href']
        state_request = session.get(state_link)
        state_soup = BeautifulSoup(state_request.text,"lxml")
        for c in state_soup.find("div",{"class":"location-state kansas-section"}).find_all("div",{"class":"col-sm-12 col-xs-12 border-bottom padd-top0 padd-right0"}):
            city_link = "https://www.budgettruck.ca" + c.find("a")['href']
           # print(city_link)
            city_request = session.get(city_link)
            city_soup = BeautifulSoup(city_request.text,"lxml")
            # script = city_soup.find(lambda tag: (tag.name == "script") and 'stringyStations' in tag.text)
            if "var stringyStations = '" in str(city_soup):
                script = str(city_soup).split("var stringyStations = '")[1].split("';")[0]
                json_data = json.loads(script)
            else:
                continue

            
            for dealer in json_data:
                locator_domain = base_url
                location_name = dealer['description']
                street_address = dealer['address1']
                city = dealer['city']
                state = dealer['stateCode']
                zipp = dealer['zipCode']
                country_code = dealer['countyCode']
                store_number = dealer['locationCode']
                phone = dealer['phoneNumber']
                location_type = dealer['licInd']
                latitude = dealer['latitude']
                longitude = dealer['longitude']
                hours_of_operation = dealer['hoursOfOperation']
                for page in city_soup.find_all("div",{"class":"locTitl"}):
                    if store_number.lower() in page.find("a")['ng-href'].split("/")[-1]:
                        page_url = "https://www.budgettruck.ca" + page.find("a")['ng-href']

                
                store = []
                store.append(locator_domain)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)   
                store.append(country_code)
                store.append('<MISSING>)
                store.append(phone)
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append(page_url)
            

                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                yield store



def scrape():
    data = fetch_data()
    write_output(data)
scrape()
