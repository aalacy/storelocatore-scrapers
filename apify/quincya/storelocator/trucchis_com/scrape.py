import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_link = "https://www.trucchis.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    data = []

    items = base.find(class_="site-nav").find_all(class_="dropdown")[-2].find_all("a")
    locator_domain = "trucchis.com"

    for i, item in enumerate(items):
        link = base_link + item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = "Trucchi's " + base.h1.text
        raw_address = (
            base.find(class_="collection-container")
            .find_all("p")[2]
            .text.replace("Address", "")
            .replace("Street Taunton", "Street, Taunton")
            .replace("Street West", "Street, West")
            .split(",")
        )

        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[2].split()[0].strip()
        zip_code = raw_address[2].split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = (
            base.find(class_="collection-container")
            .find_all("p")[1]
            .text.replace("Phone", "")
        )
        hours_of_operation = " ".join(
            list(base.find(class_="collection-container").p.stripped_strings)
        ).replace("Store Hours", "").strip()

        locs = base.find(class_="list-of-locations").find_all(
            "a", string="Map & Directions"
        )
        map_link = locs[i]["href"]
        req = session.get(map_link, headers=headers)

        try:
            raw_gps = req.url
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", raw_gps)[0].split(
                ","
            )
            latitude = geo[0]
            longitude = geo[1]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
