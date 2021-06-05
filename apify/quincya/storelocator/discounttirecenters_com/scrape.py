import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("discounttirecenters_com")


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

    base_link = "https://www.discounttirecenters.com/location-detail"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    main_links = []
    main_items = base.find(id="dm_content").find_all("a")
    for main_item in main_items:
        main_link = "https://www.discounttirecenters.com" + main_item["href"]
        main_links.append(main_link)

    for link in main_links:
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locator_domain = "discounttirecenters.com"

        if "COMING SOON" in base.find(id="dm_content").text.upper():
            continue

        location_name = " ".join(list(base.h1.stripped_strings))
        base.find("h4", attrs={"data-uialign": "center"})
        raw_data = list(
            base.find_all("h4", attrs={"data-uialign": "center"})[-1].stripped_strings
        )

        city = location_name.split(" in")[1].split(",")[0].strip()
        state = location_name.split(" in")[1].split(",")[1].strip()
        street_address = raw_data[0].split(city + ",")[0].strip()

        if state in raw_data[0]:
            zip_code = raw_data[0].split(state)[-1].strip()
        elif state in raw_data[1]:
            zip_code = raw_data[1].split(state)[-1].strip()
        else:
            zip_code = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = raw_data[-2]

        geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(base))[0].split(
            ","
        )
        latitude = geo[0]
        longitude = geo[1]

        try:
            hours_of_operation = " ".join(list(base.find(id="main").stripped_strings))
        except:
            hours_of_operation = "<MISSING>"

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
