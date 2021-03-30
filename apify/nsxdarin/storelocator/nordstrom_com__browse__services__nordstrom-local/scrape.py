import csv
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("nordstrom_com__browse__services__nordstrom-local")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=100,
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
    for code in search:
        logger.info(("Pulling Zip Code %s..." % code))
        url = (
            "https://public.api.nordstrom.com/v2/storeservice/postalcode/"
            + code
            + "?distance=100&apikey=Gneq2B6KqSbEABkg9IDRxuxAef9BqusJ&apigee_bypass_cache=1&format=json"
        )
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        lines = r.iter_lines(decode_unicode=True)
        for line in lines:
            if '{"number":' in line:
                items = line.split('{"number":')
                for item in items:
                    if ',"address":"' in item:
                        website = "nordstrom.com/browse/services/nordstrom-local"
                        country = item.split('"country":"')[1].split('"')[0]
                        name = item.split('"name":"')[1].split('"')[0]
                        add = item.split(',"address":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split(',"state":"')[1].split('"')[0]
                        zc = item.split('"zipCode":"')[1].split('"')[0]
                        phone = item.split('"phone":"')[1].split('"')[0]
                        hours = item.split('"hours":"')[1].split('"')[0]
                        if hours == "":
                            hours = "<MISSING>"
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        loc = (
                            "https://shop.nordstrom.com/store-details/"
                            + item.split('"path":"')[1].split('"')[0]
                        )
                        store = item.split(",")[0]
                        typ = item.split('"type":"')[1].split('"')[0]
                        if "United" in country and store not in ids:
                            ids.append(store)
                            country = "US"
                            hours = hours.replace("|", "; ")
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
