import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

log = SgLogSetup().get_logger("westaroilcompany.net")


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

    base_link = "http://www.westaroilcompany.net/index.php/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    items = base.find(id="sidebar").ul.find_all("li")
    locator_domain = "westaroilcompany.net"

    for item in items:
        link = "http://www.westaroilcompany.net" + item.a["href"]
        log.info(link)

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = "<MISSING>"
        raw_address = (
            base.title.text.replace("S. ", "S ")
            .replace("N. ", "N ")
            .replace("W. ", "W ")
            .replace("Miami Fl", "Miami, Fl")
            .replace("Way Coral", "Way. Coral")
            .replace("St Miami", "St. Miami")
            .replace("Street Miami", "Street. Miami")
            .replace("FL3", "FL 3")
            .split(",")
        )
        street_address = raw_address[0].split(".")[0].strip()
        city = raw_address[0].replace(street_address, "")[1:].strip()
        state = raw_address[-1].strip()[:-6].strip().upper()
        zip_code = raw_address[-1][-6:].replace("330155", "33155").strip()
        country_code = "US"
        store_number = item["class"][0].split("-")[-1]
        location_type = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"

        map_link = base.iframe["src"]
        try:
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_link)[
                -1
            ].split(",")
            latitude = geo[0]
            longitude = geo[1]
        except:
            try:
                req = session.get(map_link, headers=headers)
                map_str = str(BeautifulSoup(req.text, "lxml"))
                geo = (
                    re.findall(r"\[[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]", map_str)[0]
                    .replace("[", "")
                    .replace("]", "")
                    .split(",")
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
