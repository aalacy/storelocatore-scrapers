import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import datetime
from datetime import datetime
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "raw_address", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "https://www.spar.co.uk"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    result_coords = []
    r = session.get("https://www.spar.co.uk/sitemap-page",headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all("a"):
        if "/store-locator/" in link['href']:
            page_url = base_url + link['href']
            r1 = session.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            if soup1.find("span",{"class":"page__notice-title"}):
                continue
            addr = json.loads(soup1.find(lambda tag : (tag.name == "script") and "latitude" in tag.text).text)
            location_name = addr['name']
            try:
                street_address = addr['address']['streetAddress']
            except:
                street_address = "<MISSING>"
            try:
                city = addr['address']['addressLocality']
            except:
                city = "<MISSINIG>"
            try:
                state = addr['address']['addressRegion']
            except:
                state = "<MISSNG>"
            try:
                zipp = addr['address']['postalCode']
            except:
                zipp = "<MISSING>"
            try:
                phone = addr['telephone']
            except:
                phone = "<MISSING>"
            location_type = addr['@type']

            time = " ".join(list(soup1.find("table",{"class":"table"}).find("tbody").stripped_strings))
            if "24h" in time:
                hours = time
            elif "CLOSED" in time:
                hours = time
            else:
                data = re.findall(r'\d{1,3}:\d{1,3}\s+\d{1,3}:\d{1,3}',time)
                hours = ''
                day = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                for hour in range(len(data)):
                    start_time = datetime.strptime(data[hour].split(" ")[0],"%H:%M").strftime("%I:%M:%p")
                    end_time = datetime.strptime(data[hour].split(" ")[-1],"%H:%M").strftime("%I:%M:%p")
                    hours+= day[hour] +" "+ str(start_time) +" "+ str(end_time) +" "
                hours = hours
            coord = soup1.find(lambda tag : (tag.name == "script") and "storeLat" in tag.text).text
            latitude = coord.split('storeLat = "')[1].split('";')[0]
            longitude = coord.split('storeLng = "')[1].split('";')[0]
            if latitude == "0":
                latitude = "<MISSING>"
            if longitude == "0":
                longitude = "<MISSING>"
            store_number = coord.split('storeId = ')[1].split(";")[0]  
            store = []
            result_coords.append((latitude,longitude))
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp if zipp else "<MISSING>")   
            store.append("UK")
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
