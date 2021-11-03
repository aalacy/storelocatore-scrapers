import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("harryramsdens_co_uk")


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
    url = "https://www.harryramsdens.co.uk/.netlify/functions/get-stores"
    r = session.get(url, headers=headers)
    website = "harryramsdens.co.uk"
    typ = "Restaurant"
    country = "GB"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        hours = ""
        addinfo = item["address"]
        addinfo = (
            str(addinfo)
            .replace("\r", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace("\\n", "")
            .replace("\\t", "")
        )
        addr = parse_address_intl(addinfo)
        city = addr.city
        zc = addr.postcode
        add = addr.street_address_1
        city = "<MISSING>"
        zc = "<MISSING>"
        state = "<MISSING>"
        lat = item["location"]["lat"]
        lng = item["location"]["lng"]
        name = item["title"]
        loc = "https://www.harryramsdens.co.uk/location/" + item["slug"]["current"]
        if "takeaway" in loc:
            typ = "Takeaway"
        if "Motorway" in addinfo:
            typ = "Motorway"
        try:
            for day in item["opening_hours"]:
                hrs = day["day"] + ": " + day["open"] + "-" + day["close"]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        except:
            pass
        phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if "0" not in hours:
            hours = "<MISSING>"
        if hours is None:
            hours = "<MISSING>"
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
