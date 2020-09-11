import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    addresses = []
    base_url = "https://www.thompsonhotels.com/"

    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    page_url = ""

    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for div in soup.find("div", class_="artsy-menu-columns clearfix").find_all("ul"):
        # for li in div.find_all("li"):
        #     print(li.prettify)
        #     print("~~~~~~~~~~~")
        for a in div.find_all("a"):
            page_url = a['href']
            # print(page_url)
            r_loc = session.get(page_url, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")

            address = soup_loc.find("section", class_="sec-1")
            loc = address.find("a")
            addr = soup_loc.find_all("address")[-1]
            list_add = list(addr.stripped_strings)

            list_add = [el.replace('\r\n', ',') for el in list_add]
            # print(list_add)
            if soup_loc.find("a",{"href":re.compile("https://www.google.com/maps/")}):
                latitude = soup_loc.find("a",{"href":re.compile("https://www.google.com/maps/")})['href'].split("@")[1].split(",")[0]
                longitude=soup_loc.find("a",{"href":re.compile("https://www.google.com/maps/")})['href'].split("@")[1].split(",")[1].split(",")[0]
                
            if "MX" in " ".join(list_add) or "Mexico" in " ".join(list_add):
                continue
        
            ca_zip_list = re.findall(
                r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(" ".join(list_add)))

            us_zip_list = re.findall(re.compile(
                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(list_add)))
            if us_zip_list:
                zipp = us_zip_list[-1].strip()
                country_code = "US"
            if ca_zip_list:
                zipp = ca_zip_list[-1].strip()
                country_code = "CA"

            if len(list_add) > 1:
                location_name = list_add[0].strip()
                street_address = list_add[1].strip()
                city = list_add[-1].split(',')[0].strip()
                state = list_add[-1].split(',')[-1].split()[0].strip()
            else:
                list_add = " ".join(list_add).split(',')
                location_name = list_add[0].strip()
                street_address = list_add[1].strip()
                city = list_add[2].strip()
                state = list_add[3].split()[0].strip()
            
    
            phone_list = list(soup_loc.find(
                "section", class_="sec-2").stripped_strings)
            if "(MEXICO)" in " ".join(phone_list):
                continue
            phone = phone_list[1].strip()
            if "Thompson" in phone:
                phone="<MISSING>" 
            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"

        # print(zipp, state)

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1]) + str(store[2]) not in addresses:
                addresses.append(str(store[1]) + str(store[2]))

                store = [x.encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
