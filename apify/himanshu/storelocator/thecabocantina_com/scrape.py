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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    addresses = []
    base_url = "http://thecabocantina.com"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = ""

    r = session.get("http://cabocantina.com/about/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all('div', class_='elementor-image'):
        page_url = link.a['href']
        location_name = link.a.find("img")["alt"]

        r_loc = session.get(page_url, headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, 'lxml')
        try:
            row = soup_loc.find('div', class_='site-content')
            hours = list(row.find_all(
                'div', class_="elementor-text-editor")[2].stripped_strings)
            hours = [el.replace('\xa0', '') for el in hours]
            if hours != []:
                hours_of_operation = " ".join(
                    hours).strip().replace('Hours:', "").strip()
                hours_of_operation = re.sub(r' +', ' ', hours_of_operation)
                address = list(row.find_all(
                    'div', class_="elementor-text-editor")[1].stripped_strings)
                street_address = address[0].strip()
                city = address[1].split(',')[0].strip()
                state = address[1].split(',')[1].split()[0].strip()
                zipp = address[1].split(',')[1].split()[-1].strip()
                phone = address[-1].strip()
            else:
                hours = list(row.find_all(
                    'div', class_="elementor-text-editor")[1].stripped_strings)
                hours = [el.replace('\xa0', '') for el in hours]
                hours_of_operation = " ".join(
                    hours).strip().replace('Hours:', "").strip()
                hours_of_operation = re.sub(r' +', ' ', hours_of_operation)
                address = list(row.find_all(
                    'div', class_="elementor-text-editor")[0].stripped_strings)
                street_address = address[0].strip()
                city = address[1].split(',')[0].strip()
                state = address[1].split(',')[1].split()[0].strip()
                zipp = address[1].split(',')[1].split()[-1].strip()
                phone = address[-1].strip()
            iframe = soup_loc.find('iframe')['src']
            r_coords = session.get(iframe, headers=headers)
            soup_coord = BeautifulSoup(r_coords.text, 'lxml')
            script = soup_coord.find(lambda tag: (
                tag.name == "script") and "initEmbed" in tag.text)
            sc_string = script.text.split(
                'initEmbed(')[1].split(');')[0].split(',')[55:57]
            # print([list((i, sc_string[i])) for i in range(len(sc_string))])
            latitude = sc_string[0].strip()
            longitude = sc_string[1].replace(']', '').strip()
            # print(latitude, longitude)
            # print('~~~~~~~~~~~~~~~~~~`')

        except:
            # print('error')
            pass
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = ["<MISSING>" if x == "" else x for x in store]
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]

        if store[1] + " " + store[2] in addresses:
            continue
        addresses.append(store[1] + " " + store[2])
        # print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
