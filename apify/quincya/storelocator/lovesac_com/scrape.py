import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("lovesac.com")


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

    base_link = "https://www.lovesac.com/showroomlocator/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="amlocator-store-desc")
    locator_domain = "lovesac.com"

    for item in items:

        location_name = item.a.text.strip()
        if "coming soon" in location_name.lower():
            continue
        if "coming_soon" in str(item).lower():
            continue

        link = item.a["href"].replace("&apos;s-herald-square", "'s-herald-square")
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        logger.info(link)

        raw_address = list(
            base.find(class_="amlocator-block amlocator-location-info").stripped_strings
        )

        street_address = raw_address[9].strip()
        city = raw_address[7].strip()
        state = raw_address[5].strip()
        zip_code = raw_address[1].strip()
        country_code = raw_address[3].strip()
        store_number = item["data-amid"]
        location_type = "<MISSING>"
        phone = base.find(class_="amlocator-link").text.strip()
        if len(phone) > 20:
            phone = base.find_all(class_="amlocator-link")[1].text.strip()

        if "temporarily closed" in base.h1.text.lower():
            hours_of_operation = "Temporarily Closed"
        else:
            try:
                hours_of_operation = " ".join(
                    list(base.find(class_="amlocator-schedule-table").stripped_strings)
                )
            except:
                hours_of_operation = "<MISSING>"

        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "lat:" in str(script):
                script = str(script)
                break
        latitude = re.findall(r"lat: [0-9]{2}\.[0-9]+", script)[0].split(":")[1].strip()
        longitude = (
            re.findall(r"lng: -[0-9]{2,3}\.[0-9]+", script)[0].split(":")[1].strip()
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
