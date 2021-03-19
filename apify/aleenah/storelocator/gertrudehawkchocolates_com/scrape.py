import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("gertrudehawkchocolates_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()
all = []


def fetch_data():
    # Your scraper here

    res = session.get("https://gertrudehawkchocolates.com/find_a_store")
    soup = BeautifulSoup(res.text, "html.parser")
    stores = soup.find_all("div", {"name": "leftLocation"})
    logger.info(len(stores))

    jso = json.loads(re.findall(r'"items":(\[[^]]+\])', str(soup))[0])

    for store in stores:
        id = store.get("data-amid")
        loc = store.find("div", {"class": "amlocator-title"}).text.strip()
        phones = re.findall(r"[\d\-]{10,}", store.text)
        phone = phones[-1]
        data = (
            str(store.find("div", {"class": "amlocator-store-information"}))
            .replace(phone, "")
            .split("Distance")[0]
            .strip()
        )

        data = re.findall(
            r'<div class="amlocator-title">[ a-zA-Z]*</div>(.*)<br/>(.*)<br/>', data
        )[0]
        street = data[0].strip()
        csz = data[1].strip().split(",")
        city = csz[0]
        csz = csz[1]
        zip = re.findall(r"[\d\-]+", csz)[0].strip()
        state = csz.replace(zip, "").strip()
        if len(zip) == 4:
            zip = "0" + zip
        days = store.find_all("span", {"class": "amlocator-cell -day"})
        hours = store.find_all("span", {"class": "amlocator-cell -time"})

        tim = ""
        for i in range(len(days)):
            tim += days[i].text + ": " + hours[i].text + ", "

        tim = tim.strip(", ")
        lat = jso[stores.index(store)]["lat"]
        long = jso[stores.index(store)]["lng"]

        all.append(
            [
                "https://gertrudehawkchocolates.com",
                loc,
                street,
                city,
                state.strip(),
                zip,
                "US",
                id,  # store #
                phone,  # phone
                "<MISSING>",  # type
                lat,  # lat
                long,  # long
                tim,  # timing
                "https://gertrudehawkchocolates.com/find_a_store",
            ]
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
