import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("thebodyshop_co_uk")


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
    url = "https://www.thebodyshop.com/sitemap-gb.xml"
    r = session.get(url, headers=headers)
    website = "thebodyshop.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.thebodyshop.com/en-gb/store-finder/store/" in line:
            items = line.split(
                "<loc>https://www.thebodyshop.com/en-gb/store-finder/store/"
            )
            for item in items:
                if "<urlset" not in item:
                    locs.append(
                        "https://www.thebodyshop.com/en-gb/store-finder/store/"
                        + item.split("<")[0]
                    )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("/", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        lurl = (
            "https://api.thebodyshop.com/rest/v2/thebodyshop-uk/stores/"
            + store
            + "?fields=FULL&lang=en_GB&curr=GBP"
        )
        r2 = session.get(lurl, headers=headers)
        info = json.loads(r2.content)
        try:
            add = info["address"]["line1"]
            phone = info["address"]["phone"]
            zc = info["address"]["postalCode"]
            state = "<MISSING>"
            city = info["address"]["town"]
            lat = info["geoPoint"]["latitude"]
            lng = info["geoPoint"]["longitude"]
            name = info["displayName"]
            for item in info["openingHours"]["weekDayOpeningList"]:
                if item["closed"] is True:
                    hrs = item["weekDay"] + ": Closed"
                else:
                    hrs = item["weekDay"] + ": " + item["opens"] + "-" + item["closes"]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
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
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
