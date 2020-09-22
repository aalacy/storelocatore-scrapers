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
    locator_domain = "https://elpolloinka.com"
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
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"



    r= session.get('https://elpolloinka.com/gardena/about-us/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'html.parser')
    loc = soup.find('div',class_='entry-content')
    for p in loc.find_all('p'):
        list_p = list(p.stripped_strings)

        if (len(list_p) == 4 and re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_p[-1]))) or  ((len(list_p) == 6 ) and "Opening Hours:" == list_p[0]):
            if len(list_p) ==4:
                location_name =list_p[0]
                street_address = " ".join(list_p[1].split()[:-3])
                city =list_p[0].split(',')[0]
                state = list_p[0].split(',')[-1]
                zipp = list_p[1].split()[-1]
                phone_list =re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_p[-1]))
                phone = phone_list[0]
                
                latitude = soup.find("iframe")['src'].split('=')[-3].split(',')[0]
                longitude = soup.find("iframe")['src'].split('=')[-3].split(',')[-1].split('&')[0]
                hours_of_operation = " ".join(list(p.find_next("p").stripped_strings)).replace("Opening Hours:","")
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                store = ["<MISSING>" if x == "" or x == "Blank" else x for x in store]

                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                if store[2] in addresses :
                    continue
                addresses.append(store[2])
                return_main_object.append(store)


        elif len(list_p) >=4:
            location_name =list_p[0]
            street_address =" ".join(list_p[1].split()[:-3])
            city =list_p[0].split(',')[0]
            state = list_p[0].split(',')[-1]
            zipp = list_p[1].split()[-1]
            phone = phone_list =re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), " ".join(list_p))
            phone = phone_list[0]
            if len(list_p ) ==6:
                hours=" ".join(list_p[-2:]).split()
                if len(hours) ==8:
                    hours_of_operation = " ".join(hours[2:]).replace('&'," ")
                else:
                    hours_of_operation =" ".join(hours).replace('&'," ")
            else:
                hours_of_operation = list_p[-1]
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" or x == "Blank" else x for x in store]
            if store[2] in addresses :
                continue
            addresses.append(store[2])

            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)
        else:
            continue


    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
