import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    base_link = "https://www.boeingdistribution.com/aero/about-us/location/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    stores = base.find_all(class_="map-result")

    locator_domain = "boeingdistribution.com"
    data = []

    for i in stores:
        try:
            store = json.loads(i["data-custom"])
        except:
            continue
        if store["Filter 1"] == "Department":
            continue
        location_name = store["Title"]
        country_code = store["Title"].split("-")[0].strip()
        raw_address = list(BeautifulSoup(store["Address"], "lxml").stripped_strings)
        raw_text = BeautifulSoup(store["Address"], "lxml").text

        if country_code == raw_address[-1].strip():
            raw_address.pop(-1)

        city_line = raw_address[-1].split()
        if (country_code not in ["United States", "Canada"]) and "-" in store["Title"]:
            city = store["Title"].split("-")[1].strip()
            if city in raw_text:
                street_address = raw_text.split(city)[0].strip()
            else:
                city = city_line[0]
        else:
            street_address = " ".join(raw_address[:-1])
            city = city_line[0]
        try:
            state = city_line[1].replace(",", "")
        except:
            state = "<MISSING>"

        if country_code not in [
            "Canada",
            "Australia",
            "United States",
            "United Kingdom",
        ]:
            state = "<MISSING>"
        if country_code in ["Canada", "United Kingdom"]:
            zip_code = " ".join(city_line[-2:])
        elif country_code in ["Australia", "United States", "India", "Singapore"]:
            zip_code = city_line[-1].split(",")[0]
        else:
            zip_code = "<MISSING>"

        if city[:2].isdigit():
            street_address = street_address + " " + city
            city = city_line[1]

        city = city.replace(",", "")

        if street_address[-1:] == ",":
            street_address = street_address[:-1]

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["National Phone"]
        if not phone:
            phone = store["International Phone"]
        if not phone:
            phone = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]
        hours_of_operation = "<MISSING>"
        link = (
            "https://www.boeingdistribution.com/aero/about-us/location/#!/filter/location/contact/"
            + store["slug"]
        )

        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
