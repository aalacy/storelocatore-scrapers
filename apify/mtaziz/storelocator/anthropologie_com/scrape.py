from sglogging import SgLogSetup
from sgrequests import SgRequests
import csv
from lxml import html

logger = SgLogSetup().get_logger(logger_name="anthropologie_com")
session = SgRequests()

locator_domain_url = "https://www.anthropologie.com"
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}

MISSING = "<MISSING>"

FIELDS = [
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


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


def get_hoo(hours):
    dates_map = {
        "1": "Sunday",
        "2": "Monday",
        "3": "Tuesday",
        "4": "Wednesday",
        "5": "Thursday",
        "6": "Friday",
        "7": "Saturday",
    }
    hoo = []
    for key, value in hours.items():
        v = dates_map[key] + " " + value["open"] + " - " + value["close"]
        hoo.append(v)
    hoo = "; ".join(hoo)
    if hoo:
        return hoo
    else:
        return "<MISSING>"


def fetch_data():

    url_stores = "https://www.anthropologie.com/stores#?viewAll=true"
    r_page_url = session.get(url_stores, headers=headers)
    locations = html.fromstring(r_page_url.text, "lxml")

    url_api = "https://www.anthropologie.com/api/misl/v1/stores/search?brandId=54%7C04&distance=25&urbn_key=937e0cfc7d4749d6bb1ad0ac64fce4d5"
    data = session.get(url_api, headers=headers).json()
    items = []
    for d in data["results"]:
        country_code = d["country"]
        country_code_UK = "UK"
        country_code_CA = "CA"
        country_code_US = "US"
        if (
            country_code == country_code_UK
            or country_code == country_code_CA
            or country_code == country_code_US
        ):
            locator_domain = locator_domain_url
            location_name = d["addresses"]["marketing"]["name"]
            url_store = locations.xpath('//a[contains(., "%s")]/@href' % location_name)[
                0
            ]
            if url_store:
                page_url = "https://www.anthropologie.com" + url_store
            else:
                page_url = MISSING

            street_address = d["addressLineOne"] if d["addressLineOne"] else MISSING
            city = d["city"] if d["city"] else MISSING
            state = d["state"] if d["state"] else MISSING
            zip = d["zip"] if d["zip"] else MISSING
            country_code = d["country"] if d["country"] else MISSING
            store_number = d["storeNumber"] if d["storeNumber"] else MISSING
            try:
                phone = d["addresses"]["marketing"]["phoneNumber"]
            except KeyError:
                phone = "<MISSING>"

            try:
                location_type = d["storeType"]
            except KeyError:
                location_type = MISSING
            try:
                latitude = d["loc"][1]
            except:
                latitude = MISSING
            try:
                longitude = d["loc"][0]
            except:
                longitude = MISSING

            hours_of_operation = get_hoo(d["hours"])
            if (
                page_url == "https://www.anthropologie.com/stores"
                and street_address == MISSING
            ):
                continue
            else:
                if page_url == "https://www.anthropologie.com/stores":
                    page_url = MISSING

                row = [
                    locator_domain,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]

                items.append(row)
        else:
            continue
    return items


def scrape():
    logger.info("Scraping Started...")
    data = fetch_data()
    logger.info(f"Scraping Finished | Total Store Count: {len(data)}")
    write_output(data)


if __name__ == "__main__":
    scrape()
