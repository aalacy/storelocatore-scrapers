import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://italianvillagepizza.com/"
    r = requests.get(
        "https://italianvillagepizza.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())

    return_main_object = []

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
    location_type = "italianvillagepizza"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    val = soup.find("div", class_="webcom-wrapper").find('ul',
                                                         {'id': 'menu-header-menu'}).find('li', {'id': 'menu-item-141'}).find('ul', class_="sub-menu")

    for links in val.find_all('a'):
        r_loc = requests.get(links['href'], headers=headers)
        r_soup = BeautifulSoup(r_loc.text, "lxml")

        content = r_soup.find('div', {'role': 'main'}).find(
            'div', class_="entry-content")
        lname = content .find(lambda tag: (
            tag.name == "h1" or tag.name == "p") and "Pizza " in tag.text)
        location_list = list(lname.stripped_strings)

        location_name = "".join(location_list[0].replace(
            "\xa0", " ").replace('Delivery', "Shop"))
        address = content .find(lambda tag: (
            tag.name == "h2") and "Our Pizza Shop in " in tag.text)
        if address is not None:
            tag_address = address.nextSibling.nextSibling
            address_list = list(tag_address.stripped_strings)
            # print("".join(address_list))

            street_address = "".join(address_list).split(',')[0]
            city = "".join(address_list).split(',')[1]
            state = "".join(address_list).split(',')[2].split()[0]
            zipp = "".join(address_list).split(',')[2].split()[1]
            # print(street_address, city, state, zipp)
            phone = address.nextSibling.nextSibling.nextSibling.nextSibling.text
            hours = content .find(lambda tag: (
                tag.name == "h2") and "Hours of Operation" == tag.text).nextSibling.nextSibling
            list_hours = list(hours.stripped_strings)
            hours_of_operation = "".join(list_hours).replace("\xa0", " ")
            # print(hours_of_operation)
        else:
            if "https://italianvillagepizza.com/butler/" == links['href'] or "https://italianvillagepizza.com/elizabeth/" == links['href'] or "https://italianvillagepizza.com/downtown-pittsburgh/" == links['href'] or "https://italianvillagepizza.com/lansing-mi/" == links['href'] or "https://italianvillagepizza.com/hickory-nc/" == links['href']:
                tag_address = content.find_all('p')[-1]
                list_address = list(tag_address.stripped_strings)
                # print(list_address)
                if len(list_address) == 3:
                    street_address = " ".join(list_address[1].split()[:-3])
                    city = "".join(list_address[1].split()[-3])
                    state = "".join(list_address[1].split()[-2])
                    zipp = "".join(list_address[1].split()[-1])
                    # print(street_address, city, state, zipp)
                    phone = "".join(list_address[-1])
                else:
                    street_address = "".join(list_address[0].split(',')[0])
                    city = "".join(list_address[0].split(',')[1])
                    state = "".join(list_address[0].split(',')[-1].split()[0])
                    zipp = "".join(list_address[0].split(',')[-1].split()[-1])
                    phone = "".join(list_address[-1])
                    hours_of_operation = "<MISSING>"
                    # print(street_address, city, state, zipp, phone)
            if "https://italianvillagepizza.com/hazel-wood/" == links['href']:
                tag_address = content.find_all(
                    'p')[-1].nextSibling.nextSibling.nextSibling.nextSibling
                list_address = list(tag_address.stripped_strings)
                # print(list_address)
                street_address = "".join(list_address).split(',')[0]
                city = "".join(list_address).split(',')[1]
                state = "".join(list_address).split(',')[-1].split()[0]
                zipp = "".join(list_address).split(',')[-1].split()[-1]
                phone = content.find_all(
                    'p')[-1].nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.text

            if "https://italianvillagepizza.com/greensburg/" == links['href']:
                address = content.find(lambda tag: (
                    tag.name == "p")and "Pizza Place in Greensburg, Pa" == tag.text).nextSibling.nextSibling
                list_address = list(address.stripped_strings)
                # print(list_address)
                street_address = "".join(list_address[0].split(',')[0])
                city = "".join(list_address[0].split(',')[1])
                state = "".join(list_address[0].split(',')[-1].split()[0])
                zipp = "".join(list_address[0].split(',')[-1].split()[-1])
                phone = "".join(list_address[1])

                hours = content .find(lambda tag: (
                    tag.name == "h2") and "Hours of Operation" == tag.text).nextSibling.nextSibling
                list_hours = list(hours.stripped_strings)
                hours_of_operation = "".join(list_hours).replace("\xa0", " ")
                # print(street_address, city, state,
                #       zipp, phone, hours_of_operation)
            if "https://italianvillagepizza.com/paducah-ky/" == links['href']:
                address = content .find(lambda tag: (
                    tag.name == "p") and "Italian Village Pizza Paducah" == tag.text).nextSibling.nextSibling
                # print(address)
                list_address = list(address.stripped_strings)
                # print(list_address)
                street_address = "".join(list_address[0])
                city = "".join(list_address[1].split(',')[0])
                state = "".join(list_address[1].split(',')[1].split()[0])
                zipp = "".join(list_address[1].split(',')[1].split()[-1])
                phone = address = content .find(lambda tag: (
                    tag.name == "p") and "Italian Village Pizza Paducah" == tag.text).nextSibling.nextSibling.nextSibling.nextSibling.text
                hours_of_operation = "<MISSING>"
                print(street_address, city, state,
                      zipp, phone, hours_of_operation)

            if "https://italianvillagepizza.com/greenville-nc/" == links['href']:
                address = content .find(lambda tag: (
                    tag.name == "p") and "Italian Village Pizza Greenville, NC" == tag.text).nextSibling.nextSibling
                list_address = list(address.stripped_strings)
                # print(list_address)
                s1 = " ".join(list_address).split(',')[:-3]
                street_address = "".join(s1)
                city = "".join(list_address).split(',')[-3]
                state = "".join(list_address).split(',')[-2]
                zipp = "".join(list_address).split(',')[-1]
                phone = content .find(lambda tag: (
                    tag.name == "p") and "Italian Village Pizza Greenville, NC" == tag.text).nextSibling.nextSibling.nextSibling.nextSibling.text
                hours_of_operation = "<MISSING>"
                # print(street_address, city, state,
                #       zipp, phone, hours_of_operation)
        store = [locator_domain, location_name, street_address, city, state.replace('Pa,','PA').replace('NC,','NC'), zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        store = ["<MISSING>" if x ==
                 "" else x for x in store]
        return_main_object.append(store)
        print("data = " + str(store))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
