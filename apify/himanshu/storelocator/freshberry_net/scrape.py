import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    return_main_object = []  


    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data
    base_url = 'http://freshberry.net/'
    locator_domain = "http://freshberry.net/"
    page_url = "<MISSING>"
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

    r = session.get('http://freshberry.net/locations.html',headers = headers)
    soup= BeautifulSoup(r.text,'lxml')
    # print(soup.prettify())
    lat= soup.find('iframe')['src'].split('ll=')[-1].split(',')[0]
    lng= soup.find('iframe')['src'].split('ll=')[-1].split(',')[1].split('&')[0]
    coords = []
    coords.append(lat)
    coords.append(lng)

    for store in soup.find('div',{'id':'interiormain'}).find_all('ul')[:-4]:
        for details in store.find_all('li'):
            latitude = coords[0].strip()
            longitude = coords[1].strip()
            list_store = list(details.stripped_strings)
            if len(list_store) ==4:
                location_name = list_store[0].strip()
                street_address = list_store[1].strip()
                city = list_store[2].split(',')[0].strip()
                state = list_store[2].split(',')[1].split()[0].strip()
                zipp = list_store[2].split(',')[1].split()[-1].strip()
                phone = list_store[-1].split()[-1].strip()
                hours_of_operation = "<MISSING>"

            elif len(list_store) == 7:
                if "Miami" == list_store[0]:
                    location_name = ",".join(list_store[:2]).strip()
                    street_address = list_store[2].strip()
                    city= list_store[3].split(',')[0].strip()
                    state = list_store[3].split(',')[-1].split()[0].strip()
                    zipp = list_store[3].split(',')[-1].split()[-1].strip()
                    phone =  re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_store[4]))[0]
                    hours_of_operation = list_store[-1].strip()

                else:
                    location_name = list_store[0].strip()
                    street_address = list_store[1].strip()
                    city = list_store[2].split(',')[0].strip()
                    state = list_store[2].split(',')[-1].split()[0].strip()
                    zipp = list_store[2].split(',')[-1].split()[-1].strip()
                    phone =  re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_store[3]))[0]
                    hours_of_operation = " ".join(list_store[-2:]).strip()

            elif len(list_store) ==8:
                if "Wilmington" == list_store[0]:
                    location_name = ",".join(list_store[:2]).strip()
                    street_address  = list_store[2].strip()
                    city= list_store[3].split(',')[0].strip()
                    phone= re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_store[4]))[0]
                    hours_of_operation = " ".join(list_store[6:]).strip().replace('&','and')
                    if len(list_store[3].split(',')[-1].split()) >2:
                        state =" ".join(list_store[3].split(',')[-1].split()[:2]).strip()
                        zipp = list_store[3].split(',')[-1].split()[-1].strip()

                    else:
                        state =" ".join(list_store[3].split(',')[-1].split()).strip()
                        zipp = "<MISSING>"

                else:
                    location_name = list_store[0].strip()
                    street_address = list_store[1].strip()
                    city = list_store[2].split(',')[0].strip()
                    state =" ".join(list_store[2].split(',')[-1].split()[:-1]).strip()
                    zipp = list_store[2].split(',')[-1].split()[-1].strip()
                    phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_store[3]))[0]
                    hours_of_operation =  " ".join(list_store[5:]).strip()


            else:
                location_name = ",".join(list_store[:2]).strip()
                street_address  = list_store[2].strip()
                city= list_store[3].split(',')[0].strip()
                state = list_store[3].split(',')[-1].split()[0].strip()
                zipp = list_store[3].split(',')[-1].split()[-1].strip()
                phone= re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_store[4]))[0]
                hours_of_operation = " ".join(list_store[6:]).strip().replace('â','')




            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" or x == None else x for x in store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)
    return return_main_object



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
