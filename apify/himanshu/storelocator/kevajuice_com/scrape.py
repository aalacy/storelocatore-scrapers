import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    print("soup ===  first")

    base_url = "http://kevajuice.com/"
    r = requests.get("http://kevajuice.com/store-locator/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "kevajuice"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    # for script in soup.find_all("div", {'class': re.compile('tp-caption')}):
    #     store_url = script.find('a')['href']
    #     print("store_url == " + store_url)

    list_store_url = []
    for script in soup.find_all("div", {'class': re.compile('tp-caption')}):
        list_store_url.append(script.find('a')['href'])
        list_store_url = list(dict.fromkeys(list_store_url))

    for store_url in list_store_url:
        r_store = requests.get(store_url, headers=headers)
        soup_store = BeautifulSoup(r_store.text, "lxml")
        print("store_url = " + store_url)

        # try:
        if soup_store.find('tbody') is not None:
            for tr_data in soup_store.find('tbody').find_all('tr'):
                details = []
                for data in tr_data.find_all("td"):
                    details.append(list(data.stripped_strings))
                    print("data ======== " + str(list(data.stripped_strings)))

                hours_of_operation = ",".join(details[1])
                phone = details[2][0]

                country_code = 'US'
                store_number = '<MISSING>'
                latitude = '<INACCESSIBLE>'
                longitude = '<INACCESSIBLE>'

                if (len(details[0]) > 0):
                    location_name = details[0][0]
                    if len(details[0]) > 1:
                        street_address = details[0][1]
                    else:
                        street_address = '<MISSING>'
                    # print("details[0] === "+ str(len(details[0])))
                    # if len(details[0]) >= 3:
                    #     city = details[0][-1]
                    # else:
                    #     city = '<MISSING>'

                    zipp = details[0][-1].split(',')[-1].split(' ')[-1]
                    try:
                        zipp = (int(zipp))
                        state = details[0][-1].split(' ')[-2]
                        city = details[0][-1].split(',')[0]
                    except:
                        zipp = '<MISSING>'
                        state = '<MISSING>'
                        city = '<MISSING>'
                else:
                    street_address = '<MISSING>'
                    city = '<MISSING>'
                    state = '<MISSING>'
                    zipp = '<MISSING>'
                    location_name = '<MISSING>'

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]

                print("data = " + str(store))
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
        # except Exception as e:
        #     print(e)
        #     pass

    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
