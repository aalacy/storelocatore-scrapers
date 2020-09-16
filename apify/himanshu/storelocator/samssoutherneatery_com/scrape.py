import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    addressess = []
    base_url = "http://samssoutherneatery.com"
    r = session.get(
        "https://www.ordersamssoutherneatery.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    # for a in soup.find("main", {"class": "Index"}).find_all("a"):
    for link in soup.find_all(lambda tag: (tag.name == "a") and "Order Now" in tag.text):
        page_url = link['href']
        if "/locations-list" not in page_url:
            # print(page_url)
            # if page_url=="https://www.samssouthernpinebluff.com/#/":
            #     continue
            # if page_url=="https://www.samssouthernwhitehall.com/#/":
            #     continue
            # if page_url == "https://www.samssouthernnatchitoches.com/#/":
            #     continue
            # if page_url == "https://www.samssouthernmarlow.com/#/":
            #     continue
            # if page_url == "https://www.samssoutherntahlequah.com/#/":
            #     continue
            # if page_url == "https://www.samssoutherntahlequah.com/#/":
            #     continue
            r_loc = session.get(page_url, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, 'lxml')
            locator_domain = base_url
            jd = str(soup_loc).split("<script>")[1].split("</script>")[0]
            location_name = jd.split('var _locationName = "')[1].split('";')[0]
            addr = jd.split('var _locationAddress = "')[1].split('";')[0].split(",")
            if len(addr)==4:
                street_address = " ".join(addr[:2]).replace(" Springhill","").strip()
                city = addr[2].strip()
                state = addr[3].strip().split(" ")[0]
                zipp = addr[3].strip().split(" ")[1]
            else:
                street_address = addr[0].lower().strip()
                city = addr[1].lower().strip()
                state = addr[2].strip().split(" ")[0]
                zipp = addr[2].strip().split(" ")[1]

            store_number = jd.split('var _locationId = "')[1].split('";')[0]
            phone = soup_loc.find(lambda tag: (tag.name == "a") and "(" in tag.text).text
            latitude = jd.split('var _locationLat = ')[1].split(';')[0]
            longitude = jd.split('var _locationLng = ')[1].split(';')[0]
            hour_page = page_url+"/Website/Hours"
            hour_r = session.get(hour_page, headers=headers)
            hour_soup = BeautifulSoup(hour_r.text, 'lxml')
            hours_of_operation = " ".join(list(hour_soup.stripped_strings)[1:]).replace("Business Hours","Business Hours :").replace("Carryout Hours",",Carryout Hours :")

            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append('US')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append('<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url)
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
