import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
def fetch_data():

    all=[]
    res= session.get("http://mrgas.com/locations/gas-convenience")
    soup = BeautifulSoup(res.text, 'html.parser')
    stores = soup.find_all('a', {'class': 'readon'})

    for store in stores:
        url = "http://mrgas.com"+store.get('href')
        print(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        #print(soup)
        loc = soup.find('h2', {'class': 'itemTitle'}).text.strip()
        data=soup.find_all('span', {'class': 'itemExtraFieldsValue'})
        print(data)
        street=data[1].text.strip()
        addr=data[2].text.strip().split(",")
        city=addr[0]
        addr=addr[1].strip().split(" ")
        state=addr[0]
        zip=addr[1]
        phone=data[3].text
        tim=data[4].text
        if "#" in loc:
            id=loc.split("#")[-1]
        else:
            id="<MISSING>"
        all.append([
            "http://mrgas.com",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            id,  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim.strip(),  # timing
            url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
