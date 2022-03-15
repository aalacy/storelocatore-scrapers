import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("hamptoninn_com")


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
    canada = [
        "alberta",
        "british-columbia",
        "new-brunswick",
        "newfoundland-labr",
        "nova-scotia",
        "ontario",
        "prince-edward-island",
        "quebec",
        "saskatchewan",
        "manitoba",
    ]
    usa = [
        "alabama",
        "alaska",
        "arizona",
        "arkansas",
        "california",
        "colorado",
        "connecticut",
        "delaware",
        "district-of-columbia",
        "florida",
        "georgia",
        "hawaii",
        "idaho",
        "illinois",
        "indiana",
        "iowa",
        "kansas",
        "kentucky",
        "louisiana",
        "maine",
        "maryland",
        "massachusetts",
        "michigan",
        "minnesota",
        "mississippi",
        "missouri",
        "montana",
        "nebraska",
        "nevada",
        "new-hampshire",
        "new-jersey",
        "new-mexico",
        "new-york",
        "north-carolina",
        "north-dakota",
        "ohio",
        "oklahoma",
        "oregon",
        "pennsylvania",
        "puerto-rico",
        "rhode-island",
        "south-carolina",
        "south-dakota",
        "tennessee",
        "texas",
        "utah",
        "vermont",
        "virginia",
        "washington",
        "west-virginia",
        "wisconsin",
        "wyoming",
    ]
    url = "https://hamptoninn3.hilton.com/sitemapurl-hp-00000.xml"
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "/accommodations/index.html</loc>" in line and "/en/hotels/" in line:
            state = line.split("/en/hotels/")[1].split("/")[0]
            if state in canada:
                locs.append(line.split("<loc>")[1].split("<")[0] + "|CA")
            if state in usa:
                locs.append(line.split("<loc>")[1].split("<")[0] + "|US")
            if "en/hotels/united-kingdom" in line:
                locs.append(line.split("<loc>")[1].split("<")[0] + "|GB")
    for loc in locs:
        logger.info(loc.split("|")[0])
        country = loc.split("|")[1]
        r2 = session.get(loc.split("|")[0], headers=headers, verify=False, stream=True)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        typ = "<MISSING>"
        website = "hamptoninn.com"
        phone = ""
        purl = loc.split("|")[0]
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        store = ""
        for line2 in lines:
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"url": "https://www.hilton.com/en/hotels/' in line2:
                store = line2.split('"url": "https://www.hilton.com/en/hotels/')[
                    1
                ].split("-")[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"telephone": \'' in line2:
                phone = line2.split('"telephone": \'')[1].split("'")[0].strip()
            if '"name": \'' in line2:
                name = line2.split('"name": \'')[1].split("'")[0].strip()
            if '"streetAddress": \'' in line2:
                add = line2.split('"streetAddress": \'')[1].split("'")[0].strip()
            if '"url": \'' in line2:
                store = line2.split("/index.html")[0].rsplit("-", 1)[1]
            if '"addressLocality": \'' in line2:
                city = line2.split('"addressLocality": \'')[1].split("'")[0].strip()
            if '"addressRegion": \'' in line2:
                state = line2.split('"addressRegion": \'')[1].split("'")[0].strip()
            if '"postalCode": \'' in line2:
                zc = line2.split('"postalCode": \'')[1].split("'")[0].strip()
            if '"latitude": \'' in line2:
                lat = line2.split('"latitude": \'')[1].split("'")[0].strip()
            if '"longitude": \'' in line2:
                lng = line2.split('"longitude": \'')[1].split("'")[0].strip()
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
