import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

logger = SgLogSetup().get_logger("lesliespool_com")
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
        "authority": "lesliespool.com",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "accept": "application/json, text/javascript, */*; q=0.01",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    base_url = "https://www.lesliespool.com"
    coords = static_coordinate_list(radius=200, country_code=SearchableCountries.USA)
    for lat, lng in coords:
        logger.info(f"pulling stores for lat:{lat} long:{lng}")
        r = session.get(
            "https://lesliespool.com/on/demandware.store/Sites-lpm_site-Site/en_US/Stores-FindStores?showMap=false&radius=1000&referrer=dropdown&countryCode=US&lat={}&long={}".format(
                lat, lng
            ),
            headers=headers,
        ).json()

        for dt in r["stores"]:
            page_url = ""
            if dt["contentAssetId"]:
                page_url = "https://lesliespool.com/" + dt["contentAssetId"] + ".html"
            location_name = dt["name"].lower()
            street_address = ""
            street_address1 = ""
            if dt["address2"]:
                street_address1 = dt["address2"].lower()
            street_address = dt["address1"].lower() + " " + street_address1
            city = dt["city"].lower()
            zipp = dt["postalCode"]
            state = dt["stateCode"]
            if dt["latitude"] == 0:
                latitude = ""
                longitude = ""
            else:
                latitude = dt["latitude"]
                longitude = dt["longitude"]

            hours_of_operation = dt["storeHours"].replace("*", " ")
            phone = dt["phone"]

            store = []
            store.append(base_url)
            store.append(location_name.replace("#" + str(dt["ID"]), ""))
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(dt["ID"])
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(
                hours_of_operation.replace("Hours not scheduled for this gro", "")
            )
            store.append(page_url)
            store = [x.strip() if type(x) == str else x for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
