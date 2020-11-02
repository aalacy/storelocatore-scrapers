import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" , "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url= "https://jimmygs.squarespace.com/our-locations"
    r = session.get(base_url, headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    link = soup.find_all("div", {"class":"sqs-block-content"})
    p = (soup.find("div", {"id":"content"}).find_all("div", {"class":"sqs-block map-block sqs-block-map sized vsize-12"}))
    number = []
    for i in link:
        for h in i.find_all("h3"):
            phone = h.text.split(" ")[-1]
            if len(phone) == 17:
                phone = phone[5:]
            else:
                phone = phone[2:]
            number.append(phone)

    for index,d in enumerate(p):
        latitude = (json.loads(d['data-block-json'])['location']['mapLat'])
        longitude = json.loads(d['data-block-json'])['location']['mapLng']
        street_address = json.loads(d['data-block-json'])['location']['addressLine1']
        location_name = json.loads(d['data-block-json'])['location']['addressTitle']
        state = (json.loads(d['data-block-json'])['location']['addressLine2']).split(",")[1]
        city = (json.loads(d['data-block-json'])['location']['addressLine2']).split(",")[0].replace("loris","Loris")
        if len((json.loads(d['data-block-json'])['location']['addressLine2']).split(",")) == 3:
            zipp = json.loads(d['data-block-json'])['location']['addressLine2'].split(",")[2]
        else:
            zipp = '<MISSING>'
        if "Loris" in city:
            zipp = "29569"
        elif "Brunswick" in city :
            zipp = "28424"
        store = []
        store.append("http://jimmygstores.com/")
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state.upper() if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append('<MISSING>')
        store.append(number[index])
        store.append('<MISSING>')
        store.append(latitude if latitude else '<MISSING>' )
        store.append(longitude if longitude else '<MISSING>')
        store.append('<MISSING>' )
        store.append(base_url)
        yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
