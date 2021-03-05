import csv
import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="redwing.com")


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "http://stores.redwing.com"
    req = session.get(locator_domain, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    log.info("Getting Countries ..")
    countries = base.find_all(class_="cities")
    country_list = []
    for c in countries:
        country_list.append(locator_domain + c["href"])

    state_list = []
    log.info("Getting States ..")
    for country in country_list:
        req = session.get(country, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        states = base.find_all(class_="cities")
        for s in states:
            state_list.append(locator_domain + s["href"])

    city_list = []
    log.info("Getting Cities ..")
    for state in state_list:
        req = session.get(state, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        cities = base.find_all(class_="cities")
        for c in cities:
            city_list.append(locator_domain + c["href"])

    location_list = []
    log.info("Getting Links ..")
    for city in city_list:
        req = session.get(city, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        store_links = base.find_all(class_="website pull-right")
        for link in store_links:
            location_list.append(locator_domain + link["href"])

    all_store_data = []
    log.info("Getting Data ..")
    for i, link in enumerate(location_list):
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            loc_j = base.find("script", attrs={"type": "application/ld+json"})
            loc_json = json.loads(loc_j.text.strip())
        except:
            continue

        location_name = loc_json["name"]

        phone_number = loc_json["telephone"]

        addy = loc_json["address"]

        street_address = addy["streetAddress"]
        city = addy["addressLocality"]
        state = addy["addressRegion"]
        zip_code = addy["postalCode"]
        if len(zip_code.split(" ")) == 2:
            country_code = "CA"
        else:
            country_code = "US"

        geo = loc_json["geo"]
        lat = geo["latitude"]
        longit = geo["longitude"]

        if "openingHours" in loc_json:
            hours_list = loc_json["openingHours"]
            hours = ""
            for h in hours_list:
                hours += h + " "
            hours = hours.strip()
        else:
            hours = "<MISSING>"

        location_type = "<MISSING>"
        store_number = "<MISSING>"

        store_data = [
            locator_domain,
            link,
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
        ]

        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
