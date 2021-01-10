import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt

logger = SgLogSetup().get_logger("hilton_com")

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


@retry(stop=stop_after_attempt(2))
def get_loc(loc):
    session = SgRequests()
    return session.get(loc, headers=headers)


def fetch_data():
    locs = []
    canada = [
        "alberta",
        "british-columbia",
        "manitoba",
        "nova-scotia",
        "nunavut",
        "ontario",
        "quebec",
        "saskatchewan",
        "yukon",
        "prince-edward-island",
        "new-brunswick",
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
        "puerto-rico",
    ]
    url = "https://www3.hilton.com/sitemapurl-hi-00000.xml"
    session = SgRequests()
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            "<loc>https://www3.hilton.com/en/hotels/" in line
            and "accommodations/index.html" in line
        ):
            lurl = line.split("<loc>")[1].split("<")[0]
            locs.append(lurl)
    logger.info(len(locs))
    for loc in locs:
        sname = loc.split("https://www3.hilton.com/en/hotels/")[1].split("/")[0]
        country = ""
        if sname in usa:
            country = "US"
        if sname in canada:
            country = "CA"
        if country == "CA" or country == "US":
            logger.info("Pulling Location %s..." % loc)
            website = "hilton.com"
            typ = "<MISSING>"
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = "<MISSING>"
            phone = ""
            lat = ""
            lng = ""
            try:
                r2 = get_loc(loc)
            except IOError:
                continue
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if '"name": \'' in line2:
                    name = line2.split('"name": \'')[1].split("',")[0]
                if '"homeUrl":"' in line2 and name == "":
                    name = (
                        line2.split('"homeUrl":"')[1]
                        .split(',"name":"')[1]
                        .split('"')[0]
                    )
                if '"latitude": "' in line2:
                    lat = line2.split('"latitude": "')[1].split('"')[0]
                if '"latitude": \'' in line2:
                    lat = line2.split('"latitude": \'')[1].split("',")[0].strip()
                if '"longitude": \'' in line2:
                    lng = line2.split('"longitude": \'')[1].split("',")[0].strip()
                if '"longitude": "' in line2:
                    lng = line2.split('"longitude": "')[1].split('"')[0]
                if '"productID":"' in line2:
                    store = line2.split('"productID":"')[1].split('"')[0]
                if '"streetAddress": "' in line2:
                    add = line2.split('"streetAddress": "')[1].split('"')[0]
                if '"streetAddress": \'' in line2:
                    add = line2.split('"streetAddress": \'')[1].split("',")[0].strip()
                if '"addressLocality": "' in line2:
                    city = line2.split('"addressLocality": "')[1].split('"')[0]
                if '"addressLocality": \'' in line2:
                    city = (
                        line2.split('"addressLocality": \'')[1].split("',")[0].strip()
                    )
                if '"addressRegion": "' in line2:
                    state = line2.split('"addressRegion": "')[1].split('"')[0]
                if '"addressRegion": \'' in line2:
                    state = line2.split('"addressRegion": \'')[1].split("',")[0].strip()
                if '"postalCode": "' in line2:
                    zc = line2.split('"postalCode": "')[1].split('"')[0]
                if '"postalCode": \'' in line2:
                    zc = line2.split('"postalCode": \'')[1].split("',")[0].strip()
                if '"telephone": "' in line2:
                    phone = line2.split('"telephone": "')[1].split('"')[0]
                if '<span class="property-telephone">' in line2 and phone == "":
                    phone = (
                        line2.split('<span class="property-telephone">')[1]
                        .split("<")[0]
                        .strip()
                    )
            hours = "<MISSING>"
            if state == "":
                state = "PR"
            if name != "":
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
