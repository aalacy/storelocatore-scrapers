import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("huntington_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=None,
    max_search_results=10,
)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
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
    locs = []
    for lat, lng in search:
        x = lat
        y = lng
        url = "https://www.huntington.com/post/GetLocations/GetLocationsList"
        payload = {
            "longitude": lng,
            "latitude": lat,
            "typeFilter": "1",
            "envelopeFreeDepositsFilter": False,
            "timeZoneOffset": "420",
            "scController": "GetLocations",
            "scAction": "GetLocationsList",
        }
        logger.info("%s - %s..." % (str(x), str(y)))
        session = SgRequests()
        r = session.post(url, headers=headers, data=payload)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"LocID":"bko' in line:
                items = line.split('"LocID":"bko')
                for item in items:
                    if '"type":"FeatureCollection"' not in item:
                        lurl = (
                            "https://www.huntington.com/Community/branch-info?locationId="
                            + item.split('"')[0]
                        )
                        if lurl not in locs:
                            locs.append(lurl)
        for loc in locs:
            session = SgRequests()
            logger.info(loc)
            r2 = session.get(loc, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            lines = r2.iter_lines(decode_unicode=True)
            hours = ""
            typ = "Branch"
            website = "huntington.com"
            Found = False
            for line2 in lines:
                if '"streetAddress":"' in line2:
                    data = json.loads(line2)
                    name = data["name"]
                    store = data["@id"].rsplit("=")[1]
                    add = data["address"]["streetAddress"]
                    city = data["address"]["addressLocality"]
                    state = data["address"]["addressRegion"]
                    country = data["address"]["addressCountry"]
                    zc = data["address"]["postalCode"]
                    phone = data["telephone"]
                    lat = data["geo"]["latitude"]
                    lng = data["geo"]["longitude"]
                    items = line2.split('"dayOfWeek":"http://schema.org/')
                if "<!-- Lobby section-->" in line2:
                    Found = True
                if Found and "</div>" in line2:
                    Found = False
                if Found and "<br" in line2 and ": " in line2:
                    if hours == "":
                        hours = (
                            line2.split(">")[1]
                            .replace("\r", "")
                            .replace("\n", "")
                            .replace("\t", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + line2.split(">")[1]
                            .replace("\r", "")
                            .replace("\n", "")
                            .replace("\t", "")
                            .strip()
                        )
            if hours != "":
                yield [
                    website,
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
