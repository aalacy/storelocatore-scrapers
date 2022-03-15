import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import lxml.html

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

    all_stores = session.get(
        "https://www.abercrombie.com/shop/ViewAllStoresDisplayView?storeId=11203&catalogId=10901&langId=-1",
        headers=headers,
    )
    all_stores_sel = lxml.html.fromstring(all_stores.text)
    links = all_stores_sel.xpath('//li[@class="view-all-stores__store"]/a/@href')

    countries = []
    for link in links:
        countries.append(
            link.strip()
            .split("/shop/us/clothing-stores/")[1]
            .strip()
            .split("/")[0]
            .strip()
        )

    countries = list(set(countries))

    for country in countries:
        logger.info(f"fetching data for country: {country}")
        url = "https://www.abercrombie.com/api/ecomm/a-wd/storelocator/search?country={}&radius=10000".format(
            country
        )
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
            types = location["physicalStoreAttribute"]
            location_type = ""
            for typ in types:
                if typ["name"] == "Brand":
                    location_type = typ["value"]
                    break

            location_type = location_type.replace(
                "ACF", "abercrombie and fitch"
            ).replace("KID", "abercrombie and fitch Kids")
            store_number = location["storeNumber"]
            location_name = location_type
            city = location["city"]
            state = location["stateOrProvinceName"]
            zipp = location["postalCode"]
            country_code = location["country"]
            if country_code == "GB":
                state = "<MISSING>"

                page_url = (
                    "https://www.abercrombie.com/shop/wd/clothing-stores/"
                    + country
                    + "/"
                    + "".join(city.split())
                    + "/"
                    + country
                    + "/"
                    + store_number
                )
            else:
                page_url = (
                    "https://www.abercrombie.com/shop/wd/clothing-stores/US/"
                    + "".join(city.split())
                    + "/"
                    + state
                    + "/"
                    + store_number
                )
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
