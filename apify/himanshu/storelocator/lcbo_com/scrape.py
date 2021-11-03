import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup
from sgzip.static import static_zipcode_list, SearchableCountries

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

    search = static_zipcode_list(country_code=SearchableCountries.CANADA, radius=5)

    x = len(search)
    for zip_code in search:

        logger.info(f"{zip_code} | remaining: {x}")
        x = x - 1

        data = {"citypostalcode": zip_code}
        location_url = "https://www.lcbo.com/webapp/wcs/stores/servlet/AjaxStoreLocatorResultsView?catalogId=10051&langId=-1&storeId=10203&orderId="

        while True:
            try:
                r = session.post(location_url, headers=headers, data=data)
                break
            except:
                time.sleep(10)
                continue

        soup = BeautifulSoup(r.text, "html.parser")

        for script in soup.find_all(
            "div", attrs={"class": "row store-row store-hidden"}
        ):

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

            if store_number not in addresses:
                addresses.append(str(store[7]))
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store

        for script in soup.find_all("div", attrs={"class": "row store-row"}):
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

            if str(store_number) not in addresses:
                addresses.append(str(store[7]))
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store

        for script in soup.find_all(
            "div", attrs={"class": "row store-row pilot-store"}
        ):

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

            if store_number not in addresses:
                addresses.append(str(store[7]))
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
