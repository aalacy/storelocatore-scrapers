import csv
from sgrequests import SgRequests
import sgzip
from tenacity import retry, stop_after_attempt
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ford_com")


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


@retry(stop=stop_after_attempt(10))
def fetch_zip_code(url):
    session = SgRequests()
    return session.get(url, headers=headers, timeout=10).json()


def fetch_data():
    ids = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    code = search.next_zip()
    while code:
        result_coords = []
        url = (
            "https://www.ford.com/services/dealer/Dealers.json?make=Ford&radius=500&filter=&minDealers=1&maxDealers=100&postalCode="
            + code
            + "&api_key=0d571406-82e4-2b65-cc885011-048eb263"
        )
        js = fetch_zip_code(url)
        if "Dealer" in js["Response"]:
            dealers = (
                js["Response"]["Dealer"]
                if isinstance(js["Response"]["Dealer"], list)
                else [js["Response"]["Dealer"]]
            )
            for item in dealers:
                lng = item["Longitude"]
                lat = item["Latitude"]
                result_coords.append((lat, lng))
                name = item["Name"]
                typ = item["dealerType"]
                website = "ford.com"
                purl = item["URL"]
                hours = ""
                add = (
                    item["Address"]["Street1"]
                    + " "
                    + item["Address"]["Street2"]
                    + " "
                    + item["Address"]["Street3"]
                )
                add = add.strip()
                city = item["Address"]["City"]
                state = item["Address"]["State"]
                country = item["Address"]["Country"][:2]
                zc = item["Address"]["PostalCode"]
                store = item["SalesCode"]
                phone = item["Phone"]
                daytext = str(item["SalesHours"])
                daytext = daytext.replace("'", '"')
                daytext = daytext.replace('u"', '"').replace(" {", "{")
                days = daytext.split(",{")
                for day in days:
                    if '"name": "' in day:
                        dname = day.split('"name": "')[1].split('"')[0]
                        if '"closed": "true"' in day:
                            hrs = "Closed"
                        else:
                            hrs = (
                                day.split('"open": "')[1].split('"')[0]
                                + "-"
                                + day.split('"close": "')[1].split('"')[0]
                            )
                        if hours == "":
                            hours = dname + ": " + hrs
                        else:
                            hours = hours + "; " + dname + ": " + hrs
                if store not in ids:
                    ids.append(store)
                    if hours == "":
                        hours = "<MISSING>"
                    if purl == "":
                        purl = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
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
            search.max_count_update(result_coords)
        code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
