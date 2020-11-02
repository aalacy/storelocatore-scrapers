import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('threebearsalaska_com')





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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }



    base_url = "https://threebearsalaska.com/"
    r = session.get("https://threebearsalaska.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

    # it will used in store data.
    locator_domain = base_url
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
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = ""

    # logger.info("soup ==== " + str(soup))

    for script in soup.find('li', {'id': 'menu-item-5072'}).find_all('a'):
        # list_address = list(script.stripped_strings)
        if script['href'] != '#':
            # logger.info("script ===== " + str(script['href']))
            location_url = script['href']
            r_location = session.get(location_url, headers=headers)
            soup_location = BeautifulSoup(r_location.text, "lxml")

            latitude = soup_location.text.split('"lat":"')[1].split('"')[0]
            longitude = soup_location.text.split('"lng":"')[1].split('"')[0]

            tag_address = soup_location.find(
                lambda tag: (tag.name == "strong" or tag.name == "h2") and "Physical Address" in tag.text)
            if tag_address is None:
                tag_address = soup_location.find(lambda tag: (
                                                                     tag.name == "strong" or tag.name == "h2") and "Physical and Mailing Address" in tag.text)
            list_address = list(tag_address.parent.stripped_strings)
            if len(list_address) > 5:
                list_address = list(tag_address.nextSibling.nextSibling.stripped_strings)

            tag_hours = soup_location.find(
                lambda tag: (tag.name == "strong" or tag.name == "h2") and "Hours Of Operation" == tag.text.strip())
            if tag_hours is None:
                tag_hours = soup_location.find(
                    lambda tag: (tag.name == "strong" or tag.name == "h2") and "Store Hours:" == tag.text.strip())
            if tag_hours is None:
                tag_hours = soup_location.find(
                    lambda tag: (tag.name == "strong" or tag.name == "h2") and "Main Store:" == tag.text.strip())

            list_hours = list(tag_hours.parent.stripped_strings)
            if len(list_hours) > 5:
                list_hours = list(tag_hours.nextSibling.nextSibling.stripped_strings)

            tag_phone = soup_location.find(
                lambda tag: (tag.name == "strong" or tag.name == "h2") and "Telephone:" == tag.text.strip())

            if tag_phone is None:
                tag_phone = soup_location.find(lambda tag: (tag.name == "p") and "Telephone:" in tag.text.strip())

            if len(tag_phone.nextSibling.strip()) == 0:
                phone = tag_phone.text.split("Fax:")[0].replace("Telephone:", "").strip()
            else:
                phone = str(tag_phone.nextSibling).strip()

            if len(list_address) > 2:
                full_address = ",".join(list_address[-2:])
            else:
                full_address = ",".join(list_address)

            # logger.info("list_address ==== " + str(full_address))

            if not full_address.find('https://') >= 0:
                if len(full_address.split(',')[-1].strip().split(' ')) > 1:
                    street_address = ','.join(full_address.split(',')[:-2])
                    city = full_address.split(',')[-2]
                    if len(street_address) == 0:
                        street_address = full_address.split(',')[0]
                        city = '<MISSING>'

                    state = full_address.split(',')[-1].strip().split(' ')[0]
                    zipp = full_address.split(',')[-1].strip().split(' ')[1][-5:]
                else:
                    street_address = ','.join(full_address.split(',')[:-3])
                    city = full_address.split(',')[-3]
                    if str(full_address.split(',')[-1])[-5:].isdigit():
                        zipp = full_address.split(',')[-1][-5:]
                        state = full_address.split(',')[-2]
                    else:
                        zipp = full_address.split(',')[-2][-5:]
                        state = full_address.split(',')[-1]
            else:
                street_address = "<MISSING>"
                city = "<MISSING>"
                zipp = "<MISSING>"
                state = "<MISSING>"

            if len(location_name) == 0:
                location_name = city

            hours_of_operation = " ".join(list_hours)

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,location_url]

            store = ["<MISSING>" if x == "" else x for x in store]
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
