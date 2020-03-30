import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding='utf8') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://www.fourseasons.com"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("ul", {"class": "Navigation-mainLinks"}):
        semi_part = parts.find_all("li", {"class": "Navigation-item"})[0]
        # print(base_url + semi_part.find("a")['href'])
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        store_request = session.get(base_url + semi_part.find("a")['href'])
        store_soup = BeautifulSoup(store_request.text, "lxml")
        dl = store_soup.find('dl', class_='Accordion')
        accordion = dl.find('div', class_='Accordion-item')

        for in_semi_part in accordion.find_all("div", {"class": "LinksList-linkContainer"}):
            page_url = base_url + in_semi_part.find("a")['href']
            location_name = in_semi_part.find("a").text
            city = in_semi_part.find("a").text.split(
                ',')[-1].strip()
            city = city.split('(')[0].strip()
            store_re = session.get(
                base_url + in_semi_part.find("a")['href'])
            main_store_soup = BeautifulSoup(store_re.text, "lxml")

            inner_semi_part = main_store_soup.find(
                "div", {"id": "LocationBar"})
            temp_storeaddresss = list(inner_semi_part.stripped_strings)

            return_object = []
            address = temp_storeaddresss[0].split(',')
            if len(address) == 1:
                street_address = "".join(address)
                state = "<MISSING>"
                zipp = "<MISSING>"
            elif len(address) == 2:
                if "Lanai City" != address[0] and "Punta Mita" != address[0]:
                    street_address = address[0]
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                else:
                    street_address = "<MISSING>"
                    us_zip_list = re.findall(re.compile(
                        r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address[-1]))
                    if us_zip_list:
                        zipp = us_zip_list[0]
                        state = address[-1].split()[0]
                    else:
                        zipp = "<MISSING>"
                        state = "<MISSING>"
            elif len(address) == 3:
                street_address = address[0].strip()
                state = address[-1].split()
                if len(address[-1].split()) == 1:
                    state = address[-1].strip()
                    zipp = "<MISSING>"
                elif len(address[-1].split()) == 2:
                    state = address[-1].split()[0]
                    zipp = address[-1].split()[1]
                elif "U.S.A." in " ".join(address):
                    # print(address[-1].split())
                    state = " ".join(address[-1].split()[:-2])
                    zipp = address[-1].split()[-2].strip()
                elif "Canada" in " ".join(address):
                    # print(address[-1].split())
                    state = " ".join(address[-1].split()[:-3])
                    zipp = " ".join(address[-1].split()[-3:-1])
                    # print(state, zipp)
            elif len(address) == 4:
                # print(address)
                if "Canada" in " ".join(address):
                    street_address = address[0].strip()
                    state = address[1].split()[-1].strip()
                    zipp = address[-2].strip()
                elif " U.S.A." == address[-1]:
                    # print(address)
                    street_address = address[0].strip()
                    state = address[-2].split()[0].strip()
                    zipp = address[-2].split()[1].strip()
                elif "Mexico" in " ".join(address):
                    street_address = address[0].strip()
                    state = "<MISSING>"
                    zipp = address[-1].split()[0].strip()
                else:
                    street_address = " ".join(address[:2]).strip()
                    state = address[-1].split()[0].strip()
                    zipp = address[-1].split()[1].strip()
            elif len(address) == 5:
                street_address = " ".join(address[:2]).strip()
                if len(address[-1].split()) > 1:
                    state = address[-1].split()[0].strip()
                    zipp = address[-1].split()[1].strip()
                else:
                    state = address[-1].strip()
                    zipp = "<MISSING>"
            else:
                street_address = address[0].strip()
                zipp = address[3].strip()
                state = address[-2].strip()
            if zipp != "<MISSING>":
                if len(zipp) >5:
                    country_code = "CA"
                else:
                    country_code = "US"
            else:
                # print(address)
                country_code = "US"
            if('Location' in temp_storeaddresss):
                temp_storeaddresss.remove('Location')

            if(len(temp_storeaddresss) == 1):
                phone = '<MISSING>'
            else:
                phone = temp_storeaddresss[1].split('or')[0].strip()
            if "York" == zipp:
                zipp = address[-2].split()[-1].strip()
            if "New" == state:
                state = address[1].strip()
            if "U.S.A." in state:
                state= address[-2].split()[0].strip()
            if "Caribbean" in state:
                state = "<MISSING>"
            if "Baja California Sur" in state or "Bahamas" in state:
                continue
            if "Anguilla" in state  :
                state = "<MISSING>"
            
            return_object.append(base_url)
            return_object.append(location_name)
            return_object.append(street_address)
            return_object.append(city)
            return_object.append(state)
            return_object.append(zipp)
            return_object.append(country_code)
            return_object.append("<MISSING>")
            return_object.append(phone)
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_object.append(page_url)
            return_main_object.append(return_object)

            #print('data==' + str(return_object))
            #print('~~~~~~~~~~~~~~~~~~~~')
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
