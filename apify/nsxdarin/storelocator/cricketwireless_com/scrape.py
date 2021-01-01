import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("cricketwireless_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=10,
    max_search_results=50,
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
    for lat, lng in search:
        try:
            logger.info("Pulling %s-%s..." % (str(lat), str(lng)))
            url = (
                "https://api.momentfeed.com/v1/analytics/api/llp/cricket.json?auth_token=IVNLPNUOBXFPALWE&center="
                + str(lat)
                + ","
                + str(lng)
                + "&coordinates=40,-90,60,-110&multi_account=false&name=Cricket+Wireless+Authorized+Retailer,Cricket+Wireless+Store&page=1&pageSize=50&type=store"
            )
            r = session.get(url, headers=headers)
            lines = r.iter_lines(decode_unicode=True)
            name = ""
            website = "cricketwireless.com"
            country = "US"
            for line in lines:
                if '"momentfeed_venue_id":"' in line:
                    items = line.split('"momentfeed_venue_id":"')
                    for item in items:
                        if '"internal_ref":"' in item:
                            name = item.split('"name":"')[1].split('"')[0]
                            typ = item.split('"brand_name":"')[1].split('"')[0]
                            store = item.split('"corporate_id":"')[1].split('"')[0]
                            add = item.split('"address":"')[1].split('"')[0]
                            city = item.split('"locality":"')[1].split('"')[0]
                            state = item.split('"region":"')[1].split('"')[0]
                            zc = item.split('"postcode":"')[1].split('"')[0]
                            phone = item.split('"phone":"')[1].split('"')[0]
                            lat = item.split('"latitude":"')[1].split('"')[0]
                            lng = item.split('"longitude":"')[1].split('"')[0]
                            purl = item.split('"website":"')[1].split('"')[0]
                            hours = line.split('"store_hours":"')[1].split('"')[0]
                            hours = hours.replace("1,", "Mon: ").replace(
                                ";2,", "; Tue: "
                            )
                            hours = hours.replace(";2,", "; Tue: ")
                            hours = hours.replace(";3,", "; Wed: ")
                            hours = hours.replace(";4,", "; Thu: ")
                            hours = hours.replace(";5,", "; Fri: ")
                            hours = hours.replace(";6,", "; Sat: ")
                            hours = hours.replace(";7,", "; Sun: ")
                            hours = hours.replace(",", "-")
                            if hours == "":
                                hours = "<MISSING>"
                            if phone == "":
                                phone = "<MISSING>"
                            if store not in ids:
                                ids.append(store)
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
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
