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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://italianvillagepizza.com/"
    r = session.get(
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
        r_loc = session.get(links['href'], headers=headers)
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
            # print(location_name + " | " + street_address + " | " + city +
            #   " | " + state + " | " + zipp + " | " + hours_of_operation)

        else:
            tag_address = content.find_all('p')[-1]
            # print(tag_address)
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            list_address = list(tag_address.stripped_strings)
            # print(list_address)
            if len(list_address) == 3:
                del list_address[0]
            # print(list_address)
            if len(list_address) == 2:
                # print(list_address)
                phone = "".join(list_address[-1])
                hours_of_operation = "<MISSING>"
                st_add = list_address[0].split(',')
                # print(st_add)
                # print(len(st_add))
                # print("~~~~~~~~~~~~")
                if len(st_add) == 4:
                    street_address = "".join(st_add[0].strip())
                    city = "".join(st_add[1].strip())
                    state = "".join(st_add[2].strip())
                    zipp = "".join(st_add[-1].strip())
                    # print(street_address + " | " + city +
                    #       " | " + state + " | " + zipp)
                elif len(st_add) == 3 and "Clearview" in st_add[0]:
                    street_address = " ".join(st_add[0].split()[:-1])
                    city = "".join(st_add[0].split()[-1])
                    zipp = "".join(st_add[-1].strip())
                    state = "".join(st_add[-2].strip())
                    # print(street_address + " | " + city +
                    #       " | " + state + " | " + zipp)
                elif len(st_add) == 3 and "Clearview" not in st_add[0]:
                    # print(st_add)
                    street_address = "".join(st_add[0].strip())
                    city = "".join(st_add[1].strip())
                    state = "".join(st_add[-1].split()[-2].strip())
                    zipp = "".join(st_add[-1].split()[-1].strip())
                    # print(street_address + " | " + city +
                    #       " | " + state + " | " + zipp)
                else:
                    list_st_address = "".join(st_add).split()[:-3]
                    street_address = " ".join(list_st_address)
                    city = "".join(st_add).split()[-3]
                    state = "".join(st_add).split()[-2]
                    zipp = "".join(st_add).split()[-1]

                # print(street_address + " | " + city +
                #       " | " + state + " | " + zipp)
            else:
                # print(list_address)
                if list_address == []:
                    tag_address = content.find_all('p')[-4:]
                    st_add = list(tag_address[0].stripped_strings)
                    # print(st_add)
                    # print(len(st_add))
                    # print("~~~~~~~~~~~~~~~~~~~~~~~")
                    if len(st_add) == 2:
                        # print(st_add)
                        street_address = "".join(st_add[0].strip())
                        city = "".join(st_add[-1].split(',')[0].strip())
                        state = "".join(
                            st_add[-1].split(',')[-1].split()[0].strip())
                        zipp = "".join(
                            st_add[-1].split(',')[-1].split()[-1].strip())
                        phone1 = list(tag_address[1].stripped_strings)
                        phone = "".join(phone1)
                        hours_of_operation = "<MISSING>"
                        # print(street_address + " | " + city +
                        # " | " + state + " | " + zipp + ' | ' +phone)
                    else:
                        # print(st_add)
                        st_address = list(tag_address[1].stripped_strings)
                        street_address = "".join(
                            st_address[0].split(',')[0].strip())
                        city = "".join(st_address[0].split(',')[1].strip())
                        state = "".join(st_address[0].split(
                            ',')[-1].split()[0].strip())
                        zipp = "".join(st_address[0].split(
                            ',')[-1].split()[-1].strip())
                        phone = "".join(st_address[-1].strip())
                        # print(street_address + " | " + city +
                        # " | " + state + " | " + zipp + ' | ' +phone)
                        hours = list(tag_address[2].stripped_strings)
                        hours_of_operation = " ".join(hours).encode(
                            'ascii', 'ignore').decode('ascii').strip()
                        # print(hours_of_operation)
                else:
                    # print(list_address)
                    tag_address = content.find_all('p')[-2:]
                    # print(tag_address)
                    # print(len(tag_address))
                    # print("~~~~~~~~~~~~~")
                    st_add = list(tag_address[0].stripped_strings)
                    # print(st_add)
                    # print(len(st_add))
                    if len(st_add) == 1:
                        street_address = " ".join(st_add[0].split(',')[:2])
                        city = "".join(st_add[0].split(',')[2].strip())
                        state = "".join(st_add[0].split(',')[3].strip())
                        zipp = "".join(st_add[0].split(',')[-1].strip())
                        # print(street_address + " | " + city +
                        #       " | " + state + " | " + zipp)
                        phone1 = st_add = list(tag_address[1].stripped_strings)
                        phone = "".join(phone1)
                        hours_of_operation = "<MISSING>"
                    else:
                        tag_address = content.find(
                            'li').nextSibling.nextSibling
                        address = tag_address.text.split(',')
                        street_address = "".join(address[0].strip())
                        city = "".join(address[1].strip())
                        state = "".join(address[-1].split()[0].strip())
                        zipp = "".join(address[-1].split()[-1].strip())
                        phone = tag_address = content.find(
                            'li').nextSibling.nextSibling.nextSibling.nextSibling.text
                        hours_of_operation = "<MISSING>"
                        # print(street_address + " | " + city +
                        #       " | " + state + " | " + zipp + "|" + phone)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        store = ["<MISSING>" if x ==
                 "" else x for x in store]
        return_main_object.append(store)
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
