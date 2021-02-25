import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("abercrombie_com")


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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


session = SgRequests()


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "Accept": "application/json",
    }

    base_url = "https://www.abercrombie.com"

    urls_list = [
        "https://www.abercrombie.com/api/ecomm/a-wd/storelocator/search?country=US&radius=10000",
        "https://www.abercrombie.com/api/ecomm/a-wd/storelocator/search?country=CA&radius=10000",
        "https://www.abercrombie.com/api/ecomm/a-wd/storelocator/search?country=GB&radius=10000",
    ]

    for url in urls_list:
        r = session.get(url, timeout=(30, 30), headers=headers)
        json_data = r.json()

        # it will used in store data.
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = ""
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        hours_of_operation = ""
        page_url = ""

        for location in json_data["physicalStores"]:
            location_type = (
                location["physicalStoreAttribute"][7]["value"]
                .replace("ACF", "abercrombie and fitch")
                .replace("KID", "abercrombie and fitch Kids")
            )
            store_number = location["storeNumber"]
            location_name = location_type
            city = location["city"]
            state = location["stateOrProvinceName"]
            zipp = location["postalCode"]
            country_code = location["country"]
            latitude = str(location["latitude"])
            longitude = str(location["longitude"])
            phone = location["telephone"]
            street_address = ", ".join(location["addressLine"])

            hours_of_operation = ""
            index = 0
            days = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            for time_period in location["physicalStoreAttribute"][-1]["value"].split(
                ","
            ):
                hours_of_operation += (
                    days[index] + " " + time_period.replace("|", " - ") + " "
                )
                index += 1
            page_url = (
                "https://www.abercrombie.com/shop/wd/clothing-stores/US/"
                + "".join(city.split())
                + "/"
                + state
                + "/"
                + store_number
            )
            store = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zipp,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
                page_url,
            ]

            store = [
                x.encode("ascii", "ignore").decode("ascii").strip()
                if x
                else "<MISSING>"
                for x in store
            ]

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
