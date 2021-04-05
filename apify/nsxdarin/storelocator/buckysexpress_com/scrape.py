import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("buckysexpress_com")


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
    website = "buckysexpress.com"
    typ = "<MISSING>"
    country = "<MISSING>"
    locs = ["http://buckysexpress.com/store/buckys-342"]
    regions = [
        "https://buckysexpress.com/node/3",
        "https://buckysexpress.com/node/6",
        "https://buckysexpress.com/node/290",
        "https://buckysexpress.com/node/5",
    ]
    for region in regions:
        r = session.get(region, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '<a href="/store/' in line:
                locs.append(
                    "https://buckysexpress.com/" + line.split('href="')[1].split('"')[0]
                )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("-", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split(">")[1].split(" |")[0]
            if "streetAddress\\u0022\\u003E" in line2:
                add = line2.split("streetAddress\\u0022\\u003E")[1].split("\\")[0]
                city = line2.split("addressLocality\\u0022\\u003E")[1].split(",")[0]
                state = line2.split("addressRegion\\u0022\\u003E")[1].split("\\")[0]
                try:
                    zc = line2.split("postalCode\\u0022\\u003E")[1].split("\\")[0]
                except:
                    zc = "<MISSING>"
            if "<br /><br />" in line2:
                phone = line2.split("<br />")[4].split("<")[0]
            if '{"latitude":' in line2:
                lat = line2.split('{"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
        hours = "Sun-Sat: 24/7"
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
