import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sglogging import sglog

logger = SgLogSetup().get_logger(
    "walmart_ca__en?fltr_equals_WALK___IN___MEDICAL___CLINIC"
)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA],
    max_radius_miles=20,
    max_search_results=20,
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


ids = set()
total = 0


def item_transformer(item):
    global total
    global ids
    website = "walmart.ca/en?fltr_equals_WALK___IN___MEDICAL___CLINIC"
    typ = "Walmart"

    if "WALK_IN_MEDICAL_CLINIC" in str(item):
        name = item["displayName"]
        store = item["id"]
        loc = (
            "https://www.walmart.ca/en/stores-near-me/"
            + name.replace(" ", "-").lower()
            + "-"
            + str(store).strip()
        )
        add = item["address"]["address1"]
        city = item["address"]["city"]
        state = item["address"]["state"]
        phonecopy = item["phone"]
        lat = item["geoPoint"]["latitude"]
        lng = item["geoPoint"]["longitude"]
        zc = item["address"]["postalCode"]
        hours = None
        phone = None
        for service in item["servicesMap"]:
            if service["service"]["id"] == 1005:
                try:
                    phone = service["phone"] if service["phone"] else phonecopy
                except Exception:
                    phone = phonecopy
                hours = "; ".join(
                    [
                        str(
                            "{}: {}-{}".format(
                                str(i["day"]).capitalize(),
                                str(i["start"]),
                                str(i["end"]),
                            )
                        )
                        if "alse" in str(i["closed"])
                        else str("{}: Closed".format(str(i["day"]).capitalize()))
                        for i in service["regularHours"]
                    ]
                )
        if not phone:
            phone = phonecopy
        country = item["address"]["country"]
        if "Supercentre" in name:
            typ = "Supercenter"
        if "Neighborhood Market" in name:
            typ = "Neighborhood Market"
        if not hours:
            hours = "<MISSING>"
        if add != "" and str(str(store) + str(lat) + str(lng) + str(zc)) not in ids:
            ids.add(str(str(store) + str(lat) + str(lng) + str(zc)))
            total += 1
            return [
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


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    maxZ = search.items_remaining()
    with SgRequests() as session:
        for code in search:
            found = 0
            url = (
                "https://www.walmart.ca/en/stores-near-me/api/searchStores?singleLineAddr="
                + code.replace(" ", "")
            )
            r2 = session.get(url, headers=headers, timeout=15)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            r2 = r2.json()
            for item in r2["payload"]["stores"]:
                found += 1
                record = item_transformer(item)
                if record:
                    yield record
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )
            logzilla.info(
                f"{code} | found: {found} | total: {total} | progress: {progress}"
            )


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
