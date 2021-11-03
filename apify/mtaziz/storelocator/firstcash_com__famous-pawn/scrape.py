from sgrequests import SgRequests
from sglogging import SgLogSetup
import unicodedata
import pgeocode
import csv
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

session = SgRequests()
logger = SgLogSetup().get_logger("firstcash_com__famous-pawn")


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    url_store = "http://find.cashamerica.us/api/stores?p="
    url_key = "http://find.cashamerica.us/js/controllers/StoreMapController.js"
    logger.info(f"Extract key from: {url_key}")
    r = session.get(url_key)
    key = r.text.split("&key=")[1].split('");')[0]
    if key:
        logger.info(f"Key Found:{key}")
    else:
        logger.info(f"Unable to find the Key, please check the {url_key}")
    start = 1
    total_page_number = 2750  # As of now the last item returned by the page number 2711 while returning 1 item at a time
    items_num_per_page = 1
    total = 0
    for page in range(start, total_page_number):
        url_data = f"{url_store}{str(page)}&s={items_num_per_page}&lat=40.7128&lng=-74.006&d=2019-07-16T05:32:30.276Z&key={str(key)}"
        try:
            data = session.get(url_data).json()
            if "message" in data:
                continue
        except Exception as e:
            logger.info(f"error loading the data:{e}")
            continue

        logger.info(f"[ Pulling the data from] {url_data}")
        found = 0
        for i in range(len(data)):
            store_data = data[i]
            store = []
            store.append("https://www.firstcash.com/famous-pawn")
            store.append(store_data["brand"] if store_data["brand"] else "<MISSING>")
            store.append(
                store_data["address"]["address1"] + store_data["address"]["address2"]
                if store_data["address"]["address2"] is not None
                else store_data["address"]["address1"]
            )
            store.append(
                store_data["address"]["city"]
                if store_data["address"]["city"]
                else "<MISSING>"
            )
            state = ""
            if store_data["address"]["state"] in [
                "AL",
                "AK",
                "AZ",
                "AR",
                "CA",
                "CO",
                "CT",
                "DC",
                "DE",
                "FL",
                "GA",
                "HI",
                "ID",
                "IL",
                "IN",
                "IA",
                "KS",
                "KY",
                "LA",
                "ME",
                "MD",
                "MA",
                "MI",
                "MN",
                "MS",
                "MO",
                "MT",
                "NE",
                "NV",
                "NH",
                "NJ",
                "NM",
                "NY",
                "NC",
                "ND",
                "OH",
                "OK",
                "OR",
                "PA",
                "RI",
                "SC",
                "SD",
                "TN",
                "TX",
                "UT",
                "VT",
                "VA",
                "WA",
                "WV",
                "WI",
                "WY",
            ]:
                state = store_data["address"]["state"]
            store.append(state if state else "<MISSING>")
            zipp = store_data["address"]["zipCode"]
            nomi = pgeocode.Nominatim("us")
            if nomi.query_postal_code(str(zipp))["country_code"] != "US":
                continue
            if "00000" in store_data["address"]["zipCode"]:
                zipp = "<MISSING>"
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append(
                store_data["storeNumber"] if store_data["storeNumber"] else "<MISSING>"
            )
            phone = (
                "("
                + store_data["phone"][0:3]
                + ") "
                + store_data["phone"][3:6]
                + "-"
                + store_data["phone"][6:10]
            )
            if "() -" in phone:
                phone = "<MISSING>"
            store.append(phone if phone else "<MISSING>")
            store.append(
                store_data["brand"]
                .replace("0", "")
                .replace("1", "")
                .replace("2", "")
                .replace("3", "")
                .replace("4", "")
                .replace("5", "")
                .replace("6", "")
                .replace("7", "")
                .replace("8", "")
                .replace("9", "")
                .strip()
                if store_data["brand"]
                else "<MISSING>"
            )
            store.append(
                store_data["latitude"] if store_data["latitude"] else "<MISSING>"
            )
            store.append(
                store_data["longitude"] if store_data["longitude"] else "<MISSING>"
            )
            hours_request = session.get(
                "http://find.cashamerica.us/api/stores/"
                + str(store_data["storeNumber"])
                + "?key="
                + key
            )
            hours_details = hours_request.json()["weeklyHours"]
            hours = ""
            for k in range(len(hours_details)):
                if hours_details[k]["openTime"] != "Closed":
                    hours = (
                        hours
                        + " "
                        + hours_details[k]["weekDay"]
                        + " "
                        + hours_details[k]["openTime"]
                        + " "
                        + hours_details[k]["closeTime"]
                        + " "
                    )
            store.append(hours.strip() if hours != "" else "<MISSING>")
            store.append("<INACCESSIBLE>")
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = "".join(
                        (
                            c
                            for c in unicodedata.normalize("NFD", store[i])
                            if unicodedata.category(c) != "Mn"
                        )
                    )
            store = [x.replace("–", "-") if type(x) == str else x for x in store]
            store = [x.strip() if type(x) == str else x for x in store]
            yield store
            found += 1
        total += found
        logger.info(f"Total Store Count: {total}")
    logger.info(f"Scraping Finished | Total Store Count: {total}")


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
