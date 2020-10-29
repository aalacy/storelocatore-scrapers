import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import json
# import sgzip
# import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('southcentralbank_com')





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
    locator_domain = "https://www.southcentralbank.com/"
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
    page_url = "https://www.southcentralbank.com/locations/"



    r= session.get('https://www.southcentralbank.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')

    for row in soup.find_all('div',class_='panel-group'):

        location_name = row.h4.text.strip()
        logger.info(location_name)
        coords = row.find('div',class_='marker')
        latitude= coords['data-lat']
        longitude  = coords['data-lng']
        address= row.find('div',class_= "map-panel")
        list_address= list(address.stripped_strings)
        # logger.info(len(list_address))
        # logger.info(list_address)
        # logger.info("~~~~~~~~~~~~~~~~~~")
        if len(list_address) ==3:
            street_address = list_address[1]
            city = list_address[-1].split(',')[0]
            state = list_address[-1].split(',')[1].split()[0]
            zipp =list_address[-1].split(',')[1].split()[-1]
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"


        if len(list_address) == 6:
            phone1 = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_address[2]))
            if phone1 != []:

                street_address = list_address[0]
                city = list_address[1].split(',')[0]
                state = list_address[1].split(',')[-1].split()[0]
                zipp = list_address[1].split(',')[-1].split()[-1]
                phone = phone1[0]
                hours_of_operation = list_address[-1]



            else:
                zip_code = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(list_address[2]))
                if zip_code != []:
                    def divide_chunks(l, n):

                        # looping till length l
                        for i in range(0, len(l), n):
                            yield l[i:i + n]

                    n = 3

                    x = list(divide_chunks(list_address, n))
                    for  i in x:
                        # logger.info(i)
                        location_name = i[0]
                        street_address = i[1]
                        city = i[-1].split(',')[0]
                        state = i[-1].split(',')[-1].split()[0]
                        zipp =  i[-1].split(',')[-1].split()[-1]
                        phone = "<MISSING>"
                        hours_of_operation = "<MISSING>"


                else:
                    def divide_chunks(l, n):

                        # looping till length l
                        for i in range(0, len(l), n):
                            yield l[i:i + n]

                    n = 2

                    x = list(divide_chunks(list_address, n))
                    for i in x:
                        # logger.info(i)
                        street_address = i[0]
                        city = i[-1].split(',')[0]
                        state = i[-1].split(',')[-1].split()[0]
                        zipp = i[-1].split(',')[-1].split()[-1]
                        phone = "<MISSING>"
                        hours_of_operation = "<MISSING>"


        if len(list_address) == 7 or len(list_address) == 8 or len(list_address) == 13 or len(list_address) == 14 or len(list_address) == 16 or (len(list_address) == 9 and re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_address[2])) !=[]) or len(list_address) ==10 or len(list_address)== 11 or len(list_address) == 12:

            street_address = list_address[0]
            city = list_address[1].split(',')[0]
            state = list_address[1].split(',')[1].split()[0]
            zipp = list_address[1].split(',')[1].split()[-1]
            phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_address[2]))[0]
            hours_of_operation = " ".join(list_address[4:])



        elif len(list_address) == 9 and re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_address[2])) ==[] or len(list_address) >12:

            def divide_chunks(l, n):

                # looping till length l
                for i in range(0, len(l), n):
                    yield l[i:i + n]

            n = 3

            x = list(divide_chunks(list_address, n))
            for  i in x:
                location_name = i[0]
                street_address = i[1]
                city = i[-1].split(',')[0]
                state = i[-1].split(',')[1].split()[0]
                zipp = i[-1].split(',')[1].split()[-1]
                phone = "<MISSING>"
                hours_of_operation = "<MISSING>"

        if "phone" in location_name.lower():
            location_name = list_address[0]
            street_address = list_address[1]
            city = list_address[2].split(',')[0]
            state = list_address[2].split(',')[1].split()[0]
            zipp = list_address[2].split(',')[1].split()[-1]
            phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_address[3]))[0]
            hours_of_operation = " ".join(list_address[4:])

        if "2908 Ring Road" in city:
            street_address = "2908 Ring Road"
            city = "Elizabethtown"
            hours_of_operation = hours_of_operation[:hours_of_operation.find("Drive")]

        if "Drive" in hours_of_operation:
            hours_of_operation = hours_of_operation[:hours_of_operation.find("Drive")]
        hours_of_operation = hours_of_operation.replace("Lobby Hours","").strip()
        if "appointment" in hours_of_operation.lower():
            hours_of_operation = "<MISSING>"

        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')

        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        store = [x.replace("–","-") for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # logger.info("data===="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return_main_object.append(store)

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
