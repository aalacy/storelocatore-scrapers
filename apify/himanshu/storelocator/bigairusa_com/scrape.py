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
    base_url = "https://www.bigairusa.com"
    locator_domain = "https://www.bigairusa.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"

    r= session.get('https://www.bigairusa.com',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    for link in soup.find('div',class_='post-content').findAll('li'):
        try:
            link = link.a['href']
            loc_r= session.get(link,headers = headers)
        except:
            continue
        print(link)
        soup_loc= BeautifulSoup(loc_r.text,'lxml')

        location_name = soup_loc.title.text.replace("Home |","").replace("Home -","").split("|")[0].strip()

        address = soup_loc.find(class_="address").text
        street_city = address.split(',')[0].replace(".","").strip()
        if "|" in street_city:
            street_address = street_city.split("|")[0].strip()
            city = street_city.split("|")[-1].strip()
        else:
            street_address = " ".join(street_city.split()[:-1]).strip()
            city = street_city.split()[-1].strip()

        state = address.split(',')[-1][:3].strip()

        try:
            zipp = re.findall(r'[0-9]{5}', address)[0]
        except:
            zipp = "<MISSING>"

        if city == "Carlota":
            street_address = street_city
            city = "Laguna Hills"
            state = "CA"
            zipp = "<MISSING>"

        try:
            phone = soup_loc.find(class_="phone").text.replace("Phone:","").strip()
        except:
            info = soup_loc.find(class_="fusion-contact-info").text
            phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(info))[0]

        if "•" in phone:
            phone = phone.split("•")[-1].strip()

        hour_link = link + "hours/"
        loc_h = session.get(hour_link,headers = headers)
        soup_h = BeautifulSoup(loc_h.text,'lxml')
        hours_of_operation = ""
        raw_hours = soup_h.find('div',class_='fusion-text').find('ul')
        try:
            hours = list(raw_hours.stripped_strings)
            for hour in hours:
                if "day" in hour.lower() or "pm" in hour.lower() and "night" not in hour.lower():
                    hours_of_operation = (hours_of_operation + " " + hour.replace("\xa0","").replace("–","-").replace("SUMMER HOURS","").replace("|","")).strip()
        except:
            hours_of_operation = "<MISSING>"

        hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,link]
        store = ["<MISSING>" if x == "" or x == None  else x for x in store]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
