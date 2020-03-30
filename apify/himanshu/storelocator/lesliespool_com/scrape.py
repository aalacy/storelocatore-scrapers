import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
from sgrequests import SgRequests
import phonenumbers


session = SgRequests()

session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

    base_url = "https://www.lesliespool.com"
    r =  session.get("https://www.lesliespool.com/directory/stores.htm", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find("table").find_all("a"):
        
        if link['href'].count("/") > 2:
            page_url = base_url + link['href']
            # print(page_url)
            if "https://www.lesliespool.com/san-antonio-texas/san-antonio-2/stores.htm" in page_url:
                continue

            r1 = session.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            location_name = soup1.find("div",{"class":"name"}).text.strip()
            addr = list(soup1.find("div",{"class":"location"}).stripped_strings)
            street_address = re.sub(r'\s+'," "," ".join(addr[:-1]))
            city = addr[-1].split(",")[0]
            state = addr[-1].split(",")[1].split(" ")[1]
            zipp = addr[-1].split(",")[1].split(" ")[2]
            store_number = location_name.split("#")[-1]
            phone = phonenumbers.format_number(phonenumbers.parse(soup1.find_all("div",{"class":"phone"})[-1].text.replace(".","").strip(), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
            location_type = "<MISSING>"
            coord = soup1.find(lambda tag: (tag.name == "script" and "var stores" in tag.text)).text
            latitude = coord.split("<br />'")[1].split("]")[0].split(",")[3].replace("'","").strip()
            longitude = coord.split("<br />'")[1].split("]")[0].split(",")[4].replace("'","").strip()
            hours_of_operation = " ".join(list(soup1.find("div",{"class":"hours_col"}).stripped_strings))
    
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # print("data===="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            yield store

        # except:
        #     pass
        
       


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
