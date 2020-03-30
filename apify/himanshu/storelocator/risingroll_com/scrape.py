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

    base_url = "https://risingroll.com"
    r = session.get(
        "https://risingroll.com/locations-menu/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())

    return_main_object = []

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zip = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "risingroll"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for val in soup.find_all('div', class_="et_section_regular"):
        # print(val)
        for location in val.find_all('div', {'id': 'locdesc'}):
            if location != []:
                location_name = location.find('h1').text
                # print(location_name)
                location_details = location.find('a')

                r_location = session.get(
                    base_url + location_details['href'], headers=headers)
                soup_loc = BeautifulSoup(r_location.text, "lxml")
                # print(soup_loc)
                for ad in soup_loc.find('div', class_="et_pb_section_1").find_all(
                        'div', {'class': 'et_pb_text_inner'}):
                    for p_tag in ad.find_all('p'):
                        # print(p_tag)
                        # print("~~~~~~~~~~~~~~~~~~~~~~~~")

                        if "Owner" in p_tag.text or "Tampa" in p_tag.text:

                            tag_address = p_tag.text.replace(
                                '\xa0', "").replace('\n', " \ ").split(' \ ')
                            # print(len(tag_address))
                            # print(tag_address)
                            # print("~~~~~~~")

                            if len(tag_address) == 3:
                                location_name = "".join(tag_address[0].strip())
                                street_address = "".join(
                                    tag_address[1].strip())
                                city = "".join(
                                    tag_address[-1]).split(',')[0]
                                state = "".join(
                                    tag_address[-1]).split(',')[-1].split()[0]
                                zip = "".join(
                                    tag_address[-1]).split(',')[-1].split()[-1]
                                phone = "<MISSING>"
                                # print(location_name + " \ " + street_address +
                                #       " \ " + city + " \ " + state + " \ " + zip)
                            if len(tag_address) == 5:
                                location_name = "".join(tag_address[0].strip())
                                city = "".join(tag_address[1]).split(
                                    ',')[-2].strip()
                                state = "".join(tag_address[1]).split(
                                    ',')[-1].split()[0]
                                zip = "".join(tag_address[1]).split(
                                    ',')[-1].split()[-1]
                                street1 = "".join(
                                    tag_address[1].split(',')[:-2])
                                street2 = "".join(tag_address[-3])
                                street_address = street1 + " " + street2
                            if len(tag_address) == 7:
                                location_name = "".join(tag_address[0].strip())
                                city = "".join(
                                    tag_address[2]).split(',')[-2].strip()

                                state = "".join(
                                    tag_address[2]).split(',')[-1].split()[0]
                                zip = "".join(
                                    tag_address[2]).split(',')[-1].split()[-1]
                                street1 = "".join(
                                    tag_address[1])
                                street2 = " ".join(tag_address[3:-2])
                                street_address = street1 + " " + street2
                            if len(tag_address) == 1 or len(tag_address) == 4 or len(tag_address) == 6:
                                for br in p_tag.find_all('br'):
                                    br.replace_with(" \\ ")
                                tag_address = p_tag.text.replace(
                                    '\xa0', "").replace("\n", "").split(' \\ ')
                                if len(tag_address) == 7:
                                    location_name = " ".join(tag_address[:-5])
                                    # print(location_name)
                                    city = "".join(
                                        tag_address[4].split(",")[0])
                                    state = "".join(
                                        tag_address[4].split(",")[1].split()[0])
                                    zip = "".join(
                                        tag_address[4].split(",")[1].split()[-1])
                                    street_address = " ".join(
                                        tag_address[-5:-3])
                                if len(tag_address) == 6:

                                    location_name = "".join(tag_address[0:-5])
                                    if "VA" in "".join(tag_address[-3]) or "GA" in "".join(tag_address[-3]):
                                        city = "".join(
                                            tag_address[-3].split(",")[0])
                                        state = "".join(
                                            tag_address[-3].split(",")[1].split()[0])
                                        zip = "".join(
                                            tag_address[-3].split(",")[1].split()[-1])
                                        street_address = " ".join(
                                            tag_address[1:3])
                                    if "FL" in "".join(tag_address[-4]):
                                        city = "".join(
                                            tag_address[-4].split(',')[0])
                                        state = "".join(
                                            tag_address[-4].split(',')[1].split()[0])
                                        zip = "".join(
                                            tag_address[-4].split(',')[1].split()[-1])
                                        street1 = "".join(tag_address[1])
                                        street2 = "".join(tag_address[3])
                                        street_address = street1 + " " + street2
                                        # print(location_name + " \ " + street_address +
                                        #       " \ " + city + " \ " + state + " \ " + zip)

                                    if "KY" in "".join(tag_address[-2]):
                                        city = "".join(
                                            tag_address[-2].split(',')[0])
                                        state = "".join(
                                            tag_address[-2].split(',')[1].split()[0])
                                        zip = "".join(
                                            tag_address[-2].split(',')[1].split()[-1])
                                        street_address = " ".join(
                                            tag_address[-4:-2])
                                if len(tag_address) == 5:
                                    location_name = "".join(tag_address[0])
                                    if "TX" in "".join(tag_address[2]):
                                        city = "".join(tag_address[2]).split(
                                            ',')[-2].strip()
                                        state = "".join(tag_address[2]).split(
                                            ',')[-1].split()[0]
                                        zip = "".join(tag_address[2]).split(
                                            ',')[-1].split()[-1]
                                        street_address = "".join(
                                            tag_address[1])
                                    if "GA" in "".join(tag_address[1]):
                                        city = "".join(
                                            tag_address[1].split(',')[1])
                                        state = "".join(
                                            tag_address[1].split(',')[2].split()[0])
                                        zip = "".join(
                                            tag_address[1].split(',')[2].split()[-1])
                                        street1 = "".join(
                                            tag_address[1].split(',')[0])
                                        street2 = "".join(
                                            tag_address[2].strip())
                                        street_address = street1 + " " + street2
                                if len(tag_address) == 4:

                                    if "NE" in "".join(tag_address[0]):

                                        location_name = p_tag.find_previous_sibling(
                                            'p').text
                                        city = "".join(
                                            tag_address[1].split(',')[0].strip())
                                        state = "".join(tag_address[1].split(',')[
                                                        1].split()[0].strip())
                                        zip = "".join(tag_address[1].split(',')[
                                                       1].split()[-1].strip())
                                        street_address = "".join(
                                            tag_address[0].strip())
                                    if "NE" not in "".join(tag_address[0]):
                                        location_name = "".join(
                                            tag_address[0].strip())
                                        city = "".join(
                                            tag_address[1].split(',')[-2].strip())
                                        state = "".join(
                                            tag_address[1].split(',')[-1].split()[0])
                                        zip = "".join(
                                            tag_address[1].split(',')[-1].split()[-1])
                                        street_address = " ".join(
                                            tag_address[1].split(',')[:-2])
                            # print(location_name + " \ " + street_address +
                            #       " \ " + city + " \ " + state + " \ " + zip)

                        if "Owner" in p_tag.text or "Tampa" in p_tag.text:
                            # print(p_tag)
                            # print(p_tag.find_next_sibling('p').text)
                            tag_phone = p_tag.find_next_sibling('p')
                            if tag_phone is None:
                                phone = "<MISSING>"
                            if tag_phone is not None:
                                for br in tag_phone.find_all('br'):
                                    br.replace_with(" \\ ")
                                # print(tag_phone.text)
                                tag_p = tag_phone.text.replace(
                                    '\xa0', "").replace("\n", "").split(' \\ ')
                                if tag_p == ['']:
                                    phone = "<MISSING>"
                                    # print(phone)
                                else:
                                    phone = "".join(tag_p[0])
                            store = [locator_domain, location_name, street_address, city, state, zip, country_code,
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
