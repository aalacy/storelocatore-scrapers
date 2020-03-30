import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

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
    return_main_object = []
    addresses = []
    # store_detail = []
    base_url = "https://www.shinola.com/"
######## authorised_retailers################
    count = 0
    while True:
        r = session.get(
            'https://www.shinola.com/shinstorelocator/index/searchlocation/?location=&authorizedRetailersCurrentPage=' + str(count)).json()
        last_page = r['authorized_retailers_is_last_page']

        for loc in r['authorized_retailers']:
            if loc["country"] in ["US", "CA"]:
                locator_domain = base_url
                location_name = loc['name']
                phone_tag = loc['phone']
                if phone_tag != None:
                    phone = phone_tag.split(',')[0].strip()
                else:
                    phone = "<MISSING>"

                street_address = loc['street']
                city = loc['city']
                country_code = loc['country']
                zipp = loc['postcode']
                if zipp != None:
                    zipp = zipp.replace('Mati', '').strip()
                state = loc['region']
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                page_url = "https://www.shinola.com/store-locator"
                location_type = "Authorized Retailers"
                store_number = "<MISSING>"
                hours_of_operation = "<MISSING>"
                if loc['postcode'] != None and len(zipp) == 4:
                    zipp = "0" + zipp
                if loc['postcode'] != None and len(zipp) == 3:
                    zipp = "00" + zipp
                if loc['postcode'] != None and "770657" in zipp:
                    zipp = "<MISSING>"
                if loc['postcode'] != None and "H9R 525" in zipp:
                    zipp = "<MISSING>"
                if loc['postcode'] != None and "24B" in zipp:
                    zipp = "<MISSING>"
                if loc['postcode'] != None and "BC 5T 3E2" in zipp:
                    zipp = "<MISSING>"

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = [el.replace('\xa0', ' ') if el !=
                         None else el for el in store]
                store = ["<MISSING>" if x == "" or x ==
                         None else x for x in store]
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                return_main_object.append(store)
                # print('data ==' + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~')
        if last_page is True:
            break
        count += 1
    # return return_main_object

    ####shinola_store#########
    r = session.get("https://www.shinola.com/store-locator")
    soup = BeautifulSoup(r.text, "lxml")

    vk = soup.find('div', {'id': 'amazon-root'}).find_next('script').find_next(
        'script').text.split('"stores":')[1].split(',"total"')[0]
    addresses = []
    k = json.loads(vk)

    for loc in k:
        if loc['country'] in ["US", "CA"]:
            locator_domain = base_url
            store_number = loc['storelocator_id']
            location_name = loc['name']
            street_address = loc['address']
            city = loc['city']
            state = loc['state']
            zipp = loc['zipcode']
            phone = loc['phone']
            latitude = loc['latitude']
            longitude = loc['longtitude']
            location_type = "shinola stores"
            country_code = loc['country']
            hours_of_operation = 'monday' + ' ' + loc['monday_open'] + ' ' + loc['monday_close'] + ' ' + 'tuesday' + ' ' + loc[
                'tuesday_open'] + ' ' + loc['tuesday_close'] + ' ' + ' wednesday' + ' ' + loc[
                'wednesday_open'] + ' ' + loc['wednesday_close'] + ' ' + ' thursday' + ' ' + loc[
                'thursday_open'] + ' ' + loc['thursday_close'] + ' ' + 'friday' + ' ' + loc[
                'friday_open'] + ' ' + loc['friday_close'] + ' ' + 'saturday' + ' ' + loc[
                'saturday_open'] + ' ' + loc['saturday_close'] + ' ' + 'sunday' + ' ' + loc[
                'sunday_open'] + ' ' + loc['sunday_close']
            page_url = loc['detail_url']
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = [el.replace('\xa0', ' ') if el !=
                     None else el for el in store]
            store = ["<MISSING>" if x == "" or x ==
                     None else x for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            return_main_object.append(store)
            # print('data ==' + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object
    # r = session.get(
    #     'https://www.shinola.com/shinstorelocator/index/searchlocation/?location=&shinolaStoresCurrentPage=0').json()
    # for loc in r['shinola_stores']:
    #     if loc["country"] in ["US", "CA"]:
    #         if loc['coming_soon'] == False:
    #             locator_domain = base_url
    #             location_name = loc['name']
    #             phone = loc['phone']
    #             street_address = loc['street']
    #             city = loc['city']
    #             country_code = loc['country']
    #             zipp = loc['postcode']
    #             state = loc['region']
    #             latitude = "<MISSING>"
    #             longitude = "<MISSING>"
    #             page_url = "https://www.shinola.com/store-locator"
    #             location_type = "shinola stores"
    #             store_number = "<MISSING>"
    #             hours_of_operation = 'monday' + ' ' + loc['monday_open'] + ' ' + loc['monday_close'] + ' ' + 'tuesday' + ' ' + loc[
    #                 'tuesday_open'] + ' ' + loc['tuesday_close'] + ' ' + ' wednesday' + ' ' + loc[
    #                 'wednesday_open'] + ' ' + loc['wednesday_close'] + ' ' + ' thursday' + ' ' + loc[
    #                 'thursday_open'] + ' ' + loc['thursday_close'] + ' ' + 'friday' + ' ' + loc[
    #                 'friday_open'] + ' ' + loc['friday_close'] + ' ' + 'saturday' + ' ' + loc[
    #                 'saturday_open'] + ' ' + loc['saturday_close'] + ' ' + 'sunday' + ' ' + loc[
    #                 'sunday_open'] + ' ' + loc['sunday_close']

    #             store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
    #                      store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
    #             store = [el.replace('\xa0', ' ') if el !=
    #                      None else el for el in store]
    #             store = ["<MISSING>" if x == "" or x ==
    #                      None else x for x in store]
    #             if store[2] in addresses:
    #                 continue
    #             addresses.append(store[2])
    #             return_main_object.append(store)
    #             # print('data ==' + str(store))
    #             # print('~~~~~~~~~~~~~~~~~~~~~~')


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
