import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("newlook_ca")


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


def fetch_data():
    locator_domain = "https://www.newlook.ca/"
    ext = "en/stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locs = base.find_all(class_="succursale-card-actions")
    link_list = []
    for loc in locs:
        link_list.append(loc.a["href"])

    all_store_data = []
    for i, link in enumerate(link_list):
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        logger.info(link)
        cont = list(base.find(class_="card-info").stripped_strings)

        location_name = cont[0]

        street_address = cont[1]

        off = 0

        if ")" not in cont[2]:
            off += 1

        city_state = cont[off + 2].split("(")
        city = city_state[0].strip()
        state = city_state[1].replace(")", "").strip()

        zip_code = cont[off + 3]

        phone_number = cont[off + 4].replace("T", "").strip()

        hours = " ".join(list(base.find(class_="working-hours-list").stripped_strings))

        lat = "<MISSING>"
        longit = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        country_code = "CA"

        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            link,
        ]
        all_store_data.append(store_data)
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
