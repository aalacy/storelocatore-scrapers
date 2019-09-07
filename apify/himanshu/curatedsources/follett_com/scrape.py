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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # print("soup ===  first")

    base_url = "https://www.follett.com"

   
    r = ""
    isInitData = False;
    while not isInitData:
        r = requests.get("https://follett.com/college-bookstores/", headers=headers)
        
        soup = BeautifulSoup(r.text, "lxml")
        if soup.find('div') is not None:
            isInitData = True

    
   


    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

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
    location_type = "follett"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # print("soup ==== " + str(soup))

    for script in soup.find_all('div', {'class': 'block-store col-lg-4 col-md-4 col-sm-6 col-xs-12 widget-block'}):
        if script.find('a') is not None and script.find('a')['href'][0] is "/":
            location_url = base_url + script.find('a')['href']
            location_name = script.find('a').text

            store_number = location_url.split('&storeid=')[1]
            

            isData = False;
            while not isData:

                try:
                    r_location = requests.get(location_url, headers=headers)
                except:
                    continue    

                soup_location = BeautifulSoup(r_location.text, "lxml")

                if soup_location.find('div',{'itemprop':'address'}) is not None:
                    full_address = ",".join(list(soup_location.find('div',{'itemprop':'address'}).stripped_strings)).replace(',,,',',')
                    isData = True
                else:
                    continue

                # print('street_address === '+ str(full_address))

                street_address = ','.join(full_address.split(',')[:-3])
                zipp = (full_address.split(',')[-1])
                state = (full_address.split(',')[-2])
                city = (full_address.split(',')[-3])

                phone = soup_location.find("span",{"itemprop":"telephone"}).text

                map_url = soup_location.find("div",{"class":"col-lg-8 col-md-8 col-sm-12 col-xs-12 widget-block"}).find('img')['src']
                latitude = map_url.split('?center=')[1].split('&')[0].split(',')[0]
                longitude = map_url.split('?center=')[1].split('&')[0].split(',')[1]

                # print("longitude === "+ str(longitude))
                # print("latitude === "+ str(latitude))

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]

                store = ["<MISSING>" if x == "" else x for x in store]

                
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
