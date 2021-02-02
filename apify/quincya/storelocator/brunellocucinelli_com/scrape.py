import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []
    found_poi = []
    locator_domain = "brunellocucinelli.com"

    country_codes = ["US", "CA", "GB"]

    for country_code in country_codes:
        base_link = (
            "https://shop.brunellocucinelli.com/on/demandware.store/Sites-bc-us-Site/en_US/Stores-findBoutiques?countryCode="
            + country_code
        )

        stores = session.get(base_link, headers=headers).json()["filterList"]

        for store in stores:
            location_name = store["name"]
            link = "https://shop.brunellocucinelli.com" + store["url"]
            if "SingleBoutique" in link:
                continue
            street_address = store["address1"].replace(", Boston, MA", "").strip()
            if street_address in found_poi:
                continue
            found_poi.append(street_address)
            city = store["city"]
            state = store["stateCode"]
            zip_code = store["postalCode"]
            store_number = store["ID"]
            location_type = "<MISSING>"
            phone = store["phone"]
            latitude = store["markers"]["lat"]
            longitude = store["markers"]["long"]
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = " ".join(
                list(base.find(class_="cc-container-day-info").stripped_strings)
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
