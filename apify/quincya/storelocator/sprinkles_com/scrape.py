import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("sprinkles_com")


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

    base_link = "https://sprinkles.com/pages/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.main.find_all(class_="item")

    data = []
    for item in items:
        locator_domain = "sprinkles.com"

        location_name = item.h3.text.strip()
        logger.info(location_name)

        raw_address = list(item.p.stripped_strings)
        street_address = " ".join(raw_address[:-2]).strip()
        if not street_address:
            street_address = "<MISSING>"
        city_line = raw_address[-2].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.find(class_="tel").text.strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        page_link = "https://sprinkles.com" + item.a["href"]
        page_req = session.get(page_link, headers=headers)
        page = BeautifulSoup(page_req.text, "lxml")

        hours_of_operation = ""
        raw_hours = page.find(class_="addr-hours")
        raw_hours = raw_hours.find_all("p")

        for hour in raw_hours:
            if "hours" in hour.text.lower():
                hours_of_operation = (
                    " ".join(list(hour.stripped_strings))
                    .split("hours:")[1]
                    .split("The hours above")[0]
                    .replace("The SIMON Fashion Valley Mall ATM is open", "")
                    .replace("Hollywood & Highland ATM is open", "")
                    .strip()
                )

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        data.append(
            [
                locator_domain,
                page_link,
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
