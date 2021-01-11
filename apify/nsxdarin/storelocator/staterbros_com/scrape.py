import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("staterbros_com")


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
    url = "https://www.staterbros.com/stores-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "staterbros.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.staterbros.com/stores/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        rawadd = ""
        state = ""
        zc = ""
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        store = loc.split("/stores/")[1].split("/")[0]
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "Phone Number</h1>" in line2:
                next(lines)
                next(lines)
                next(lines)
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                phone = g.split('">')[1].split("<")[0]
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" - ")[0]
            if '<div class="elementor-custom-embed"><iframe frameborder="0"' in line2:
                rawadd = line2.split('title="')[1].split('"')[0]
                try:
                    add = usaddress.tag(rawadd)
                    baseadd = add[0]
                    if "AddressNumber" not in baseadd:
                        baseadd["AddressNumber"] = ""
                    if "StreetName" not in baseadd:
                        baseadd["StreetName"] = ""
                    if "StreetNamePostType" not in baseadd:
                        baseadd["StreetNamePostType"] = ""
                    if "PlaceName" not in baseadd:
                        baseadd["PlaceName"] = "<INACCESSIBLE>"
                    if "StateName" not in baseadd:
                        baseadd["StateName"] = "<INACCESSIBLE>"
                    if "ZipCode" not in baseadd:
                        baseadd["ZipCode"] = "<INACCESSIBLE>"
                    address = (
                        add[0]["AddressNumber"]
                        + " "
                        + add[0]["StreetName"]
                        + " "
                        + add[0]["StreetNamePostType"]
                    )
                    address = address.encode("ascii").decode()
                    if address == "":
                        address = "<MISSING>"
                    city = add[0]["PlaceName"]
                    state = add[0]["StateName"]
                    zc = add[0]["ZipCode"]
                except:
                    pass
            if '<p class="elementor-icon-box-description"><p><b>' in line2:
                if hours == "":
                    hours = (
                        line2.split('<p class="elementor-icon-box-description"><p><b>')[
                            1
                        ]
                        .split("</p>")[0]
                        .replace("</b>", ": ")
                        .replace("&#8211;", "-")
                    )
                else:
                    hours = (
                        hours
                        + "; "
                        + line2.split(
                            '<p class="elementor-icon-box-description"><p><b>'
                        )[1]
                        .split("</p>")[0]
                        .replace("</b>", ": ")
                        .replace("&#8211;", "-")
                    )
        if add != "":
            if state == "Linda":
                state = "CA"
                city = "Yorba Linda"
            yield [
                website,
                loc,
                name,
                rawadd,
                address,
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
