import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
from random import choice
import usaddress

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",'page_url'])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    return_main_object = []
    base_url = "https://www.cityblueshop.com/pages/locations"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    r = session.get(base_url,headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("div", {"class": "rte-content colored-links"}):
        for semi_parts in parts.find_all("h3"):
            siblings = list(semi_parts.find_next_sibling().stripped_strings)
            top_level_address = ', '.join(siblings)
            tagged = usaddress.tag(top_level_address)[0]
            if 'StateName' not in tagged:
                continue
            state = tagged['StateName']
            city = tagged['PlaceName']
            street_address = top_level_address.split(city)[0].strip(',( ')
            if street_address.lower().endswith("shopping center"):
                street_address = street_address.rsplit(',', 1)[0].strip()
            zipcode = tagged['ZipCode']
            phone1 =''
            store_request = session.get(semi_parts.find("a")['href'])
            store_soup = BeautifulSoup(store_request.text, "lxml")
            page_url = semi_parts.find("a")['href']
            for inner_parts in store_soup.find_all("div", {"class": "rte-content colored-links"}):
                longitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[0]
                latitude = inner_parts.find("iframe")['src'].split("!2d")[-1].split("!3d")[-1].split("!2m")[0].split("!3m")[0]
                temp_storeaddresss = list(inner_parts.stripped_strings)
                location_name = semi_parts.text
                if len(temp_storeaddresss) ==7:
                    phone1 = temp_storeaddresss[2].replace("Ph: ","")
                    hours = " ".join(temp_storeaddresss[-4:])
                elif len(temp_storeaddresss) ==4:
                    phone1 = temp_storeaddresss[-3]
                    hours = " ".join(temp_storeaddresss[-2:])
                elif len(temp_storeaddresss) ==5:
                    hours = " ".join(temp_storeaddresss[-2:])
                    if "Mon" in temp_storeaddresss[-2]:
                        hours = " ".join(temp_storeaddresss[-2:])
                    if "Mon" in temp_storeaddresss[-3]:
                        hours = " ".join(temp_storeaddresss[-3:])
                    phone_list = re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(temp_storeaddresss))
                    if phone_list:
                        phone1 = phone_list[-1]
                    temp_storeaddresss.remove(phone1)
                    new = temp_storeaddresss[:-2]
                    if "Mon" in new[-1]:
                        del new[-1]
            return_object =[]
            return_object.append("https://www.cityblueshop.com")
            return_object.append(location_name.strip() if location_name else "<MISSING>")
            return_object.append(street_address.strip() if street_address else "<MISSING>")
            return_object.append(city.strip() if city else "<MISSING>")
            return_object.append(state.strip() if state  else "<MISSING>")
            return_object.append(zipcode if zipcode else "<MISSING>")
            return_object.append("US")
            return_object.append("<MISSING>")
            return_object.append(str(phone1).strip().replace("Ph:","") if phone1 else "<MISSING>")
            return_object.append("<MISSING>")
            return_object.append(latitude if latitude else "<MISSING>")
            return_object.append(longitude if longitude else "<MISSING>")
            return_object.append(hours.strip() if hours else "<MISSING>")
            return_object.append(page_url)
            if return_object[2] in addresses:
                continue
            addresses.append(return_object[2])
            yield return_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()


