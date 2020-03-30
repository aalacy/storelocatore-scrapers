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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.tomjames.com"
    r = session.get("https://www.tomjames.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    usa_part = BeautifulSoup(soup.find(
        "div", {"class": "white-section center"}).prettify().split("<h4")[2], "lxml")
    locator_domain = "https://www.tomjames.com"
    store_number = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"
    for location in usa_part.find_all("a"):
        # print(location["href"])
        page_url = location["href"].strip()
        #print(page_url)
        location_request = session.get(
            location["href"].strip(), headers=headers)
        location_soup = BeautifulSoup(location_request.text, "lxml")
        try:
            iframe = location_soup.find('iframe')['src']
            r_coord = session.get(iframe, headers=headers)
            soup_coord = BeautifulSoup(r_coord.text, 'lxml')
            script = soup_coord.find(lambda tag: (
                tag.name == "script") and "initEmbed" in tag.text)
            sc_string = script.text.split(
                'initEmbed(')[1].split(');')[0].split(',')[61:64]
            if "null" in " ".join(sc_string):
                sc_string.remove("null")
            latitude = sc_string[0]
            longitude = sc_string[1].replace(']', '').strip()
            # print ([list((i, sc_string[i])) for i in range(len(sc_string))])
            # print(latitude, longitude)
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        country_code = "US"

        location_name = location_soup.find("h1").text
        if location_name == "Our Apologies":
            continue
        address = list(location_soup.find(
            "span", {"itemprop": "address"}).stripped_strings)
        street_address = " ".join(address[:-1])
        city = address[-1].split(",")[0]
        state = address[-1].split(",")[-1].split(" ")[-2]
        zipp = address[-1].split(",")[-1].split(" ")[-1]
        if "972015848" == zipp or "212081393" == zipp:
            zipp = "".join(zipp[:5]) + "-" + "".join(zipp[5:])
            #print(zipp)
        phone = location_soup.find("span", {"itemprop": "telephone"}).text
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        # if x == "":
        #     store = "<MISSING>"
        # else:
        #     x for x in store
        store = ["<MISSING>" if x == "" else x for x in store]

        # print("data == " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)
    for location in soup.find_all("div", {"class": "button-link-white white middle"}):
        if "Canada" in location.find("h6").text:
            location_request = session.get(
                location.find("a")["href"].strip(), headers=headers)
            location_soup = BeautifulSoup(location_request.text, "lxml")
            try:
                iframe = location_soup.find('iframe')['src']
                r_coord = session.get(iframe, headers=headers)
                soup_coord = BeautifulSoup(r_coord.text, 'lxml')
                script = soup_coord.find(lambda tag: (
                    tag.name == "script") and "initEmbed" in tag.text)
                sc_string = script.text.split(
                    'initEmbed(')[1].split(');')[0].split(',')[61:64]
                if "null" in " ".join(sc_string):
                    sc_string.remove("null")
                latitude = sc_string[0]
                longitude = sc_string[1].replace(']', '').strip()
                # print ([list((i, sc_string[i])) for i in range(len(sc_string))])
                # print(latitude, longitude)
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            location_name = location_soup.find("h1").text
            if location_name == "Our Apologies":
                continue
            country_code = "CA"
            address = list(location_soup.find(
                "span", {"itemprop": "address"}).stripped_strings)
            phone = location_soup.find("span", {"itemprop": "telephone"}).text
            street_address = " ".join(address[:-1])
            city = address[-1].split(",")[0]
            state = address[-1].split(",")[-1].split(" ")[1]
            zipp = " ".join(address[-1].split(",")[-1].split(" ")[2:])
            page_url = location.find("a")["href"].strip()
            # print(page_url)

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            # if x == "":
            #     store = "<MISSING>"
            # else:
            #     x for x in store
            store = ["<MISSING>" if x == "" else x for x in store]

            # print("data == " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
