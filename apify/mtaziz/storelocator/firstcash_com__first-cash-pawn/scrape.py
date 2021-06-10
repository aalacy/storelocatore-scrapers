import csv
from sgrequests import SgRequests
import unicodedata
import pgeocode
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("firstcash_com__first-cash-pawn")
session = SgRequests()


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
    r = session.get("http://find.cashamerica.us/js/controllers/StoreMapController.js")
    key = r.text.split("&key=")[1].split('");')[0]
    logger.info(
        "[API Authenticaion Key Obtained from StoreMapController.js: %s\n]" % key
    )
    page = 1
    while True:
        try:
            url_api_store = (
                "http://find.cashamerica.us/api/stores?p="
                + str(page)
                + "&s=10&lat=40.7128&lng=-74.006&d=2019-07-16T05:32:30.276Z&key="
                + str(key)
            )
            location_request = session.get(url_api_store)
            logger.info("[API URL]: %s\n" % url_api_store)

        except:
            break
        data = location_request.json()

        if "message" in data:
            break
        logger.info("Number of stores per page: %s" % len(data))
        for i in range(len(data)):
            page_url = (
                "http://find.cashamerica.us/#/storesdetails/"
                + str(data[i]["storeNumber"])
                + "/"
                + data[i]["brand"]
                + "/"
                + str(data[i]["distance"])
                + "/"
                + data[i]["hours"]["displayText"]
                + "/"
                + data[i]["hours"]["storeStatus"]
            )
            store_data = data[i]
            store = []
            store.append("https://www.firstcash.com/first-cash-pawn")
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
            if store_data["address"]["state"] in [
                "AL",
                "AK",
                "AZ",
                "AR",
                "CA",
                "CO",
                "CT",
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

            # Store Number
            store.append(
                store_data["storeNumber"] if store_data["storeNumber"] else "<MISSING>"
            )

            # Phone
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
            phone = phone if phone else "<MISSING>"
            store.append(phone)

            # Location Type
            location_type = store_data["brand"]
            location_type = (
                location_type.replace("0", "")
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
                if location_type
                else "<MISSING>"
            )
            if location_type == "First Cash Pawn #":
                continue
            store.append(location_type)

            # Latitude
            store.append(
                store_data["latitude"] if store_data["latitude"] else "<MISSING>"
            )

            # Longitude
            store.append(
                store_data["longitude"] if store_data["longitude"] else "<MISSING>"
            )

            # Hours of operation
            try:
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
            except:
                hours = ""
            store.append(hours.strip() if hours != "" else "<MISSING>")

            # Page URL
            store.append(page_url)

            # Sanitize the data
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
        page += 1


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
