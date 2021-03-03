import csv
from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kiehls_ca")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.CANADA],
    max_radius_miles=25,
    max_search_results=None,
)

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    ids = []
    for lat, lng in search:
        try:
            x = lat
            y = lng
            url = (
                "https://www.kiehls.ca/on/demandware.store/Sites-kiehls-ca-Site/en_CA/Stores-Search?unit=km&distance=25&lat="
                + str(x)
                + "&long="
                + str(y)
                + "&ajax=true"
            )
            logger.info("%s - %s..." % (str(x), str(y)))
            website = "kiehls.ca"
            r = session.get(url, headers=headers)
            for item in json.loads(r.content)["storelocatorresults"]["stores"]:
                name = item["name"]
                logger.info(name)
                loc = "<MISSING>"
                add = item["address1"] + " " + item["address2"]
                add = add.strip()
                city = item["city"]
                phone = item["phone"]
                lat = item["latitude"]
                lng = item["longitude"]
                country = "CA"
                typ = "<MISSING>"
                zc = item["postalCode"]
                store = item["id"]
                zc = item["postalCode"]
                hours = ""
                state = "<MISSING>"
                surl = (
                    "https://www.kiehls.ca/on/demandware.store/Sites-kiehls-ca-Site/en_CA/Stores-Details?sid="
                    + store
                )
                r2 = session.get(surl, headers=headers)
                alllines = ""
                for line2 in r2.iter_lines():
                    line2 = str(line2.decode("utf-8"))
                    alllines = alllines + line2.replace("\r", "").replace(
                        "\t", ""
                    ).replace("\n", "")
                try:
                    hours = alllines.split(
                        '<div class="c-storelocator__details-hours">'
                    )[1].split("<")[0]
                except:
                    hours = "<MISSING>"
                hours = hours.replace("/", "; ")
                if store not in ids:
                    ids.append(store)
                    poi = [
                        website,
                        loc,
                        name,
                        add,
                        city,
                        state,
                        zc,
                        country,
                        store,
                        phone,
                        typ,
                        lat,
                        lng,
                        hours,
                    ]
                    yield poi
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
