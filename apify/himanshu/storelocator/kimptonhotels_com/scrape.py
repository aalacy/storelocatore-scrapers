import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
import time



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.ihg.com/kimptonhotels/content/us/en/stay/find-a-hotel#location=all"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for data in soup.findAll('div', {'class', 'hotel-tile-info-wrapper'}):
        data_url = "https:" + data.find('a').get('href')
        page_url = data_url
        detail_url = session.get(data_url, headers=headers)
        detail_soup = BeautifulSoup(detail_url.text, "lxml")
        latitude = detail_soup.find('input',{'id':'latitude'})['value']
        longitude = detail_soup.find('input',{'id':'longitude'})['value']
        detail_block = detail_soup.select('.brand-logo .visible-content')
        if detail_block:
            for br in detail_soup.select('.brand-logo .visible-content')[0].find_all("br"):
                br.replace_with(",")

            address = detail_soup.select('.brand-logo .visible-content')[0].get_text().strip().split(',')
            if "United States" in address[-1] or "Canada" in address[-1]:
                # print(address)

                location_name = detail_soup.select('.name')[0].get_text().strip()
                phone = detail_soup.select('.phone-number')[0].get_text().strip()[8:]
                street_address = ' '.join(address[:-2]).strip()
                # print(address[-2].split(" "))
                # print(len(address[-2].split(" ")))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~`')
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(" ".join(address[-2].split(" "))))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(address[-2].split(" "))))
                if us_zip_list:
                    zip = us_zip_list[0].strip()
                    country_code = "US"
                    city = " ".join(address[-2].split(" ")[:-2]).strip()
                    state =address[-2].split(" ")[-2].strip()


                elif ca_zip_list:
                    zip = ca_zip_list[0].strip()
                    country_code = "CA"
                    city = "".join(address[-2].split(" ")[0]).strip()
                    state =address[-2].split(" ")[1].strip()
                    # print(city +" | "+state+" | "+zip)


            else:
                # print(address[-1])
                continue
            store = []
            store.append("https://www.kimptonhotels.com/")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append(page_url)
            #print("data === "+str(store))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
            return_main_object.append(store)
        else:
            pass
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
