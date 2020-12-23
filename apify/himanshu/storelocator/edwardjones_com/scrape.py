import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("edwardjones_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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

    address = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    zipcodes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=25,
        max_search_results=100,
    )
    for zip_code in zipcodes:
        try:
            r = session.get(
                "https://www.edwardjones.com/cgi/findFaByAddress.action?address="
                + str(zip_code),
                headers=headers,
            )
            json_data = r.json()
        except:
            continue

        if "error" not in json_data and json_data["multipleLocations"] is False:
            if json_data["faList"] is not [] and json_data["faList"] is not None:
                for x in json_data["faList"]:
                    if x["additionalFaData"]["faInfo"] is not None:
                        location_name = x["additionalFaData"]["faInfo"]["convertedName"]
                        street_address = x["additionalFaData"]["faInfo"][
                            "streetAddress"
                        ]
                        state = x["additionalFaData"]["faInfo"]["state"]
                        city = x["additionalFaData"]["faInfo"]["city"]
                        zipp = x["additionalFaData"]["faInfo"]["postalCode"]
                        store_number = x["additionalFaData"]["faInfo"]["entityNumber"]
                        latitude = x["additionalFaData"]["faInfo"]["latitude"]
                        longitude = x["additionalFaData"]["faInfo"]["longitude"]
                        phone = x["additionalFaData"]["faInfo"]["phoneNumber"]
                        page_url = (
                            "https://www.edwardjones.com/financial-advisor/index.html?CIRN="
                            + x["additionalFaData"]["faInfo"]["locatorId"]
                        )

                        store = []
                        store.append("https://www.edwardjones.com/")
                        store.append(location_name)
                        store.append(street_address if street_address else "<MISSING>")
                        store.append(city)
                        store.append(state)
                        store.append(zipp)
                        store.append("US")
                        store.append(store_number)
                        store.append(phone)
                        store.append("<MISSING>")
                        store.append(latitude)
                        store.append(longitude)
                        store.append("<INACCESIBLE>")
                        store.append(page_url)
                        if store[2] in address:
                            continue
                        address.append(store[2])
                        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
