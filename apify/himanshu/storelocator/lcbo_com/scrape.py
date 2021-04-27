import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import sgzip
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("lcbo_com")


session = SgRequests()


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


def fetch_data():
    addresses = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    base_url = "https://www.lcbo.com"
    r_store_id = session.get(base_url, headers=headers)
    store_id = r_store_id.text.split('"storeId":\'')[1].split("'")[0]

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], max_search_results=50
    )

    for zip_code in search:
        logger.info(f"{zip_code} | remaining: {search.items_remaining()}")

        data = "citypostalcode=" + str(zip_code)
        location_url = (
            "https://www.lcbo.com/webapp/wcs/stores/servlet/AjaxStoreLocatorResultsView?storeId="
            + str(store_id)
        )

        while True:
            try:
                r = session.post(location_url, headers=headers, data=data)
                break
            except Exception as e:
                time.sleep(10)
                continue

        soup = BeautifulSoup(r.text, "lxml")

        for script in soup.find_all("div", {"class": "row store-row"}):

            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = "US"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            raw_address = ""
            page_url = ""
            hours_of_operation = ""

            # do your logic here

            store_number = script["data-store-num"]
            street_address = script["data-address"]
            city = script["data-city"]
            latitude = script["data-lat"]
            longitude = script["data-long"]
            location_name = script.find("div", {"class": "store-name"}).text.strip()
            phone = script.find("div", {"class": "store-phone"}).text.strip()
            zipp = script.find("div", {"class": "store-postal"}).text.strip()
            hours_json_str = (
                "[{"
                + script.find("button", {"class": "md-mt-10 storehourslink"})["onclick"]
                .split("[{")[1]
                .split("}]")[0]
                + "}]"
            )
            hours_json = json.loads(hours_json_str)

            if zipp.isdigit():
                country_code = "US"
            else:
                zipp = zipp[:3] + " " + zipp[3:]
                country_code = "CA"

            hours_of_operation = ""
            index = 1
            for hours_day in hours_json:
                hours_of_operation += hours_day[str(index)][0] + " "
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

            if str(store[2]) not in addresses:
                addresses.append(str(store[2]))

                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
