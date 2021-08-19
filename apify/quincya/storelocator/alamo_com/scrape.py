import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgselenium import SgChrome


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

    base_links = [
        "https://www.alamo.com/en/car-rental-locations/us.model.json",
        "https://www.alamo.com/en/car-rental-locations/ca.model.json",
    ]

    data = []

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    driver = SgChrome(user_agent=user_agent).driver()

    session = SgRequests()

    for base_link in base_links:
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locator_domain = "alamo.com"

        raw = json.loads(base.text)
        stores = raw[":items"]["root"][":items"]["container_10"][":items"][
            "branch_locations_dra"
        ]["locations"]

        for store in stores:
            location_name = store["name"]
            street_address = (
                " ".join(store["addressLines"])
                .replace("NO CRUISE SHIP PICK UP", "")
                .replace("Williamsport Regional Airport", "")
                .replace("Ronald Reagan Wash Natl Airprt", "")
                .replace("Luis Munoz Marin Intl Airport", "")
                .replace("Vancouver Intl Airport", "")
                .replace("(hfx Airport)", "")
                .strip()
            )
            city = store["city"]
            state = store["countrySubdivisionCode"]
            country_code = store["countryCode"]
            store_number = store["groupBranchNumber"]
            location_type = store["locationType"]
            latitude = store["latitude"]
            longitude = store["longitude"]

            link = (
                "https://www.alamo.com/en/car-rental-locations"
                + store["url"].split("car-rental-locations")[1]
            )
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            script = base.find("script", attrs={"id": "mainschema"}).contents[0]
            store_js = json.loads(script)

            zip_code = store_js["address"]["postalCode"]
            phone = store_js["telephone"]
            hours_of_operation = store_js["openingHours"]
            if not hours_of_operation:
                driver.get(link)
                base = BeautifulSoup(driver.page_source, "lxml")
                try:
                    hours_of_operation = " ".join(
                        list(
                            base.find(
                                class_="map-location-detail-tile-expanded-state__location-hours-container map-location-detail-tile-expanded-state__location-hours-container--on-branch-page"
                            ).stripped_strings
                        )[1:]
                    )
                    if not hours_of_operation:
                        hours_of_operation = "<MISSING>"
                except:
                    hours_of_operation = "<MISSING>"

            if hours_of_operation == "MO,TU,WE,TH,FR,SA,SU":
                hours_of_operation = hours_of_operation + " 24 hours"

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
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
