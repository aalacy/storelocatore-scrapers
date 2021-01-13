import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("buffaloexchange.com")


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

    base_link = "https://www.buffaloexchange.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find(id="locations_list").find_all("a")
    locator_domain = "buffaloexchange.com"

    for item in items:
        link = item["href"]
        logger.info(link)

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if "permanently closed" in base.text.lower():
            continue

        location_name = base.find(id="loc-details").h1.text.strip()
        if "Headquarters" in location_name:
            continue

        raw_address = (
            base.find(id="loc-details")
            .address.text.replace("The LAB,", "")
            .replace("WE MOVED!", "")
            .split(",")
        )
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = " ".join(raw_address[2].split()[:-1])
        try:
            zip_code = raw_address[2].split()[-1]
            if not zip_code.isdigit():
                zip_code = "<MISSING>"
        except:
            zip_code = "<MISSING>"
        country_code = "US"
        store_number = base.article["id"].split("-")[1]
        location_type = "<MISSING>"
        phone = base.find(class_="tel").text.strip()
        hours_of_operation = (
            base.find(id="loc-details")
            .find_all("p")[2]
            .text.replace("Store Hours:", "")
            .replace("\xa0", "")
        )

        map_link = base.iframe["src"]
        req = session.get(map_link, headers=headers)
        map_str = BeautifulSoup(req.text, "lxml")
        geo = (
            re.findall(r"\[[0-9]{2,3}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]", str(map_str))[0]
            .replace("[", "")
            .replace("]", "")
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]

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
