
import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import selenium
from selenium import webdriver


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.cslplasma.com"
    r = requests.get(base_url + "/locations/search-results-state")
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())
    return_main_object = []
    comming_soon = []
    for option in soup.find('select', {"name": "SelectedState"}).find_all("option"):
        if option['value'] == "":
            continue
        location_request = requests.get(base_url + option['value'])
        lcoation_soup = BeautifulSoup(location_request.text, 'lxml')
        # section = soup_loc.find('section', class_='center-search-results')
        # container = soup_loc.find('div', class_='center-search-item-container')

        for location in lcoation_soup.find_all("div", {"class": "center-search-item"}):
            # print(location.prettify())
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            store = []

            location_address = list(location.find(
                "div", {"class": "center-search-item-addr"}).stripped_strings)
            if location_address[1] != "Coming Soon" and location_address[1] != "Coming soon":

                name = location.find(
                    "span", {'class': "center-search-item-name"}).text

                street_address = location_address[1].strip()
                # if "Coming Soon" in street_address:
                #     print(street_address)
                city = location_address[-1].split(',')[0].strip()
                state = location_address[-1].split(',')[-1].split()[0].strip()
                zipp = location_address[-1].split(',')[-1].split()[-1].strip()
                if "" == city:
                    city = "<MISSING>"
                location_hours = list(location.find(
                    'div', {"class": "center-search-item-contact"}).stripped_strings)

                phone = ""
                if "Ph:" in location_hours:
                    phone = location_hours[location_hours.index("Ph:") + 1]
                else:
                    phone = "<MISSING>"
                #print(phone)
                page_url = base_url + location.find_all("a")[-1]['href']
                import warnings
                warnings.filterwarnings('ignore')
                browser = webdriver.PhantomJS(
                    '/usr/local/Cellar/phantomjs-2.1.1-macosx/bin/phantomjs')
                # browser = webdriver.Firefox()
                browser.get(page_url)
                iframe = browser.find_element_by_tag_name("iframe")
                browser.switch_to.default_content()
                browser.switch_to.frame(iframe)
                # print(browser.current_url)
                iframe_source = browser.page_source
                soup = BeautifulSoup(iframe_source, 'lxml')
                l1 = []
                l2 = []
                for script in soup.find_all("script"):
                    if "initEmbed" in script.text:
                        try:
                            coords = json.loads(script.text.split(
                                'initEmbed(')[1].split(');')[0])[5][-2][0][-1][1]
                            res = [i for i in coords if i]
                            lat = res[2][-2]
                            lng = res[2][-1]
                            l1.append(lat)
                            l2.append(lng)
                        except:
                            # print(json.loads(script.text.split(
                            #     'initEmbed(')[1]))
                            # print(soup.prettify())
                            lat = "<MISSING>"
                            lng = "<MISSING>"
                            l1.append(lat)
                            l2.append(lng)

                store = []
                store.append("https://www.cslplasma.com")
                store.append(name)
                store.append(street_address)
                store.append(city if city != "" else "<MISSING>")
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone != "" else "<MISSING>")
                store.append("<MISSING>")
                store.append(l1.pop(0))
                store.append(l2.pop(0))
                store.append(location_hours[-1] if location_hours[-1] !=
                             "Contact Info" and location_hours[-1] != "Coming Soon" else "<MISSING>")
                store.append(page_url)
                #print("===" + str(store))
                #print('~~~~~~~~~~~~~~~~~~~~`')
                return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
