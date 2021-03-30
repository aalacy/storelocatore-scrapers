import csv
from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("fisherautoparts_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=50,
    max_search_results=None,
)


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
    url = "https://fisherautoparts.com/Fisher-Store-Locator.aspx/GetLocations"
    for lat, lng in search:
        x = lat
        y = lng
        logger.info(("Pulling Lat-Long %s,%s..." % (str(x), str(y))))
        payload = {"lat": str(x), "lng": str(y)}
        r = session.post(url, headers=headers, data=json.dumps(payload))
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if "DocumentElement" in line:
                items = line.split("\\u003cLocation\\u003e")
                for item in items:
                    if '{"d":' not in item:
                        website = "fisherautoparts.com"
                        name = item.split("\\u003cLocationDesc\\u003e")[1].split("\\")[
                            0
                        ]
                        add = item.split("\\u003cAddress\\u003e")[1].split("\\")[0]
                        try:
                            phone = item.split("Phone\\u003e")[1].split("\\")[0]
                        except:
                            phone = "<MISSING>"
                        hours = "<MISSING>"
                        typ = "Location"
                        city = item.split("CityState\\u003e")[1].split(",")[0]
                        state = (
                            item.split("CityState\\u003e")[1]
                            .split(",")[1]
                            .split("\\")[0]
                            .strip()
                        )
                        zc = "<MISSING>"
                        country = "US"
                        store = item.split("\\u003cLocationId\\u003e")[1].split("\\")[0]
                        lat = item.split("Latitude\\u003e")[1].split("\\")[0]
                        lng = item.split("Longitude\\u003e")[1].split("\\")[0]
                        if store not in ids:
                            ids.append(store)
                            logger.info(("Pulling Store ID #%s..." % store))
                            purl = "https://www.fisherautoparts.com/Fisher-Store-Locator.aspx"
                            yield [
                                website,
                                purl,
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
