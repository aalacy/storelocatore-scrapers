from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
import re

def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # store data
    locations_titles = []
    urls = []
    location_id = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    hours = []
    longitude_list = []
    latitude_list = []
    data = []

    COMPANY_URL = "beggarspizza.com"
    store_url = "https://www.beggarspizza.com/wp-admin/admin-ajax.php?action=store_search&lat=41.878114&lng=-87.629798&max_results=25&search_radius=1000&autoload=1"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    req = session.get(store_url, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    locations = json.loads(base.text)

    for location in locations:
        # ID
        location_id.append(location["id"])

        # Title
        locations_titles.append(location["store"].replace("–","-"))

        # Street address
        street_addresses.append(location["address"] + " " + location["address2"])

        # City
        cities.append(location["city"])

        # State
        states.append(location["state"])

        # Phone
        phone_numbers.append(location["phone"])

        # Zip
        zip_code = location["zip"]
        if zip_code == "40409":
            zip_code = "46409"
        zip_codes.append(zip_code)

        # Latitude
        latitude_list.append(location["lat"])

        # Longitude
        longitude_list.append(location["lng"])

        link = location["url"]
        urls.append(link)

        # Hour
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        raw_hours = base.find(class_="col-sm-12 reset-left").find(class_="col-xs-6 smallWide reset-left").text.replace("–","-").replace("<"," ").strip().split("\n")
        fin_hours = ""
        for raw_hour in raw_hours:
            if "day" in raw_hour.lower() or "am " in raw_hour.lower() or "pm " in raw_hour.lower():
                fin_hours = fin_hours + " " + raw_hour
        fin_hours = (re.sub(' +', ' ', fin_hours)).strip()
        if " LA" in fin_hours:
            fin_hours = fin_hours[:fin_hours.find(" LA")].strip()
        hours.append(fin_hours)

    for (
        locations_title,
        url,
        street_address,
        city,
        state,
        zipcode,
        phone_number,
        latitude,
        longitude,
        hour,
        id,
    ) in zip(
        locations_titles,
        urls,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
        hours,
        location_id,
    ):
        data.append(
            [
                COMPANY_URL,
                url,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                "US",
                id,
                phone_number,
                "<MISSING>",
                latitude,
                longitude,
                hour,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
