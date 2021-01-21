import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
import usaddress

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("knockouts_net")


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
                "raw_address",
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
    url = "https://www.knockouts.com/wp-json/wpgmza/v1/markers/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMopR0gEJFGeUgsSKgYLRsbVKtQCWBhBO"
    r = session.get(url, headers=headers)
    website = "knockouts.net"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        rawadd = item["address"]
        loc = "<MISSING>"
        store = "<MISSING>"
        lat = item["lat"]
        lng = item["lng"]
        name = item["title"]
        phone = "<MISSING>"
        hours = "<MISSING>"
        try:
            tagged = usaddress.tag(rawadd)[0]
            city = tagged.get("PlaceName", "<MISSING>")
            state = tagged.get("StateName", "<MISSING>")
            zc = tagged.get("ZipCode", "<MISSING>")
            if city != "<MISSING>":
                add = rawadd.split(city)[0].strip()
            else:
                add = rawadd.split(",")[0]
        except:
            zc = "<MISSING>"
            add = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
        if "Burleson" in name:
            add = "1185 N. Burleson Blvd., Ste. 215"
            city = "Burleson"
            state = "Texas"
            zc = "76028"
        add = add.replace("<br />", "")
        if "Keller" in name:
            add = "1600 Keller Pkwy Suite 130"
            city = "Keller"
            state = "Texas"
            zc = "76248"
        if "Saginaw" in name:
            add = "1209 N Saginaw Blvd"
            city = "Saginaw"
            state = "Texas"
            zc = "76179"
        add = add.replace(",", "").strip()
        yield [
            website,
            loc,
            name,
            rawadd,
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
