import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authorization": "Bearer 6152722e2ced5fe5853657e4ba35654e484e3e9ed76c3da268d24e83220d5017",
}

logger = SgLogSetup().get_logger("harrisandhoole_co_uk")


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
    url = "https://www.harrisandhoole.co.uk/shops"
    r = session.get(url, headers=headers)
    website = "harrisandhoole.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ',slug:"' in line:
            items = line.split(',slug:"')
            for item in items:
                if ",hero:" in item and "our-" not in item:
                    locs.append(
                        "https://www.harrisandhoole.co.uk/shop/" + item.split('"')[0]
                    )
    for loc in locs:
        logger.info(loc)
        purl = (
            "https://cdn.contentful.com/spaces/yb6dw9km2hlk/environments/master/entries?include=10&content_type=store&fields.slug="
            + loc.split("/shop/")[1]
        )
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        monhrs = ""
        tuehrs = ""
        wedhrs = ""
        thuhrs = ""
        frihrs = ""
        sathrs = ""
        sunhrs = ""
        r2 = session.get(purl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"title": "' in line2 and name == "":
                name = line2.split('"title": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                addinfo = line2.split('"streetAddress": "')[1].split('"')[0]
                addr = parse_address_intl(addinfo)
                city = addr.city
                zc = addr.postcode
                add = addr.street_address_1
            if '"lon":' in line2:
                lng = line2.split('"lon":')[1].split(",")[0].strip()
            if '"lat":' in line2:
                lat = (
                    line2.split(":")[1]
                    .strip()
                    .replace("\r", "")
                    .replace("\n", "")
                    .replace("\t", "")
                )
            if '"day": "' in line2:
                day = line2.split('"day": "')[1].split('"')[0]
            if '"opensAt": "' in line2:
                hrs = day + ": " + line2.split('"opensAt": "')[1].split('"')[0]
            if '"closesAt": "' in line2:
                hrs = hrs + "-" + line2.split('At": "')[1].split('"')[0]
                if "Mon" in hrs:
                    monhrs = hrs
                if "Tue" in hrs:
                    tuehrs = hrs
                if "Wed" in hrs:
                    wedhrs = hrs
                if "Thu" in hrs:
                    thuhrs = hrs
                if "Fri" in hrs:
                    frihrs = hrs
                if "Sat" in hrs:
                    sathrs = hrs
                if "Sun" in hrs:
                    sunhrs = hrs
        hours = (
            monhrs
            + "; "
            + tuehrs
            + "; "
            + wedhrs
            + "; "
            + thuhrs
            + "; "
            + frihrs
            + "; "
            + sathrs
            + "; "
            + sunhrs
        )
        if "TEMPORARILY" in name.upper():
            hours = "TEMPORARILY CLOSED"
        if " Temp" in name:
            name = name.split(" Temp")[0]
        if " TEMP" in name:
            name = name.split(" TEMP")[0]
        if "guildford-tesco" in loc:
            zc = "GU2"
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
