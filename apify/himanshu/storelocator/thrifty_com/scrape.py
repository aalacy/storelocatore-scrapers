import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("thrifty_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    base_url = "https://www.thrifty.com/"
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_results=84,
        max_radius_miles=100,
    )
    for zip_code in search:
        logger.info(f"{zip_code} | remaining: {search.items_remaining()}")
        page_url = (
            "https://www.thrifty.com/loc/modules/multilocation/?near_location="
            + str(zip_code)
            + "&services__in=&published=1&within_business=true"
        )
        try:
            json_r = session.get(page_url, headers=headers).json()
        except:
            continue
        for data in json_r["objects"]:
            location_name = data["location_name"]
            street_address = data["street"]
            city = data["city"]
            state = data["state"]
            zipp = data["postal_code"]
            country_code = data["country"]
            if country_code not in ["CA", "US"]:
                continue
            phone = data["phonemap"]["phone"]
            latitude = data["lat"]
            longitude = data["lon"]
            page_url = data["location_url"]
            store_number = data["id"]
            hour = data["formatted_hours"]["primary"]["days"]
            HOO = ""
            for h in hour:
                HOO = HOO + " " + h["label"] + " " + h["content"] + " "
            location_type = "Thrifty"
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(HOO if HOO else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
