import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "locale": "en_GB",
}

logger = SgLogSetup().get_logger("cadillac_co_uk")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    cities = [
        "Edinburgh",
        "Aberdeen",
        "Belfast",
        "Manchester",
        "Liverpool",
        "London",
        "Plymouth",
    ]
    ids = []
    for cname in cities:
        logger.info(cname)
        try:
            url = (
                "https://www.cadillac.co.uk/OCRestServices/dealer/city/v1/Cadillac/"
                + cname
                + "?distance=50000&maxResults=5000"
            )
            r = session.get(url, headers=headers)
            website = "cadillac.co.uk"
            typ = "<MISSING>"
            country = "GB"
            loc = "<MISSING>"
            store = "<MISSING>"
            hours = "<MISSING>"
            lat = "<MISSING>"
            lng = "<MISSING>"
            logger.info("Pulling Stores")
            for item in json.loads(r.content)["payload"]["dealers"]:
                name = item["dealerName"]
                try:
                    phone = item["phone1"]
                except:
                    phone = "<MISSING>"
                loc = item["dealerUrl"]
                lat = item["geolocation"]["latitude"]
                lng = item["geolocation"]["longitude"]
                add = item["address"]["addressLine1"]
                zc = item["address"]["postalCode"]
                city = item["address"]["cityName"]
                try:
                    state = item["address"]["countrySubdivisionCode"]
                except:
                    state = "<MISSING>"

                store = item["id"]
                zc = zc.replace("Cheshire", "").strip()
                if store not in ids:
                    ids.append(store)
                    yield [
                        website,
                        loc,
                        name,
                        add,
                        city,
                        state,
                        zc,
                        country,
                        store,
                        phone,
                        typ,
                        lat,
                        lng,
                        hours,
                    ]
        except Exception:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
