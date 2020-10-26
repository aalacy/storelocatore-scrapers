import csv
from bs4 import BeautifulSoup
import re
import json
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('t-grill_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_url = "https://t-grill.com/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

    location_url = "https://t-grill.com/locations"
    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    box = soup.find("div",{"data-ux":"ContentCards"}).find_all("div",{"data-ux":"ContentCard"})
    for card in box:
        try:
            page_url = card.find("a",{"data-ux":"ContentCardButton"})['href']
            # logger.info(page_url)
            payload_link = page_url.replace("http://","").replace("hrpos.heartland.us","mobilebytes.com")
            id_url = "https://online.hrpos.heartland.us/location"
            payload_id = '{\"domain\":\"'+payload_link+'\",\"action\":\"subdomain_info\"}'
            try:
                location_id = session.post(id_url, headers=headers, data = payload_id).json()['payload']['LocationID']
            except KeyError:
                location_id = "14045"
           

            payload = '{\"domain\":\"'+payload_link+'\",\"locationId\":\"'+str(location_id)+'\",\"jwt\":\"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjYXJ0SWQiOiIzOTZFOEI5Ni0yRjRFLTQ0QzMtQkMxRC04QzQ3N0E5NDA5MDQiLCJsb2NhdGlvbklkIjozMTc1LCJzb3VyY2VJcCI6IjEwNC4xOTQuMjIwLjIwMCIsImV4cCI6MTYwMDg0Njc5NywiaWF0IjoxNjAwODQzMTk3fQ.Z1EgfcCSjD78m78VX2sGZv6VoQd_xEdi_eWL7NkFz4I\",\"env_config\":\"prod\"}'
           
            url = "https://online.hrpos.heartland.us/setup"
            json_data = session.post(url,headers=headers,data=payload).json()['payload']['setupFile']['SetupInfo']
            jd = json.loads(json_data)
            location_name = jd['name']
            street_address = jd['address']['line']
            city = jd['address']['city']
            state = jd['address']['state']
            zipp = jd['address']['zip']
            country_code = jd['address']['country']
            store_number = jd['locationId']
            phone = jd['phone']
            latitude = jd['address']['lat']
            longitude = jd['address']['lon']
            hours_of_operation = "Monday-Saturday : 10:30 AM-8:30 PM, Sunday:Closed"
            page_url = page_url
        except TypeError:
            location_name = "Teriyaki Grill - Ruston"
            street_address = "1913 E. Kentucky Avenue"
            city = "Ruston"
            state = "Louisiana"
            zipp = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            phone = "3182540777"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"
            page_url = "<MISSING>"

        phone = "("+phone[:3]+")"+phone[3:6]+"-"+phone[6:]
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append("Restaurant")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
