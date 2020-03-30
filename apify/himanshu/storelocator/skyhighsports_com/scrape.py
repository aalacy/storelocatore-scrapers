import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
import unicodedata


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

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
    base_url = "https://skyhighsports.com/locations/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('div', {'class', 'state'})
    state_dict = {'california': 'CA', 'illinois': 'IL', 'oregon': 'OR', 'tennessee': 'TN'}
    if exists:
        for states in soup.findAll('div', {'class', 'state'}):
            state_name = states.get('class')[1].lower()
            for links in states.find_next('ul').findAll('a'):
                if "http" in links.get('href'):
                    data_url = links.get('href')
                    detail_url = session.get(data_url, headers=headers)
                    detail_soup = BeautifulSoup(detail_url.text, "lxml")
                    if detail_soup.select('#hours'):
                        if detail_soup.select('.phone_number'):
                            phone = detail_soup.select('.phone_number')[0].get_text().strip()
                            state = state_dict[state_name]
                        else:
                            phone = "<MISSING>"
                        if detail_soup.select('.welcome'):
                            location_name = detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0]
                            if "," in detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0]:
                                city = detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0].split(',')[0]
                            elif "/" in detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0]:
                                city = detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0].split('/')[0]
                            else:
                                city = detail_soup.select('.welcome')[0].get_text().strip().split('  ')[0]
                        else:
                            city = "<MISSING>"
                        if detail_soup.select('#hours'):
                            hours_of_operation = detail_soup.select('#hours')[0].get_text().replace("\n\n\n", ' ').replace('\n', ' ').strip()
                        else:
                            hours_of_operation = "<MISSING>"
                        city = city.replace("Sky High Sports ","")
                        address = detail_soup.find("article",{'class':"address"}).find("span").text
                        if len(address.split(",")) > 2:
                            city = address.split(",")[-2]
                        if city in address:
                            street_address = address.split(city)[0]
                        elif "," in address:
                            street_address = " ".join(address.split(",")[0].split(" ")[:-1])
                        else:
                            street_address = " ".join(address.split(" ")[-3])
                        store_zip_split = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),address)
                        if store_zip_split:
                            store_zip = store_zip_split[-1]
                        else:
                            store_zip = "<MISSING>"
                        store = []
                        store.append("https://skyhighsports.com/")                        
                        store.append(location_name)
                        store.append(street_address.replace(",",""))
                        store.append(city.strip())
                        store.append(state)
                        store.append(store_zip)
                        store.append("US")
                        store.append("<MISSING>")
                        store.append(phone.replace("JUMP","").replace("()",""))
                        store.append("<MISSING>")
                        geo_location = detail_soup.find("article",{'class':"address"}).find("a")["href"]
                        store.append(geo_location.split("/@")[1].split(",")[0] if "/@" in geo_location else "<MISSING>")
                        store.append(geo_location.split("/@")[1].split(",")[1] if "/@" in geo_location else "<MISSING>")
                        store.append(hours_of_operation)
                        store.append("<MISSING>")
                        for i in range(len(store)):
                            if type(store[i]) == str:
                                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                        store = [x.replace("–","-") if type(x) == str else x for x in store]
                        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                        return_main_object.append(store)
                    else:
                        pass
                else:
                    pass
        return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
