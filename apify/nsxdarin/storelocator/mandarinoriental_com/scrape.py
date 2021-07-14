import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("mandarinoriental_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    url = "https://www.mandarinoriental.com/ajax/getproperties?language=1"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    array = json.loads(r.content)
    for item in array["data"]["record"]:
        hurl = "https://www.mandarinoriental.com/" + item["homepage"].replace(
            "\\/", "/"
        )
        name = item["name"]
        rawadd = "<MISSING>"
        website = "mandarinoriental.com"
        add = "<MISSING>"
        lat = item["latitude"]
        lng = item["longitude"]
        typ = "Hotel"
        hours = "<MISSING>"
        city = item["city"]
        state = "<MISSING>"
        zc = "<MISSING>"
        country = item["country"]
        store = item["properties_id"]
        phone = item["phone"]
        r2 = session.get(hurl, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        logger.info(("Pulling Location %s..." % hurl))
        for line in r2.iter_lines(decode_unicode=True):
            if '"addressRegion">' in line:
                state = line.split('"addressRegion">')[1].split("<")[0]
            if 'itemprop="streetAddress">' in line:
                add = line.split('itemprop="streetAddress">')[1].split("<")[0]
            if '"postalCode">' in line:
                zc = line.split('"postalCode">')[1].split("<")[0]
            if '<span class="address-display">' in line:
                rawadd = line.split('<span class="address-display">')[1].split(
                    "</span>"
                )[0]
                addr = parse_address_intl(rawadd)
                zc = addr.postcode
                state = addr.state
                add = addr.street_address_1
        if "-" in city:
            city = city.split("-")[0].strip()
        if state == "" or state is None:
            state = "<MISSING>"
        if city == "" or city is None:
            city = "<MISSING>"
        if zc == "" or zc is None:
            zc = "<MISSING>"
        if add == "" or add is None:
            add = "<MISSING>"
        yield [
            website,
            hurl,
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
