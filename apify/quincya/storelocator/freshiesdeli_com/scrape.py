import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("freshiesdeli_com")


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

    base_link = "https://freshiesdeli.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    all_links = []
    data = []

    req = session.get(base_link, headers=headers)
    base = str(BeautifulSoup(req.text, "lxml"))

    all_links = re.findall(r"https://www.freshiesdeli.com/storelocations/[a-z]+", base)
    geos = re.findall(r"LatLng\([0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\);", base)[1:]
    for i, link in enumerate(all_links):
        logger.info(link)

        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")

        locator_domain = "freshiesdeli.com"

        location_name = item.find("meta", attrs={"property": "og:title"})[
            "content"
        ].replace("—", "-")
        if (
            location_name == "Freshies Deli"
            and link == "https://www.freshiesdeli.com/storelocations/machiasfreshies"
        ):
            link = "https://freshiesdeli.com/storelocations/machaisfreshies"
            req = session.get(link, headers=headers)
            item = BeautifulSoup(req.text, "lxml")
            location_name = item.find("meta", attrs={"property": "og:title"})[
                "content"
            ].replace("—", "-")

        logger.info(location_name)

        phone = item.find("meta", attrs={"itemprop": "description"})["content"][
            -15:
        ].strip()
        if "(" not in phone:
            phone = item.find("meta", attrs={"itemprop": "description"})["content"][
                3:18
            ].strip()
            raw_address = (
                item.find("meta", attrs={"itemprop": "description"})["content"][20:]
                .replace("St ", "St. ")
                .replace("Trail ", "Trail. ")
                .replace("", "")
                .strip()
            )
        else:
            raw_address = (
                item.find("meta", attrs={"itemprop": "description"})["content"][3:-18]
                .replace("St ", "St. ")
                .replace("Trail ", "Trail. ")
                .replace("", "")
                .strip()
            )
        street_address = raw_address[: raw_address.find(".")]
        city = raw_address[raw_address.find(".") + 1 : raw_address.find(",")].strip()
        state = raw_address[-3:].strip()
        zip_code = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = ""
        raw_hours = item.find_all(class_="sqs-block-content")[3].find_all("tr")[1:]
        if not raw_hours:
            raw_hours = item.find_all(class_="sqs-block-content")[2].find_all("tr")[1:]
        for raw_hour in raw_hours:
            day = raw_hour.td.text
            hours = raw_hour.find_all("td")[2].text
            hours_of_operation = hours_of_operation + " " + day + " " + hours
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        latitude = geos[i].split("(")[1].split(",")[0]
        longitude = geos[i].split(",")[1][:-2]

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
