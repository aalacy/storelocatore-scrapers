import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lincoln_com")
session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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

    base_url = "https://www.lincoln.com"
    addresses = []
    zipcodes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA]
    )
    for zip_code in zipcodes:
        str_zip = str(zip_code)
        if len(str_zip) == 4:
            str_zip = "0" + str_zip
            logger.info(f"appended zero:{zip_code} => {str_zip}")
        if len(str_zip) == 3:
            str_zip = "00" + str_zip
            logger.info(f"appended zeros:{zip_code} => {str_zip}")
        logger.info(f"fetching records for zipcode:{str_zip}")
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        phone = ""
        latitude = ""
        longitude = ""
        hours_of_operation = ""
        get_u = (
            "https://www.lincoln.com/services/dealer/Dealers.json?make=Lincoln&radius=500&minDealers=1&maxDealers=100&postalCode="
            + str_zip
            + "&api_key=0d571406-82e4-2b65-cc885011-048eb263"
        )
        try:
            k = session.get(get_u, timeout=5).json()
        except:
            logger.info(f"timeout probably")
            continue
        if "Response" in k and "Dealer" in k["Response"]:
            if isinstance(k["Response"]["Dealer"], list):
                for i in k["Response"]["Dealer"]:
                    if i["ldlrcalltrk_lad"]:
                        phone = i["ldlrcalltrk_lad"]
                    else:
                        phone = i["Phone"]
                    if "Street1" in i["Address"]:
                        street_address = i["Address"]["Street1"]
                    else:
                        street_address = "<MISSING>"
                    city = i["Address"]["City"]
                    state = i["Address"]["State"]
                    zipp = i["Address"]["PostalCode"]
                    time = ""
                    time1 = ""
                    h1 = ""
                    if "Day" in i["SalesHours"]:
                        for j in i["SalesHours"]["Day"]:
                            if "closed" in j and j == "true":
                                h1 = j["name"] + " " + "closed"
                            elif "open" in j:
                                time = (
                                    time
                                    + " "
                                    + j["name"]
                                    + " "
                                    + j["open"]
                                    + " "
                                    + j["close"]
                                    + " "
                                    + h1
                                )

                    hours_of_operation = time.strip()
                    latitude = i["Latitude"]
                    longitude = i["Longitude"]
                    zipcodes.found_location_at(latitude, longitude)
                    store = []
                    store.append(base_url)
                    store.append(i["Name"])
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    store.append("<MISSING>")
                    store.append(latitude)
                    store.append(longitude)
                    store.append(
                        hours_of_operation if hours_of_operation else "<MISSING>"
                    )
                    store.append(
                        "https://www.lincoln.com/dealerships/dealer-details/"
                        + i["urlKey"]
                    )
                    if store[13] in addresses:
                        continue
                    addresses.append(store[13])
                    yield store

        if "Response" in k and "Dealer" in k["Response"]:
            if isinstance(k["Response"]["Dealer"], dict):

                if "Street1" in k["Response"]["Dealer"]["Address"]:
                    street_address = k["Response"]["Dealer"]["Address"]["Street1"]
                else:
                    street_address = "<MISSING>"

                if k["Response"]["Dealer"]["ldlrcalltrk_lad"]:
                    phone = k["Response"]["Dealer"]["ldlrcalltrk_lad"]
                else:
                    phone = k["Response"]["Dealer"]["Phone"]

                city = k["Response"]["Dealer"]["Address"]["City"]
                state = k["Response"]["Dealer"]["Address"]["State"]
                zipp = k["Response"]["Dealer"]["Address"]["PostalCode"]
                time = ""
                time1 = ""
                h1 = ""
                if "Day" in k["Response"]["Dealer"]["SalesHours"]:
                    for j in k["Response"]["Dealer"]["SalesHours"]["Day"]:
                        if "closed" in j and j == "true":
                            h1 = j["name"] + " " + "closed"
                        elif "open" in j:
                            time = (
                                time
                                + " "
                                + j["name"]
                                + " "
                                + j["open"]
                                + " "
                                + j["close"]
                                + " "
                                + h1
                            )

                if "Day" in k["Response"]["Dealer"]["ServiceHours"]:
                    for j in k["Response"]["Dealer"]["ServiceHours"]["Day"]:
                        if "closed" in j and j == "true":
                            h1 = j["name"] + " " + "closed"
                        elif "open" in j:
                            time1 = (
                                time1
                                + " "
                                + j["name"]
                                + " "
                                + j["open"]
                                + " "
                                + j["close"]
                                + " "
                                + h1
                            )

                hours_of_operation = " SalesHours " + time + " ServiceHours " + time1
                latitude = k["Response"]["Dealer"]["Latitude"]
                longitude = k["Response"]["Dealer"]["Longitude"]

                store = []
                store.append(base_url)
                store.append(k["Response"]["Dealer"]["Name"])
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(
                    hours_of_operation.replace(
                        " SalesHours  ServiceHours ", "<MISSING>"
                    )
                    if hours_of_operation
                    else "<MISSING>"
                )
                store.append(
                    "https://www.lincoln.com/dealerships/dealer-details/" + i["urlKey"]
                )
                if store[13] in addresses:
                    continue
                addresses.append(store[13])
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
