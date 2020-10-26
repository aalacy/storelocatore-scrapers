import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import json
# import sgzip
# import time



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.sparklemarkets.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "sparklemarkets"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"



    r= session.get('https://www.sparklemarkets.com/locations',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')

    for i  in soup.find_all(class_="bDfMI"):
        if i.a['href'].split('/')[-1]:
            page_url = locator_domain + i.a['href'][2:]
            r_soup = session.get(page_url,headers = headers)
            soup_loc = BeautifulSoup(r_soup.text,'lxml')
            # print(page_url)
            location_name = soup_loc.h1.text.encode('ascii', 'ignore').decode('ascii').strip().capitalize()

            adds = soup_loc.find_all('p',class_='font_7')
            for add in adds:
                if "Address:" in add.text:
                    break
            phone= add.find(lambda tag: (tag.name == "span") and "Phone:" in tag.text).nextSibling.encode('ascii', 'ignore').decode('ascii').strip()
            hours_of_operation = add.find(lambda tag: (tag.name == "span") and "Hours:" in tag.text).nextSibling.replace('\xa0','').replace('|','')
            if "(" in hours_of_operation:
                hours_of_operation = hours_of_operation[:hours_of_operation.find("(")].strip()
            span = add.find(lambda tag: (tag.name == "span") and "Address:" in tag.text).nextSibling
            address = span.split(',')
            if len(address) == 2:

                street_address = " ".join(address[0].split()[:-1]).encode('ascii', 'ignore').decode('ascii').strip()
                city = "".join(address[0].split()[-1].encode('ascii', 'ignore').decode('ascii').strip())
                state = address[-1].split()[0].encode('ascii', 'ignore').decode('ascii').strip()
                zipp= address[-1].split()[-1].encode('ascii', 'ignore').decode('ascii').strip()

            else:
                street_address = " ".join(address[:-2]).encode('ascii', 'ignore').decode('ascii').strip()
                city = address[-2].encode('ascii', 'ignore').decode('ascii').strip()
                state = address[-1].split()[0].encode('ascii', 'ignore').decode('ascii').strip()
                zipp = address[-1].split()[-1].encode('ascii', 'ignore').decode('ascii').strip()
                # print(city)
        else:
            page_url = i.a['href']
            # print(page_url)
            add = i
            location_name = add.h4.text.strip()
            # print(location_name)
            address = add.find_all(class_="_1Z_nJ")[-1]
            list_address= list(address.stripped_strings)
            street_address = list_address[0]
            city = list_address[1].split(',')[0]
            state = list_address[1].split(',')[1].split()[0]
            zipp = list_address[1].split(',')[1].split()[-1]
            phone = list_address[-1]
            hours_of_operation = "<MISSING>"


        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" else x for x in store]

        # print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
