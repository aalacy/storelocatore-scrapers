import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import time

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger(
    "skyscanner_com__airports__uk__airports-in-united-kingdom"
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
    locs = []
    urls = [
        "https://www.skyscanner.com/airports/engla/airports-in-england.html",
        "https://www.skyscanner.com/airports/n_ire/airports-in-northern-ireland.html",
        "https://www.skyscanner.com/airports/scotl/airports-in-scotland.html",
        "https://www.skyscanner.com/airports/wales/airports-in-wales.html",
    ]
    cities = []
    website = "skyscanner.com/airports/uk/airports-in-united-kingdom"
    typ = "<MISSING>"
    country = "GB"
    for url in urls:
        r = session.get(url, headers=headers)
        logger.info(url)
        time.sleep(10)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if (
                '<a href="/airports/' in line
                and ">All airports</a>" not in line
                and "<h4>With non-stop" in line
            ):
                items = line.split('<a href="/airports/')
                for item in items:
                    if '<span class="label">' in item:
                        lurl = (
                            "https://www.skyscanner.com/airports/" + item.split('"')[0]
                        )
                        if "airports.html" in lurl:
                            cities.append(lurl)
                        else:
                            if lurl not in locs and "airports-in" not in lurl:
                                locs.append(lurl)
    for city in cities:
        logger.info(city)
        time.sleep(10)
        r = session.get(city, headers=headers)
        Found = True
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if "<strong>Airports near" in line:
                Found = False
            if (
                Found
                and '<a href="/airports/' in line
                and "All airports</a></li>" not in line
            ):
                lurl = (
                    "https://www.skyscanner.com" + line.split('href="')[1].split('"')[0]
                )
                if lurl not in locs and "airports-in" not in lurl:
                    locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        time.sleep(10)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" Information")[0]
            if 'property="place:location:latitude" content="' in line2:
                lat = line2.split('property="place:location:latitude" content="')[
                    1
                ].split('"')[0]
            if 'property="place:location:longitude" content="' in line2:
                lng = line2.split('property="place:location:longitude" content="')[
                    1
                ].split('"')[0]
            if 'itemprop="telephone">' in line2:
                phone = line2.split('itemprop="telephone">')[1].split("<")[0]
            if "IATA code:</th><td>" in line2:
                store = line2.split("IATA code:</th><td>")[1].split("<")[0]
            if "Address:</strong><br>" in line2:
                rawadd = (
                    line2.split("Address:</strong><br>")[1]
                    .split("</p><table>")[0]
                    .replace("<br>", "")
                    .replace("  ", " ")
                )
                rawadd = rawadd.replace("UNITED KINGDOM", "").strip()
                addr = parse_address_intl(rawadd)
                city = addr.city
                zc = addr.postcode
                add = addr.street_address_1
        if phone == "":
            phone = "<MISSING>"
        if zc == "":
            zc = "<MISSING>"
        if city == "":
            city = "<MISSING>"
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
