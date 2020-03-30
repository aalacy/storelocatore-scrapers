import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import pandas as pd



session = SgRequests()

def write_output(data):
    with open('data.csv', 'w')as output_file:
        writer = csv.writer(output_file, delimiter=',')
        # header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # body
        for row in data or []:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://kruseandmuerrestaurants.com"
    r = session.get(
        "https://kruseandmuerrestaurants.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    return_main_object = []

    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "kruseandmuerrestaurants"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for val in soup.find('div', class_="locations-wrap").find_all('div', class_="team-content"):
        tag_link = val.find('a')['href']
        r_location = session.get(base_url + tag_link, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")
        location_name = soup_location.find(
            'h1', class_="single-post-title").text
        details = soup_location.find('div', class_="post-content")
        tag_address = details.find(
            lambda tag: (tag.name == "address")).text
        tag_address = re.sub("[\t ]+", " ", tag_address).split('\n')
        tag_address.remove(tag_address[0])
        tag_address.remove(tag_address[2])
        street_address = "".join(tag_address[0].strip())
        c = " ".join(tag_address[1].split()[:-2])
        city = c.split(',')[0]
        state = "".join(tag_address[1].split()[-2])
        zipp = "".join(tag_address[1].split()[-1])

        phone = details.find(lambda tag: (
            tag.name == "p")).text.split(":")[1].strip()

        hours = details.find('div', class_="entry").find('table')
        if hours is not None:
            hours_of_operation = "".join(hours.text.strip().replace("\n", " ").replace(
                "\xa0", "").split("Click Here for Holiday Hours"))

        if hours is None:
            for hours in details.find('div', class_="entry").find_all(
                    lambda tag: (tag.name == "p") and ("Lunch Hours:" in tag.text.strip())):
                launch_hours = "".join(
                    hours.text.strip().replace("\n", " "))
            for hours in details.find('div', class_="entry").find_all(
                    lambda tag: (tag.name == "p") and ("Dinner Hours:" in tag.text.strip())):
                dinner_hours = "".join(
                    hours.text.strip().replace("\n", " "))
            hours_of_operation = launch_hours + " " + dinner_hours

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        store = ["<MISSING>" if x == "" else x for x in store]
        return_main_object.append(store)
        print("data = " + str(store))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
