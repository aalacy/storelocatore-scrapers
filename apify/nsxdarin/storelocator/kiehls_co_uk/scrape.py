import csv
from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kiehls_co_uk")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.BRITAIN],
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
                "https://www.kiehls.co.uk/on/demandware.store/Sites-kiehls-uk-v2-Site/en_GB/Stores-Search?unit=km&distance=25&lat="
                + str(x)
                + "&long="
                + str(y)
                + "&ajax=true"
            )
            logger.info("%s - %s..." % (str(x), str(y)))
            website = "kiehls.co.uk"
            r = session.get(url, headers=headers)
            for item in json.loads(r.content)["storelocatorresults"]["stores"]:
                name = item["name"]
                logger.info(name)
                loc = "<MISSING>"
                add = item["address1"] + " " + item["address2"]
                add = add.strip().replace("\\n", ", ").replace("\n", ", ")
                if "," in add:
                    add = add.split(",")[0].strip()
                city = item["city"]
                if city == "":
                    city = "<MISSING>"
                phone = item["phone"]
                lat = item["latitude"]
                lng = item["longitude"]
                country = "GB"
                typ = "<MISSING>"
                store = item["id"]
                zc = item["postalCode"]
                hours = ""
                state = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
                surl = "https://www.kiehls.co.uk/on/demandware.store/Sites-kiehls-uk-v2-Site/en_GB/Stores-Details?sid=" + store.replace(
                    "'", "%27"
                ).replace(
                    " ", "%20"
                )
                r2 = session.get(surl, headers=headers)
                alllines = ""
                for line2 in r2.iter_lines():
                    line2 = str(line2.decode("utf-8"))
                    alllines = alllines + line2.replace("\r", "").replace(
                        "\t", ""
                    ).replace("\n", "; ")
                try:
                    hours = alllines.split(
                        '<div class="c-storelocator__details-hours">'
                    )[1].split("<")[0]
                except:
                    hours = "<MISSING>"
                hours = hours.replace("/", "; ")
                if hours == "":
                    hours = "<MISSING>"
                if store == "":
                    store = "<MISSING>"
                if zc == "":
                    zc = "<MISSING>"
                hours = hours.replace("Tuesday", "; Tuesday")
                hours = hours.replace("Wednesday", "; Wednesday")
                hours = hours.replace("Thursday", "; Thursday")
                hours = hours.replace("Friday", "; Friday")
                hours = hours.replace("Saturday", "; Saturday")
                hours = (
                    hours.replace("day", "day ").replace(" ;", ";").replace("  ", " ")
                )
                if add not in ids and city != "Online":
                    ids.append(add)
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
