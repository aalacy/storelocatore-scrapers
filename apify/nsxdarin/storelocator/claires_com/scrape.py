import csv
from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("claires_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=25,
    max_search_results=None,
)

session = SgRequests()
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
    ids = []
    for lat, lng in search:
        try:
            result_coords = []
            x = lat
            y = lng
            url = "https://www.claires.com/on/demandware.store/Sites-clairesNA-Site/en_US/Stores-GetNearestStores"
            payload = {
                "time": "00:00",
                "page": "storelocator",
                "lat": str(x),
                "lng": str(y),
            }
            logger.info("%s - %s..." % (str(x), str(y)))
            website = "claires.com"
            r = session.post(url, headers=headers, data=payload)
            if '"id":"' in r.content.decode("utf-8"):
                for item in json.loads(r.content)["stores"]:
                    hours = ""
                    store = item["id"]
                    name = item["name"]
                    add = item["address1"]
                    try:
                        add = add + " " + item["address2"]
                    except:
                        pass
                    add = add.strip()
                    city = item["city"]
                    zc = item["postalCode"]
                    country = item["country"]
                    phone = item["phone"]
                    lat = item["coordinates"]["lat"]
                    lng = item["coordinates"]["lng"]
                    result_coords.append((lat, lng))
                    typ = item["business"]
                    state = "<MISSING>"
                    loc = "https://www.claires.com/us/store-details/?StoreID=" + store
                    r2 = session.get(loc, headers=headers)
                    lines = r2.iter_lines()
                    for line2 in lines:
                        line2 = str(line2.decode("utf-8"))
                        if (
                            '<link rel="canonical" href="https://stores.claires.com/us/'
                            in line2
                        ):
                            state = (
                                line2.split(
                                    '<link rel="canonical" href="https://stores.claires.com/us/'
                                )[1]
                                .split("/")[0]
                                .upper()
                            )
                        if (
                            '<link rel="canonical" href="https://stores.claires.com/ca/'
                            in line2
                        ):
                            state = (
                                line2.split(
                                    '<link rel="canonical" href="https://stores.claires.com/ca/'
                                )[1]
                                .split("/")[0]
                                .upper()
                            )
                        if "<p><strong>" in line2:
                            next(lines)
                            next(lines)
                            next(lines)
                            g = next(lines)
                            g = str(g.decode("utf-8"))
                            state = g.strip().split(" ")[0]
                    for day in item["storeHours"]:
                        hrs = (
                            day["day"]
                            + ": "
                            + day["from"].strip()
                            + "-"
                            + day["to"].strip()
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
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
    url = "https://stores.claires.com/sitemap.xml"
    website = "claires.com"
    locs = []
    country = "GB"
    typ = "<MISSING>"
    store = "<MISSING>"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://stores.claires.com/gb-" in line and ".html" in line:
            locs.append(line.split(">")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"location-name brand-text-color" ' in line2:
                name = (
                    line2.split('"location-name brand-text-color"')[1]
                    .split('">')[1]
                    .split("<")[0]
                )
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"openingHours": "' in line2 and hours == "":
                hours = line2.split('"openingHours": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
                state = "<MISSING>"
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if (
                '<div class="location-closure-message brand-primary-color">This location is temporarily closed</div>'
                in line2
            ):
                hours = "Temporarily Closed"
        if "Claire's " in add:
            add = add.replace("  ", " ").strip()
            add = add.split("Claire's ")[1]
            store = add.split(" ")[0]
            add = add.split(" ", 1)[1]
        if "/419.html" in loc:
            add = "UNIT 16 THE LANES CENTRE"
        if "/408.html" in loc:
            add = "102 FISHERGATE WALK ST GEORGES CENTRE"
        yield [
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
