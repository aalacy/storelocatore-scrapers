import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import sgzip
# import json
# import http.client
# import time



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
    # zips = sgzip.coords_for_radius(100)
    # zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    #     "Accept": "application/json, text/plain, */*",
    #     "X-API-Key": "ec8f7bbece2ab8e98f4e02b523f126e2"
    #     # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    # }

    # it will used in store data.
    base_url = "https://caribbeancinemas.com/"
    locator_domain = "https://caribbeancinemas.com/"
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
    page_url = "<MISSING>"

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",

    }

    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    footer = soup.find('footer').find('div', class_='three-fourth column')

    for loc_url in footer.find_all(lambda tag: (tag.name == "a") and "ARUBA" != tag.text and "PANAMA" != tag.text and "TRINIDAD" != tag.text):
        p_url = loc_url['href'].split('/')
        if len(p_url) != 4:
            page_url = 'https:' + loc_url['href']
        else:
            page_url = loc_url['href']
        rr = session.get(page_url, headers=headers)
        rr_soup = BeautifulSoup(rr.text, 'lxml')
        try:
            coords = rr_soup.find_all('div', class_='section')[1].find(
                'div', class_='column one-fourth1 column_column').find('iframe')
            if coords != None:
                if len(coords['src'].split('!2d')) > 1:
                    longitude = coords['src'].split(
                        '!2d')[1].split('!')[0].strip()
                    latitude = coords['src'].split(
                        '!3d')[1].split('!')[0].strip()
                else:
                    latitude = coords['src'].split('=')[1].split(',')[0]
                    longitude = coords['src'].split('=')[1].split(',')[
                        1].split('&')[0]
            else:
                # print(page_url)
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            info = rr_soup.find('div', class_='sections_group').find(
                'div', class_='items_group clearfix').find('div', {'id': 'cineinfo'})
            location_name = info.h4.text.strip()
            # print(location_name)

            list_phone = list(info.find('li', class_='phone').stripped_strings)
            if list_phone != []:
                phone = list_phone[0].strip()
            else:
                phone = "<MISSING>"
            address = info.find('li', class_='address')
            list_address = list(address.stripped_strings)
            if list_address == []:
                street_address = "<MISSING>"
                city = page_url.split('/')[-2].split('-')[0].strip()

            else:
                if len(list_address) > 1:
                    location_name = list_address[0].strip()
                    if len(list_address[-1].split(',')) > 1:
                        street_address = " ".join(
                            list_address[-1].split(',')[:-1]).strip()
                        city = "<MISSING>"
                        state = "<MISSING>"
                    else:
                        if len(list_address[-1].split()) > 1:
                            street_address = list_address[-1].strip()
                            location_name = list_address[0].strip()
                        else:
                            street_address = " ".join(
                                list_address[0].split()[3:]).strip()
                            location_name = " ".join(
                                list_address[0].split()[:3])
                        city = "<MISSING>"
                        state = "<MISSING>"
                else:
                    street_address = list_address[0].strip()
                    location_name = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    # print(list_address)
                    # print(len(list_address))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                # street_address = list_address[0].strip()
                # c = page_url.split('/')[-2]
                # # print(p_url)
                # if "cinestarguadeloupe.com" == c:
                #     city = "<MISSING>"
                # elif "caribbean-cinemas-vip-at-paseo-herencia" == c:
                #     city = "paseo-herencia"
                # else:

                #     city = c.replace(
                #         '-cinemas', '').replace('-megaplex-8', '').strip()
                # print(city)

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = ["<MISSING>" if x == "" else x for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])

            # print(street_address)

            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)

        except:
            # page_url = "https://caribbeancinemas.com/location/republica-dominicana"
            continue

    link = soup.find('nav', {'id': 'menu'}).find(
        'li', class_='menu-item menu-item-has-children').find('ul', class_='sub-menu mfn-megamenu mfn-megamenu-5')
    for li in link.find_all('li', class_='menu-item'):
        try:
            if "#MORE" != li.a['href']:
                page_url = "https:" + li.a['href']
                r_loc = session.get(page_url, headers=headers)
                soup_loc = BeautifulSoup(r_loc.text, 'lxml')
                coords = soup_loc.find_all('div', class_='section')[1].find(
                    'div', class_='column one-fourth1 column_column').find('iframe')
                if len(coords['src'].split('!2d')) > 1:
                    longitude = coords['src'].split(
                        '!2d')[1].split('!')[0].strip()
                    latitude = coords['src'].split(
                        '!3d')[1].split('!')[0].strip()
                else:
                    latitude = coord['src'].split('q=')[1].split(',')[0]
                    longitude = coord['src'].split('q=')[1].split(',')[
                        1].split('&')[0]

                # if "1m0" != coords['src'].split('!')[4]:
                #     latitude = coords['src'].split('!')[4].split(
                #         '.')[0][-2:] + "." + coords['src'].split('!')[4].split('.')[-1]
                #     longitude = coords['src'].split('!')[5].split('2d')[-1]
                # else:
                #     latitude = coords['src'].split('@')[1].split(',')[0]
                #     longitude = coords['src'].split('@')[1].split(',')[1]

                info = soup_loc.find('div', class_='sections_group').find(
                    'div', class_='items_group clearfix').find('div', {'id': 'cineinfo'})
                # location_name = info.h4.text.strip()
                phone = info.find('li', class_='phone').text.strip()
                address = info.find('li', class_='address')
                list_address = list(address.stripped_strings)
                # print(list_address)
                # print(len(list_address))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                if len(list_address) > 1:
                    phone_list = re.findall(re.compile(
                        ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_address[-1]))

                    if phone_list == []:
                        location_name = list_address[0].strip()
                        tag_address = list_address[1].split(',')
                        # print(tag_address)
                        # print(len(tag_address))
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        city = info.h4.text.strip()
                        if len(tag_address) > 1:
                            state = tag_address[-1].split()[0].strip()
                            zipp = tag_address[-1].split()[-1].strip()
                            street_address = " ".join(tag_address[:-1]).strip()
                        else:
                            street_address = tag_address[0].strip()
                            state = "<MISSING>"
                            zipp = "<MISSING>"

                    else:
                        location_name = info.h4.text.strip()
                        street_address = list_address[0].split(',')[0].strip()
                        city = list_address[0].split(',')[1].strip()
                        state = list_address[0].split(
                            ',')[-1].split()[0].strip()
                        zipp = list_address[0].split(
                            ',')[-1].split()[-1].strip()
                else:
                    location_name = info.h4.text.strip()
                    street_address = ",".join(
                        list_address[0].split(',')[:-2]).strip()
                    city = list_address[0].split(',')[-2].strip()
                    state = list_address[0].split(',')[-1].split()[0].strip()
                    zipp = list_address[0].split(',')[-1].split()[-1].strip()
                if "Ponce" == state or "Hatillo" == state:
                    state = "<MISSING>"
                if "Guayama" not in city and "Fajardo" not in city and "Aguadilla" not in city:
                    city = "<MISSING>"
                #     print(list_address)
                #     print('~~~~~~~~~~~~~~~~~~~~~~~~~')
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = ["<MISSING>" if x == "" else x for x in store]
                if store[2] in addresses:
                    continue
                addresses.append(store[2])

                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)

        except:
            pass

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
