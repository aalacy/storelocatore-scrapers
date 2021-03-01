import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("jenis_com")


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

    base_link = "https://jenis.com/scoop-shops/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find(id="content").find_all("a")
    locator_domain = "jenis.com"

    for item in items:
        link = item["href"]
        if "http" not in link:
            continue
        logger.info(link)

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            location_name = base.h1.text.replace("’", "'").strip()
        except:
            continue

        raw_address = list(base.find(class_="content group").address.stripped_strings)
        if raw_address[2] == "60614":
            raw_address[1] = raw_address[1].replace("\r", " ") + raw_address[2]
            raw_address.pop(2)
        street_address = " ".join(raw_address[:-3]).replace("\r", "").strip()
        city_line = raw_address[-3].replace("IL60614", "IL 60614").strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = raw_address[-2].strip()

        hours_of_operation = base.find(class_="hours").text.replace("\n", " ").strip()
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

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
